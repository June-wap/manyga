# TECHNICAL DESIGN DOCUMENT (TDD) — LIVEGAME STUDIO

**Phiên bản:** 1.0.0 (GD00 Baseline)  
**Đối tượng:** Codex, Antigravity, Principal/Senior Engineers  

---

## 1. Kiến trúc tiến trình & Runtime (Process & Runtime Topology)

LiveGame Studio vận hành theo mô hình **Local-First Multi-Process Supervised Desktop** trên Windows 11/10 (64-bit):

1. **Desktop Supervisor / UI Process (`apps/desktop`, PySide6):**
   - Khởi tạo cửa sổ quản trị chính, quản lý cấu hình khởi động và kết nối tới Backend qua HTTP/WebSocket loopback (`http://127.0.0.1:<port>`).
   - Có thể quản lý tiến trình con Backend (khi chạy gói cài đặt GD20) hoặc gắn vào Backend đang chạy (dev mode).
   - Tích hợp `QWebEngineView` cho màn hình xem trước nội bộ (World Preview / Broadcast Preview) hoặc mở URL Broadcast sạch cho OBS Browser Source / Window Capture.
2. **Backend Authoritative Server (`apps/backend`, Python 3.11+ / FastAPI / Uvicorn):**
   - Tiến trình duy nhất nắm quyền ghi SQLite (`ADR-014`).
   - Chạy vòng lặp `asyncio` chứa: REST API, WebSocket hubs (`/ws/admin`, `/ws/renderer`), Event Gateway/Bus, Simulation Clock, Active Game Plugin runtime và SQLite Unit-of-Work executor.
3. **Broadcast Frontend Runtime (`frontend/`, TypeScript + Vite + Three.js):**
   - Chạy trong browser engine (OBS Browser Source / Chromium / `QWebEngineView`) ở độ phân giải chuẩn dọc `1080×1920`.
   - Không lưu trạng thái bền vững; khi tải lại hoặc reconnect, gửi yêu cầu `snapshot_request` và dựng lại toàn bộ cảnh từ state authoritative của Backend.

---

## 2. Simulation Clock & Vòng lặp mô phỏng (Deterministic Tick Engine)

Để đảm bảo khả năng kiểm thử xác định (deterministic unit/replay test) và miễn nhiễm với nhảy giờ hệ thống Windows:

- **Clock Abstraction (`core/clock.py`):**
  - `WallClock`: trả về UTC ISO-8601 (`datetime.now(timezone.utc)`) phục vụ `created_at`, `ended_at`, `audit_logs`.
  - `SimulationClock`: dựa trên `time.monotonic()` ở runtime và `ManualFakeClock` trong test.
  - Khi Game Master bấm `PAUSE` hoặc connector mất kết nối quá grace period (`15s`), `SimulationClock` **đóng băng hoàn toàn** (`elapsed_sim_ms` không tăng), do đó mọi cooldown, bộ đếm tu luyện (1s), tick chiến đấu boss (2s), nhịp thiên lôi (4s) và lịch sự kiện đều dừng sạch mà không trôi thời gian.
- **Tách biệt Tick và Frame Rate:**
  - Backend chạy tick logic cố định (ví dụ `1000ms` cho cultivation tick, `2000ms` cho boss tick, sub-tick `200ms` cho timer kiểm tra chuyển trạng thái sự kiện).
  - Frontend Three.js chạy `requestAnimationFrame` độc lập, nội suy chuyển động (`lerp`/`slerp`) giữa các revision từ Backend. Tụt FPS ở Renderer **không làm chậm hay sai lệch** simulation tick ở Backend.

---

## 3. Đồng thời, Giao dịch & Quản lý SQLite (Concurrency & Persistence)

### Cấu hình SQLite bắt buộc (tại mỗi kết nối)
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;
PRAGMA temp_store = MEMORY;
```

### Mô hình thực thi giao dịch (Database-Wide Single Writer — `HIGH-003`)
*(Chỉ thiết kế trong GD00; triển khai thực tế tại `GD02`)*

SQLite khóa **toàn bộ tệp cơ sở dữ liệu** khi ghi (ngay cả ở chế độ `WAL` cũng chỉ cho phép duy nhất **1 write transaction** hoạt động đồng thời). Vì vậy, khóa theo từng `player_id` (per-player lock) **chỉ đủ cho thứ tự logic domain và KHÔNG đủ để ngăn `SQLITE_BUSY` write contention** giữa nhiều người chơi ghi song song.

- **Centralized Write Coordination (Database-Wide Serialization):**
  - Mọi tác vụ ghi vào SQLite bắt buộc đi qua một **Centralized Write Coordinator** (global transaction serializer / bounded write queue `max_write_queue = 512`) đặt trong `Database Manager`.
  - Đảm bảo bất biến: **tối đa 1 write transaction đang mở trên toàn bộ CSDL tại bất kỳ thời điểm nào**. Các tác vụ đọc thuần túy (`read_session()`) chạy song song qua kết nối `WAL` read-only.
- **Unit of Work, Timeouts & Rollback:**
  - Mỗi write job thực thi bên trong một `UnitOfWork` nguyên tử có **`transaction_timeout_ms = 5000`** (song song với `PRAGMA busy_timeout = 5000`).
  - Mọi ngoại lệ hoặc quá hạn `transaction_timeout_ms` bắt buộc **rollback nguyên tử**, nhả ngay khóa write serializer và trả mã lỗi có cấu trúc.
  - Khi **Graceful Shutdown**: đóng cổng nhận write job mới, drain hết các job đã nhận trong giới hạn timeout, chạy `PRAGMA wal_checkpoint(TRUNCATE)` và đóng engine sạch.
- **Optimistic Concurrency Control:** Các bảng tiến trình quan trọng (ví dụ bảng tiến trình của plugin) kết hợp thêm cột `version INTEGER NOT NULL DEFAULT 1` kiểm tra `WHERE profile_id = :id AND version = :expected_version` để phát hiện xung đột logic trước khi commit.
- **Chiến lược Checkpoint:**
  - *Immediate Commit (Atomic):* Nhập môn (`!join`), đổi nghề/ngoại hình, đột phá, giữ/giải phóng XP độ kiếp, dùng vật phẩm (`!heal`), phát thưởng (`reward_ledger`), lưu immutable outcome snapshot, chuyển trạng thái session/event, thao tác GM audit.
  - *Periodic Checkpoint (mỗi 10 giây):* Gom ghi nhận XP tích lũy từ auto-cultivation trong bộ nhớ để giảm IOPS đĩa và kéo dài tuổi thọ SSD, đồng thời xả ngay (flush) khi dừng phiên, pause hoặc có sự kiện đột phá/boss.

---

## 4. Đồng bộ trạng thái Backend → Frontend (Snapshot & Delta Protocol — `HIGH-006`)

Backend là nguồn sự thật duy nhất; Renderer tuyệt đối không quyết định gameplay state. Mọi gói tin trên `/ws/renderer` bắt buộc mang đủ bộ định danh đồng bộ:
- **`stream_epoch`:** UUID/generation ID sinh mới mỗi khi Backend khởi động lại hoặc reset state stream.
- **`session_id`:** Định danh phiên đang hoạt động.
- **`revision` (`uint64`):** Số phiên bản trạng thái tăng đơn điệu trong cùng `(stream_epoch, session_id)`.
- **`snapshot_seq` (`uint64`):** Thứ tự tăng đơn điệu của gói `STATE_SNAPSHOT` trong cùng `stream_epoch`.
- **`request_id`:** Correlation ID gắn khớp giữa `SNAPSHOT_REQUEST` và gói `STATE_SNAPSHOT` phản hồi.

### 4.1 Vòng đời Resync phía Renderer (Resync Lifecycle)
```text
DISCONNECTED → CONNECTING → AWAITING_SNAPSHOT → SYNCED ⇄ RESYNCING → DISCONNECTED
```
1. Khi mới kết nối hoặc reconnect (sau mất mạng hoặc Backend restart), Renderer đặt trạng thái `AWAITING_SNAPSHOT`, bỏ qua mọi `STATE_DELTA` đến sớm và gửi `SNAPSHOT_REQUEST(request_id, reason="initial"|"reconnect")`.
2. Khi nhận `STATE_SNAPSHOT`:
   - **Stale Snapshot Handling:** Bỏ qua nếu cùng `stream_epoch` và `snapshot_seq < last_applied_snapshot_seq` hoặc `revision < last_applied_revision` (nếu `stream_epoch` khác với `current_epoch`, coi là Backend restart → xóa sạch scene state cũ và chấp nhận snapshot mới).
   - Khi hợp lệ: cập nhật `current_epoch`, `current_session_id`, `last_applied_snapshot_seq`, `last_applied_revision = snapshot.revision`, dựng lại scene và chuyển `SYNCED`.
3. Khi đang `SYNCED` và nhận `STATE_DELTA(stream_epoch, session_id, from_revision, to_revision, ops)`:
   - **Quy tắc áp dụng duy nhất:** Chỉ apply delta khi **đồng thời thỏa mãn**: `delta.stream_epoch == current_epoch` **AND** `delta.session_id == current_session_id` **AND** `delta.from_revision == last_applied_revision` **AND** `delta.to_revision > delta.from_revision`.
   - **Epoch / Session Mismatch (Backend restart hoặc đổi phiên):** Xóa cache hiển thị cục bộ, chuyển `RESYNCING` và gửi `SNAPSHOT_REQUEST(reason="epoch_or_session_mismatch")`.
   - **Duplicate Delta (`to_revision <= last_applied_revision` cùng epoch/session):** Bỏ qua an toàn (idempotent no-op).
   - **Overlapping Revision (`from_revision < last_applied_revision < to_revision`):** Từ chối apply cục bộ, chuyển `RESYNCING` và gửi `SNAPSHOT_REQUEST(reason="overlap_detected")`.
   - **Revision Gap (`from_revision > last_applied_revision`):** Không suy đoán hay bỏ bước; chuyển `RESYNCING` và gửi `SNAPSHOT_REQUEST(reason="gap_detected")`.
- **Bảo mật dữ liệu truyền:** Tuyệt đối chỉ serialize DTO dành cho hiển thị (display name đã sanitize/truncate 20 ký tự, realm, vị trí, trạng thái). Không bao giờ đưa `external_user_id` thô nhạy cảm, token hay audit nội bộ vào stream Renderer.

---

## 5. Kiến trúc Thế giới chung 3D, Camera Director & Crowd Rendering

### 5.1 Single WebGLRenderer & Output 9:16
- Chỉ khởi tạo **1 instance `THREE.WebGLRenderer`** cố định tỷ lệ `9:16` (độ phân giải mục tiêu `1080×1920`, cấu hình `pixelRatio` giới hạn tối đa `1.5`–`2.0` để bảo vệ VRAM).
- **Safe Area Overlay:** Cung cấp lớp khung căn chỉnh (Safe Area Guides có thể bật/tắt ở preview) tránh vùng UI TikTok ở cạnh phải và vùng bình luận phía dưới.
- **PiP (Picture-in-Picture):** Tối đa **1 PiP** trong MVP. Kỹ thuật: dùng cùng `WebGLRenderer` gọi `renderer.setScissorTest(true)` + `renderer.setViewport(...)` cho khung phụ bằng `CAM03` (hoặc camera phụ định nghĩa bởi intent), tránh tạo WebGL context thứ 2. Có công tắc tắt PiP ngay từ Game Master Panel khi GPU tải cao.

### 5.2 Phân tách Simulation State vs Rendered State
- Simulation State cho phép `100+` người chơi hoạt động song song (tu luyện, đăng ký boss, chờ kiếp).
- Rendered State áp dụng **Render Budget**:
  - `max_visible_characters` (mặc định cấu hình 100, có thể hạ động xuống 60/40 nếu frame time p95 vượt ngưỡng `33.3ms`).
  - Người chơi vượt quá slot render hoặc đã idle quá `10 phút` vẫn giữ nguyên trạng thái simulation hợp lệ (không bị xóa dữ liệu), chỉ ẩn khỏi scene và vào danh sách chờ hình ảnh.
  - **Không dùng culling để thay đổi luật chơi.**

### 5.3 Chiến lược Crowd Rendering cho SkinnedMesh
- **Ràng buộc kỹ thuật WebGL/Three.js:** `THREE.InstancedMesh` chuẩn chỉ áp dụng cho static/rigid geometry (đèn lồng, cây, trụ đá, bồ đoàn ngồi thiền, hạt VFX), **không tự động hỗ trợ skeletal animation độc lập cho từng `SkinnedMesh`**.
- **Giải pháp phân tầng (kiểm chứng benchmark ở GD09 & GD19):**
  1. **Tái sử dụng tài nguyên:** Dùng chung `BufferGeometry`, `Material`, `Texture` từ `AssetCache`; nhân bản skeleton qua `SkeletonUtils.clone` chỉ cho nhân vật đang hiển thị.
  2. **LOD 3 cấp:**
     - `LOD0` (gần camera / nhân vật nổi bật / boss / đang độ kiếp): `5k–8k` tris, full skeleton + animation mượt.
     - `LOD1` (trung cảnh): `2k–3k` tris, giảm tần suất cập nhật bone (animation throttling 15–20 Hz).
     - `LOD2` (hậu cảnh xa): `0.5k–1k` tris hoặc static/pose mesh đơn giản cho trạng thái ngồi thiền (`meditation`).
  3. **Frustum Culling & Object Pooling:** Tắt update animation matrix cho mesh ngoài camera frustum; pool sẵn toàn bộ VFX particles và DOM/Canvas nameplates (chỉ hiện tối đa N nameplate gần camera hoặc nhân vật được `!find`).
  4. **Resource Cleanup bắt buộc:** Khi đổi game, reload asset hoặc đóng ứng dụng, giải phóng đầy đủ `geometry.dispose()`, `material.dispose()`, `texture.dispose()`, `renderTarget.dispose()`, hủy `requestAnimationFrame` và đóng WebSocket để chống rò rỉ VRAM/RAM trên các phiên live kéo dài nhiều giờ.

### 5.4 Camera Director & Tách biệt 3 Hàng chờ (`MEDIUM-002`)
Để tránh nghẽn gameplay khi có nhiều sự kiện cá nhân cùng lúc (ví dụ 20 yêu cầu Tiểu Thiên Kiếp), hệ thống tách biệt tuyệt đối **3 hàng chờ độc lập**:
1. **Gameplay Execution Queue** (bền vững ở tầng Plugin/DB, ví dụ FIFO hàng chờ độ kiếp): quyết định thứ tự thực thi nghiệp vụ và giữ tài nguyên.
2. **Camera Focus Queue** (`Camera Director`, ephemeral): quyết định góc máy hiển thị — **không bắt buộc mọi sự kiện cá nhân phải được chiếu bằng camera chính** (có thể chiếu qua PiP tùy chọn hoặc để nền nếu camera chính đang ưu tiên cao hơn).
3. **Event Presentation Queue** (`Overlay Engine`, ephemeral có TTL): quản lý thẻ thông tin, toast gộp và feed hiển thị.

- Quản lý 5 camera ảo (`CAM01`..`CAM05`) trên một mảng cấu hình định nghĩa bởi Map/Plugin.
- **Thuật toán chọn shot:**
  - Nhận `CameraIntent(camera_id, target_entity_id, priority, duration_ms, ttl_ms)`.
  - Nếu đang có shot chạy chưa đủ `min_hold_ms = 5000ms`, chỉ cho phép cắt ngang khi `incoming.priority > current.priority` (ví dụ `Boss 90` hoặc `Tribulation 80` cắt ngang `Idle 10` hoặc `!find 30`).
  - Không bao giờ cho phép `!find` (`priority=30`) cắt ngang `Boss` (`90`) hoặc `Tribulation` (`80`).
  - Chuyển đổi vị trí & lookAt mượt trong `600ms` (smoothstep / damped interpolation).
  - Chế độ Manual Override từ Game Master có `auto_return_ms = 20000ms` (có thể khóa thủ công nếu GM chọn rõ).

---

## 6. Phục hồi sau sự cố & Tắt ứng dụng an toàn (Crash Recovery & Graceful Shutdown — `HIGH-005`)

### 6.1 Phân tách Trách nhiệm Recovery (Platform Core vs Game Plugin)
- **Platform Recovery Core (`Game Session Manager`) tuyệt đối không hardcode logic gameplay hay tên bảng của Tu Tiên Online (`g_cultivation_*`).**
- Khi khởi động lại sau crash, Platform thực hiện đúng 2 bước trong transaction tuần tự qua SQLite Write Coordinator:
  1. **Platform Level:** Quét các `game_sessions` ở trạng thái chưa kết thúc (`RUNNING`, `PAUSED`, `PAUSED_ERROR`, `STOPPING`) → chuyển sang `INTERRUPTED_RECOVERED` (cho phép GM chọn mở phiên mới, không reset tiến trình người chơi) và đánh dấu các `scheduled_events` chưa kết thúc cần ủy thác xử lý.
  2. **Plugin Level Delegation:** Với từng `plugin_id` có phiên/event gián đoạn, Platform gọi `plugin.recover_after_crash(uow, RecoveryContext(session_id, reward_ledger))`. Chính Plugin tự xử lý bảng domain riêng (hoàn tài nguyên đang giữ, xử lý outcome snapshot, trả thưởng idempotent qua `RewardLedger`).

### 6.2 Ma trận Phục hồi Trạng thái Sự kiện (Event Crash Recovery Matrix)
Quy tắc **Immutable Outcome Snapshot Transaction**: Trước khi bất kỳ sự kiện có thưởng nào bước vào pha phát thưởng (`REWARDING`), hệ thống bắt buộc commit một **`outcome_snapshot_json` bất biến** kèm cờ `outcome_committed = 1` (chứa kết quả cuối, danh sách người đủ điều kiện và danh sách phần thưởng xác định) trong **1 SQLite transaction nguyên tử**.

| Trạng thái lúc Crash | `outcome_committed` | Hành động Recovery bắt buộc | Chính sách Thưởng & Tài nguyên giữ |
|---|---|---|---|
| `SCHEDULED` | `0` | Chuyển `CANCELED_RECOVERY` (hoặc hủy lịch phiên cũ) | Không phát thưởng; không có tài nguyên giữ |
| `ANNOUNCING` / `REGISTRATION` / `PREPARING` / `ACTIVE` | `0` | Chuyển `CANCELED_RECOVERY`; gọi plugin refund handler | Không phát thưởng mới; hoàn trả **100%** tài nguyên/XP đang giữ (không phạt) |
| `RESOLVING` *(pre-commit)* | `0` | Outcome chưa commit → coi như chưa phân định; chuyển `CANCELED_RECOVERY` + gọi plugin refund handler | Không phát thưởng; hoàn trả **100%** tài nguyên/XP đang giữ |
| `RESOLVING` *(post-commit)* | `1` | Outcome bất biến đã commit → chuyển tiếp sang `REWARDING` và chạy payout idempotent | Chạy `RewardLedger.grant_idempotent()` theo `outcome_snapshot_json` → `COMPLETED` |
| `REWARDING` | `1` | Tiếp tục phát thưởng idempotent từ `outcome_snapshot_json` đã lưu → hoàn tất chuyển `COMPLETED` | Khóa duy nhất `(event_id, player_id, reward_kind)` ngăn phát trùng 100%; giữ nguyên các bản ghi đã commit |
| `COMPLETED` | `1` | Terminal state — **No-op** (không chạy lại) | Bảo toàn nguyên vẹn lịch sử và sổ cái |
| `CANCELED` / `CANCELED_RECOVERY` | `0` | Terminal state — **No-op** (xác minh không còn tài nguyên bị kẹt) | Không phát thưởng; không phạt lại |
| `FAILED` | `0` hoặc `1` | Terminal state — **No-op** (nếu đã có outcome thất bại hợp lệ và chưa phát thưởng an ủi trong `REWARDING`, xử lý theo nhánh `REWARDING` trên; đã chốt kết thúc thì không chạy lại) | Không phát thưởng trùng |

- Sau khi recovery xong, mọi thực thể nhân vật trong phiên cũ được đặt về trạng thái nghỉ `OFFLINE/IDLE` (không cộng tu vi bù cho khoảng thời gian server tắt).

### 6.3 Quy trình tắt ứng dụng sạch (Graceful Shutdown)
Khi nhận `SIGINT`/`SIGTERM` hoặc nút thoát từ Desktop UI:
1. Ngừng tiếp nhận sự kiện mới từ Event Gateway và đóng cổng nhận write job mới.
2. Đóng băng `SimulationClock`, gọi `plugin.on_session_stop()` để hủy an toàn các event chưa kết thúc theo luật refund.
3. Flush toàn bộ checkpoint còn lại và ghi nhận `session.state = 'COMPLETED'`, `session.ended_at` + `audit_logs`.
4. Đóng toàn bộ WebSocket clients, drain write queue, chạy `PRAGMA wal_checkpoint(TRUNCATE)` và giải phóng SQLAlchemy engine/connection pool.
5. Đảm bảo không còn orphan subprocess (Uvicorn/Vite/Qt WebEngine) tồn tại sau khi thoát.

---

## 7. Khả năng quan sát, Xử lý lỗi & Mục tiêu Kiểm thử Hiệu năng (Observability, Error Handling & Performance Targets)

### 7.1 Mục tiêu Benchmark MVP (Subject to Verification — Chưa phải kết quả đo thực tế)
Toàn bộ các chỉ tiêu sau là **mục tiêu kiểm thử tại GD19**, chưa được triển khai đo hoặc khẳng định đã đạt trong GD00:
- **Broadcast Output:** `1080×1920` (9:16), mục tiêu **`30 FPS`** ổn định (`60 FPS` mục tiêu nâng cao) khi capture cùng OBS.
- **Tải người chơi:** **`100` concurrent active players** (tách simulation state với render budget/LOD).
- **Kiến trúc đồ họa:** **Single `WebGLRenderer`**, tối đa **1 PiP** (render qua scissor/viewport trên cùng renderer, tắt được).
- **Chiến lược tối ưu:** **LOD 3 cấp** (`5–8k / 2–3k / 0.5–1k` tris mục tiêu), frustum culling, animation throttling, object pooling VFX/nameplate.
- **Resource Disposal:** Giải phóng triệt để geometry, material, texture, renderTarget, animation mixer, timer và WebSocket khi despawn/reload/shutdown.
- **4-Hour Continuous Session Test:** Phiên chạy liên tục **4 giờ** dưới tải giả lập thực tế không crash, không tăng trưởng RAM/VRAM bất thường và không rò rỉ handle.
- **Resource Monitoring:** Giám sát liên tục **CPU, RAM, GPU utilization và GPU VRAM (Total vs Used/Free)** song song với p50/p95 frame time, draw calls và event queue depth.

### 7.2 Observability & Error Isolation

- **Structured Logging (JSON lines + Console human-readable):** Mỗi log mang `timestamp_utc`, `level`, `module`, `session_id`, `event_id`, `correlation_id`, `message`. Bộ lọc tự động redact các trường khớp `token`, `secret`, `password`, `authorization`, `cookie`, `api_key`.
- **Error Isolation cho Plugin:** Mọi lời gọi vào `GamePlugin.handle_event()` hoặc `tick()` được bọc `try/except` tại `Game Session Manager`. Lỗi cục bộ trên 1 lệnh người chơi trả mã lỗi có cấu trúc và ghi log cho GM, không làm sập toàn bộ vòng lặp Backend; nếu lỗi nghiêm trọng tái diễn vượt ngưỡng (circuit breaker), tự động chuyển phiên sang `PAUSED_ERROR` và báo động trên Game Master Panel.
- **Health & Metrics Endpoint:** `/api/v1/health` và `/api/v1/metrics` cung cấp trạng thái DB, active plugin, queue depth, event processing latency p50/p95, WS client count để Desktop UI hiển thị trạng thái thực theo thời gian thực.
