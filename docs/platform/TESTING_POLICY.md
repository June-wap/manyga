# TESTING POLICY — LIVEGAME STUDIO

**Phiên bản:** 1.0.0 (GD00 Baseline)  
**Nguyên tắc tối thượng:** Trung thực tuyệt đối — **không bao giờ báo cáo test chưa chạy là `PASS`**; kiểm thử hành vi thật, không chỉ kiểm tra mock calls.

---

## 1. Phân loại trạng thái kiểm thử bắt buộc (5 Status Labels)

Mọi báo cáo bàn giao (`GDxx_DELIVERY_REPORT.md`) và báo cáo review (`GDxx_ANTIGRAVITY_REVIEW.md`) phải phân loại rõ từng hạng mục kiểm thử:

| Trạng thái | Định nghĩa chính xác |
|---|---|
| `PASS` | Đã thực thi thực tế trong môi trường hiện tại và đạt toàn bộ assertion/tiêu chí |
| `FAIL` | Đã thực thi thực tế và có ít nhất một assertion/tiêu chí thất bại |
| `SKIP` | Chủ động bỏ qua có điều kiện hợp lệ (bắt buộc ghi rõ nguyên nhân kỹ thuật) |
| `NOT RUN` | Chưa chạy trong phiên bàn giao/review này |
| `BLOCKED` | Không thể chạy do thiếu điều kiện tiên quyết bên ngoài (ví dụ: chưa có Authorized TikTok Provider ở GD17) |

---

## 2. Tháp kiểm thử (Test Pyramid & Directories)

```text
tests/
├── unit/           # Domain logic thuần Python (công thức XP, cảnh giới, boss, kiếp, parser, cooldown)
├── integration/    # SQLite thật (temp file, WAL+FK ON), FastAPI TestClient, Alembic migration, persistence qua restart
├── contracts/      # GamePlugin Contract (test với >=2 plugins), Asset Validator, API & Event Schema
├── replay/         # Event Simulator deterministic replay, idempotency, crash recovery
├── ui/             # PySide6 Desktop UI smoke/widget tests (không freeze, không overlap, backend-offline state)
├── frontend/       # TypeScript typecheck, Vite build, Three.js scene/camera/disposal tests
├── security/       # Path traversal, loopback bind, HTML/XSS escape, secret redaction, plugin allowlist
└── perf/           # Burst 100 lệnh/s trong 30s; Benchmark 1/20/50/100 nhân vật + OBS (GD19)
```

---

## 3. Quy tắc chất lượng Test (Anti-Fake-Test Standards)

1. **Kiểm thử hành vi thật (Real Behavior Verification):**
   - Integration tests phải chạy trên tệp **SQLite thật** (bật `PRAGMA foreign_keys=ON`), kiểm tra đọc lại sau khi đóng/mở kết nối mới (persistence across restart).
   - Cấm viết test chỉ `assert mock.called_once()` mà không kiểm tra dữ liệu đầu ra hoặc trạng thái CSDL.
2. **Deterministic Clock Injection:**
   - Mọi test liên quan cooldown, auto-cultivation tick, Boss combat tick, Tribulation strikes và grace period phải inject `ManualFakeClock` — **không dùng `time.sleep()` dài** gây test chậm và flaky.
3. **Không sửa test để che lỗi:**
   - Khi test phát hiện bug ở code nguồn, phải sửa code nguồn hoặc báo cáo `FAIL`; cấm nới lỏng assertion để đạt `PASS` giả.
4. **Phân tách Simulator vs Live:**
   - Simulator `PASS` **không đồng nghĩa** Live TikTok `PASS`. Các tiêu chí gắn với kết nối TikTok thật (`AC18`) chỉ được phép đánh `PASS` sau khi chạy Authorized Live Smoke Test tại `GD17`.
5. **Trung thực về Benchmark hiệu năng & Mục tiêu Kiểm thử MVP (GD19):**
   - Toàn bộ các chỉ tiêu sau là **mục tiêu kiểm thử (benchmark targets)**, **không phải kết quả đã đạt** và không chạy runtime benchmark trong GD00:
     - Độ phân giải phát sóng `1080×1920`, mục tiêu `30 FPS` (`60 FPS` nâng cao), mục tiêu `100` concurrent active players.
     - Single `WebGLRenderer`, tối đa `1` PiP (tắt được), áp dụng chiến lược `LOD` và `Resource Disposal` không rò rỉ.
     - Bài kiểm thử bền bỉ liên tục **4 giờ (4-hour continuous session test)** kèm giám sát liên tục **CPU, RAM, GPU và VRAM**.
   - Mọi báo cáo hiệu năng (`AC15`) bắt buộc ghi đủ: cấu hình CPU/RAM/GPU/VRAM (phân biệt Tổng VRAM và VRAM khả dụng), độ phân giải (`1080×1920`), có bật OBS capture hay không, số nhân vật (`1/20/50/100`), p50/p95 frame time, draw calls và queue depth. Không suy đoán hay bịa FPS.

---

## 4. Ma trận Ánh xạ Tiêu chí Nghiệm thu GAME001 (AC01–AC18)

*(Đối chiếu trực tiếp với `docs/games/cultivation_online/GDD.md` v0.1.1 Mục 19 và Amendment v0.1.1)*

| AC ID | Kịch bản bắt buộc | Loại test | Giai đoạn nghiệm thu |
|---|---|---|---|
| `AC01` | 20 người `!join` cùng lúc không duplicate | Integration / Concurrency | `GD11` |
| `AC02` | Rejoin sau restart giữ cảnh giới, XP, nghề, inventory | Integration / Restart | `GD11` |
| `AC03` | Tu luyện 10 tick (+20 XP); PAUSE không cộng | Unit + Integration | `GD11` |
| `AC04` | Đột phá đủ/thiếu XP, transaction nguyên tử | Unit + Integration | `GD14` |
| `AC05` | 20 người yêu cầu kiếp: FIFO, không giữ XP 2 lần, không chồng Boss; tách 3 hàng chờ (Execution/Camera/Presentation) & đo **queue waiting time** | Integration / Perf | `GD14` |
| `AC06` | Kiếp thất bại/hủy/restart (penalty/refund đúng) & bộ lệnh `!hothe`, `!hotheauto`, `!hotheauto on/off` (mặc định bật, server-side timing, GM cấu hình mặc định, gift không ảnh hưởng xác suất) | Integration / Crash | `GD14` |
| `AC07` | Boss thắng / thua / hết giờ: kết thúc xác định, thưởng đúng + chạy **Combat Balance Simulator** (`1/5/10/20/50/100` người, đa cảnh giới/nghề, auto/skill/mixed/retaliation) | Unit + Integration + Sim | `GD13` |
| `AC08` | Replay event & crash recovery trên toàn bộ trạng thái (`ACTIVE`/`RESOLVING` pre & post-commit immutable outcome/`REWARDING`/`COMPLETED`/`CANCELED`/`FAILED`): không cấp thưởng trùng, không mất `xp_reserved` | Replay / Crash | `GD12`, `GD13`, `GD14` |
| `AC09` | Lệnh sai / spam burst `100/s` (30s): không crash, cooldown đúng, queue đầy `100%` trả `INGESTION_QUEUE_FULL` (không silent drop gameplay, không block Gateway) | Replay / Perf | `GD04`, `GD06`, `GD19` |
| `AC10` | `!info`/`!find` trong lúc đánh Boss không cắt camera Boss, TTL đúng | Unit + Integration | `GD10`, `GD16` |
| `AC11` | Renderer disconnect/reconnect, Backend restart (đổi `stream_epoch`), stale snapshot, duplicate/overlapping/gap delta → resync snapshot đúng, không reset gameplay | Frontend + Integration | `GD08` |
| `AC12` | Mất nguồn sự kiện: pause sau grace period 15s, resume có kiểm soát | Integration | `GD04`, `GD17` |
| `AC13` | Game Master Pause/Stop: clock đóng băng, lưu dữ liệu, không orphan process | UI + Integration | `GD03`, `GD12`, `GD18` |
| `AC14` | Nạp GLB thật / placeholder đúng version; kiểm thử 2 chế độ `DEVELOPMENT` (fallback + cảnh báo) vs `PRODUCTION` (chặn thiếu required asset / placeholder chưa duyệt) | Contract + Frontend | `GD07`, `GD09`, `GD18` |
| `AC15` | Benchmark mục tiêu `1080×1920`, `30 FPS`, `100` concurrent active players, single `WebGLRenderer`, tối đa `1` PiP, LOD, resource disposal, **phiên chạy liên tục 4 giờ** kèm giám sát **CPU/RAM/GPU/VRAM** và OBS (báo số đo thật + cấu hình) | Perf / Benchmark / Soak | `GD19` |
| `AC16` | Gift gửi lặp: chỉ cosmetic, không đổi XP/HP/ATK, dedupe | Unit + Security | `GD06`, `GD16` |
| `AC17` | Output dọc `1080×1920` dễ đọc, không bị che bởi UI TikTok | UI / Visual E2E | `GD08`, `GD18` |
| `AC18` | TikTok LIVE Authorized Smoke Test (ghi rõ quyền & hạn chế) | Live Gate E2E | `GD17` |

---

## 4.5 Tiêu chí Nghiệm thu Bảo mật theo từng Giai đoạn (Phased Security Acceptance Criteria — `HIGH-004`)

| Giai đoạn | Kiểm thử Bảo mật Bắt buộc (`PASS` gate) |
|---|---|
| **`GD01`** | Bind mặc định `127.0.0.1` (không `0.0.0.0`); `TrustedHostMiddleware` chặn `Host` lạ; không có wildcard CORS `*`; `/api/v1/health` công khai cục bộ không lộ secret/path; khung privileged endpoint chặn request thiếu/sai Admin Token (`401/403`); structured logs redact toàn bộ secrets. |
| **`GD02`** | Toàn bộ REST CRUD `/settings`, `/sessions`, `/players` yêu cầu `ADMIN_SESSION_TOKEN`; SQLite centralized write serializer không rò rỉ dữ liệu hay để mở đường dẫn DB tùy ý; secrets trong `application_settings` luôn trả `"***"`. |
| **`GD03`** | `/ws/admin` xác thực `ADMIN_SESSION_TOKEN` + kiểm tra `Origin` (đóng mã `1008` nếu sai); Desktop UI không ghi token ra logs/UI copyable text. |
| **`GD05`** | `Game Plugin Manager` chỉ nạp plugin có trong **static trusted allowlist** (từ chối module ngoài allowlist kể cả nằm trong thư mục `games/`). |
| **`GD07`** | `Asset Validator` & `Asset Library` chặn 100% path traversal (`../`, absolute path, UNC, symlink, tệp thực thi `.exe`/`.py`), không expose arbitrary host paths qua API. |
| **`GD08`** | `/ws/renderer` xác thực `RENDERER_STREAM_TOKEN` (chỉ đọc) + `Origin`; mọi thông điệp cố đột biến gameplay từ Renderer bị từ chối; Broadcast URL tuyệt đối không chứa `ADMIN_SESSION_TOKEN`; XSS escape 100% trên mọi nameplate/overlay. |
| **`GD17`** | Authorized TikTok Connector không dùng scraping/cookie trái phép; credential bảo vệ qua `SecretStr`/OS storage và không bao giờ xuất hiện trong logs/audit. |

---

## 5. Cổng chất lượng trước khi chuyển giai đoạn (Phase Gate Policy)

Một giai đoạn `GDxx` chỉ được đề xuất chuyển tiếp sang `GD(xx+1)` khi:
1. Toàn bộ lỗi `CRITICAL` và `HIGH` ảnh hưởng acceptance criteria đã được xử lý và kiểm chứng lại.
2. Toàn bộ test trong phạm vi giai đoạn đã chạy thực tế (không để `NOT RUN` mà không có lý do `BLOCKED` chính đáng).
3. Regression suite của các giai đoạn trước vẫn `PASS`.
4. Có đủ `docs/GDxx_DELIVERY_REPORT.md` và review độc lập từ Antigravity.
