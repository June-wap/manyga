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

### Mô hình thực thi giao dịch
- **Single Writer Discipline:** Mọi tác vụ ghi vào SQLite đi qua một lớp `UnitOfWork` (SQLAlchemy 2.x) với serialization hợp lý theo `player_id` hoặc hàng đợi ghi tập trung ở tầng Application Service để triệt tiêu `SQLITE_BUSY` khi burst `100 lệnh/giây`.
- **Optimistic Concurrency Control:** Các bảng tiến trình quan trọng (`g_cultivation_progress`) có cột `version INTEGER NOT NULL DEFAULT 1`. Cập nhật kiểm tra `WHERE profile_id = :id AND version = :expected_version` và tăng `version + 1`.
- **Chiến lược Checkpoint:**
  - *Immediate Commit (Atomic):* Nhập môn (`!join`), đổi nghề/ngoại hình, đột phá, giữ/giải phóng XP độ kiếp, dùng vật phẩm (`!heal`), phát thưởng (`reward_ledger`), chuyển trạng thái session/event, thao tác GM audit.
  - *Periodic Checkpoint (mỗi 10 giây):* Gom ghi nhận XP tích lũy từ auto-cultivation trong bộ nhớ để giảm IOPS đĩa và kéo dài tuổi thọ SSD, đồng thời xả ngay (flush) khi dừng phiên, pause hoặc có sự kiện đột phá/boss.

---

## 4. Đồng bộ trạng thái Backend → Frontend (Snapshot & Delta Protocol)

- Backend duy trì một bộ đếm `state_revision: uint64` tăng đơn điệu cho từng phiên live.
- **Luồng kết nối mới / Reconnect:**
  1. Renderer mở WebSocket `/ws/renderer?session_id=<id>`.
  2. Backend gửi gói `STATE_SNAPSHOT` đầy đủ chứa: `revision`, `session_state`, `world_config`, danh sách `entities` đang hoạt động, `active_event`, `camera_state`, `overlay_queue`, `asset_bindings`.
  3. Các thay đổi tiếp theo gửi dưới dạng `STATE_DELTA` (`from_revision`, `to_revision`, danh sách ops: `entity_upsert`, `entity_remove`, `event_update`, `camera_intent`, `overlay_push`, `vfx_trigger`, `audio_trigger`).
- **Xử lý mất gói / Lệch Revision:**
  - Nếu Renderer nhận delta có `to_revision <= last_applied_revision`: **bỏ qua (idempotent)**.
  - Nếu `from_revision > last_applied_revision`: phát hiện gap → Renderer tự gửi `SNAPSHOT_REQUEST` để đồng bộ lại toàn bộ trạng thái mà không reset gameplay ở Backend.
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

### 5.4 Camera Director State Machine
- Quản lý 5 camera ảo (`CAM01`..`CAM05`) trên một mảng cấu hình định nghĩa bởi Map/Plugin.
- **Thuật toán chọn shot:**
  - Nhận `CameraIntent(camera_id, target_entity_id, priority, duration_ms, ttl_ms)`.
  - Nếu đang có shot chạy chưa đủ `min_hold_ms = 5000ms`, chỉ cho phép cắt ngang khi `incoming.priority > current.priority` (ví dụ `Boss 90` hoặc `Tribulation 80` cắt ngang `Idle 10` hoặc `!find 30`).
  - Không bao giờ cho phép `!find` (`priority=30`) cắt ngang `Boss` (`90`) hoặc `Tribulation` (`80`).
  - Chuyển đổi vị trí & lookAt mượt trong `600ms` (smoothstep / damped interpolation).
  - Chế độ Manual Override từ Game Master có `auto_return_ms = 20000ms` (có thể khóa thủ công nếu GM chọn rõ).

---

## 6. Phục hồi sau sự cố & Tắt ứng dụng an toàn (Crash Recovery & Graceful Shutdown)

### 6.1 Khởi động lại sau Crash (Startup Recovery Routine)
Khi Backend khởi động và mở SQLite:
1. Kiểm tra các `game_sessions` có trạng thái `RUNNING` hoặc `PAUSING` chưa đóng: chuyển sang `INTERRUPTED_RECOVERED` (cho phép GM chọn resume phiên hoặc mở phiên mới, không reset tiến trình người chơi).
2. Kiểm tra các event đang dở dang (`ANNOUNCING`, `REGISTRATION`, `PREPARING`, `ACTIVE`):
   - Chuyển trạng thái sang `CANCELED_RECOVERY`.
   - Giải phóng toàn bộ `xp_reserved` đang giữ trong `g_cultivation_tribulation_queue` và `g_cultivation_progress` trong cùng transaction (không phạt người chơi vì lỗi hệ thống).
   - Không phát thưởng mới cho event chưa tới bước `REWARDING`.
3. Kiểm tra các event dừng ở trạng thái `REWARDING`:
   - Tiếp tục phát thưởng idempotent dựa trên `outcome_snapshot` đã lưu và khóa duy nhất `(event_id, player_id, reward_kind)` trong `reward_ledger`; hoàn tất chuyển `COMPLETED`.
4. Đặt trạng thái runtime của mọi nhân vật về `OFFLINE/IDLE` (không cộng tu vi bù cho khoảng thời gian server tắt).

### 6.2 Quy trình tắt ứng dụng sạch (Graceful Shutdown)
Khi nhận `SIGINT`/`SIGTERM` hoặc nút thoát từ Desktop UI:
1. Ngừng tiếp nhận sự kiện mới từ Event Gateway.
2. Đóng băng Simulation Clock, hủy an toàn các event chưa kết thúc theo luật refund.
3. Flush toàn bộ XP checkpoint và ghi nhận `session.ended_at` + `audit_logs`.
4. Đóng toàn bộ WebSocket clients, giải phóng SQLAlchemy engine/connection pool (`PRAGMA wal_checkpoint(TRUNCATE)`).
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
