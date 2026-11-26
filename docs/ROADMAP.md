# DEVELOPMENT ROADMAP — LIVEGAME STUDIO

**Phiên bản:** 1.0.0 (GD00 Baseline)  
**Chiến lược:** Vertical Slice Development — phát triển Platform (`GD00`–`GD20`) song hành kiểm chứng trực tiếp qua `GAME001` (Tu Tiên Online, `TT-GD01`–`TT-GD08`), tách độc lập luồng sản xuất mỹ thuật (`TT-AS01`–`TT-AS09`).

---

## 1. Bảng ánh xạ Lộ trình Platform (`GD00`–`GD20`) với Game Track (`TT-GD01`–`TT-GD08`)

| Track GAME001 (GDD Mục 20) | Nội dung chính | Ánh xạ vào Giai đoạn Platform |
|---|---|---|
| `TT-GD01` | Plugin skeleton, config schema, domain model, simulator onboarding | `GD05`, `GD06` |
| `TT-GD02` | Player progression, persistence, cultivation, commands | `GD11` |
| `TT-GD03` | Shared scene, map anchors, animation, camera, overlay | `GD08`, `GD09`, `GD10` |
| `TT-GD04` | Scheduler, Game Master, queue và lifecycle | `GD12` |
| `TT-GD05` | Boss combat, profession skills, reward ledger | `GD13`, `GD15` |
| `TT-GD06` | Breakthrough, tribulation, recovery | `GD14` |
| `TT-GD07` | Full simulation, import production assets, balancing | `GD07`, `GD16`, `GD18` |
| `TT-GD08` | Authorized live connector, OBS, E2E, benchmark | `GD17`, `GD18`, `GD19`, `GD20` |

---

## 2. Chi tiết 21 Giai đoạn Phát triển (`GD00` – `GD20`)

### GD00 – Project Design & Initialization
- **Objective:** Khởi tạo workspace chính thức `D:\Tiktok Mini Game`, Git branch `design/gd00`, cấu trúc thư mục và bộ tài liệu kiến trúc/hợp đồng đầy đủ làm nguồn sự thật trước khi viết code.
- **Scope:** Thiết kế 37 module, CSDL + ERD, Game Plugin/Asset/API/Event Contracts, UI Guidelines, Testing Policy, TikTok Feasibility, Roadmap, đối chiếu GDD GAME001, báo cáo môi trường.
- **Dependencies:** Không.
- **Deliverables:** 21 tài liệu chuẩn, `.gitignore`, khung thư mục gốc, `docs/GD00_DELIVERY_REPORT.md`.
- **Acceptance criteria:** Toàn bộ tài liệu nhất quán, ranh giới kiến trúc rõ ràng, GDD được kiểm tra trung thực, không viết code runtime GD01.
- **Test requirements:** Cross-check liên kết tài liệu, kiểm tra bảng/schema/contract không xung đột, `git status` sạch không chứa file rác/secret.
- **Out-of-scope requirements:** Không triển khai GD01, không chạy migration DB, không tạo production asset, không tích hợp TikTok thật.

### GD01 – Platform Foundation
- **Objective:** Dựng bộ khung chạy được đầu tiên cho Backend FastAPI, Desktop Shell PySide6 và Frontend TypeScript/Vite/Three.js 9:16.
- **Scope:** Khởi tạo `.venv` Python + `pyproject.toml`, `core/` (Application Core, Config Manager cơ bản, Logging System với redaction, SQLite smoke), FastAPI `/api/v1/health` bind `127.0.0.1`, PySide6 Main Window Dark/Purple (Dashboard, Game Library, Asset Library, Settings + Backend Unavailable state), Vite + Three.js scene 9:16 với cleanup chuẩn.
- **Dependencies:** `GD00`.
- **Deliverables:** Code chạy cục bộ 3 lớp, script khởi chạy dev, unit/smoke tests, `docs/GD01_DELIVERY_REPORT.md`.
- **Acceptance criteria:** Backend chỉ bind loopback; Desktop UI mở mượt không freeze, xử lý đúng trạng thái mất Backend và thoát sạch không orphan process; Three.js build sạch không lỗi console, render 9:16 và resize đúng.
- **Test requirements:** `pytest` backend health/config/logging; `tsc --noEmit` + `vite build`; UI smoke test thực tế.
- **Out-of-scope requirements:** Không Meshy/Tripo/AI Asset Generator, không TikTok thật, không gameplay production GAME001, không cloud/payment.

### GD02 – Database & Application Services
- **Objective:** Thiết lập hệ thống CSDL SQLite (WAL + FK ON), Alembic migrations cho bảng Platform và lớp Application Services + Repository pattern.
- **Scope:** `Database Manager`, Alembic (`render_as_batch=True`), 14 bảng Platform (tối thiểu `application_settings`, `game_plugins`, `game_sessions`, `players`, `external_identities`, `player_game_profiles`, `audit_logs`), `Application Services`, `Player Persistence` cơ bản.
- **Dependencies:** `GD01`.
- **Deliverables:** Migration scripts đầu tiên, SQLAlchemy models, Repositories, REST CRUD sessions/players/settings.
- **Acceptance criteria:** Dữ liệu bền vững qua restart thực tế; FK và unique constraints hoạt động; rollback nguyên tử khi lỗi; không lộ secret khi đọc settings.
- **Test requirements:** Integration tests trên tệp SQLite thật (upgrade/downgrade Alembic, persistence qua restart, duplicate/invalid request, FK violation).
- **Out-of-scope requirements:** Không tạo bảng gameplay riêng của GAME001, không tích hợp TikTok thật.

### GD03 – Desktop Shell & Game Master UI
- **Objective:** Hoàn thiện khung điều hướng 14 màn hình Desktop PySide6 và nền tảng Game Master UI (chưa nối gameplay production).
- **Scope:** Sidebar 4 nhóm, Dark/Purple design tokens, trạng thái Empty/Loading/Error/Backend Offline nhất quán, WebSocket `/ws/admin`, nút Emergency Pause/Stop với hộp thoại xác nhận, khung Game Panel Extension Slot.
- **Dependencies:** `GD01`, `GD02`.
- **Deliverables:** Desktop Shell đầy đủ khung 14 màn hình (màn hình chưa có backend đánh dấu rõ `Sắp ra mắt`), audit log viewer cơ bản.
- **Acceptance criteria:** Không có nút giả mạo đang hoạt động; responsive ở `1280×800` và `1920×1080`; Tiếng Việt UTF-8 hiển thị chuẩn không overlap; shutdown sạch.
- **Test requirements:** PySide6 widget/smoke tests, manual & automated visual check resize và backend disconnect/reconnect.
- **Out-of-scope requirements:** Không xây 3D game logic trong PySide6; không truy cập trực tiếp SQLite từ Desktop UI.

### GD04 – Event Gateway & Simulator
- **Objective:** Xây dựng đường ống tiếp nhận sự kiện chuẩn hóa, chống trùng lặp, hàng đợi có backpressure và Event Simulator phục vụ phát triển/kiểm thử.
- **Scope:** `Event Gateway`, `Event Bus`, `Event Simulator` (REST + UI), `ConnectorAdapter` interface + `MockEventProvider`, bảng `event_ingestions` và `processed_events`, grace period `15s` khi giả lập disconnect.
- **Dependencies:** `GD02`, `GD03`.
- **Deliverables:** Normalized Event pipeline, JSONL replay runner, burst generator `100 events/s`, Simulator UI screen.
- **Acceptance criteria:** Chống trùng theo `(source_namespace, source_event_id)`; chịu tải burst `100 lệnh/s` trong 30s không crash/mất lệnh hợp lệ; giả lập disconnect quá 15s tự kích hoạt pause (AC12).
- **Test requirements:** Unit + integration dedupe, ordering, backpressure, replay determinism và burst 30s test.
- **Out-of-scope requirements:** Không kết nối TikTok thật.

### GD05 – Game Plugin Engine *(gắn `TT-GD01` phần 1)*
- **Objective:** Triển khai `Game Registry`, `Game Plugin Manager`, `Game Session Manager` và xác minh khả năng chạy đa game qua plugin skeleton.
- **Scope:** Manifest loader + allowlist trusted built-in plugins (`games/`), `SimulationClock` (monotonic + injectable), vòng đời plugin, error isolation/circuit breaker, skeleton `games/cultivation_online/` (`GAME001`) và 1 dummy plugin kiểm thử thứ 2.
- **Dependencies:** `GD02`, `GD04`.
- **Deliverables:** Plugin engine hoàn chỉnh, `games/cultivation_online/manifest.json` + skeleton, REST `/api/v1/games` và `/api/v1/sessions` lifecycle.
- **Acceptance criteria:** Đăng ký và chạy được `dummy_test_game` song song với `cultivation_online` mà không sửa `core/` hay `modules/`; từ chối nạp plugin ngoài allowlist; `PAUSE` đóng băng `SimulationClock`.
- **Test requirements:** Contract tests với ≥ 2 plugins, security test chặn dynamic path/plugin lạ, lifecycle & error-isolation tests.
- **Out-of-scope requirements:** Không triển khai đầy đủ boss/độ kiếp của GAME001 trong GD05.

### GD06 – Command Parser & Rule Engine *(gắn `TT-GD01` phần 2)*
- **Objective:** Hoàn thiện phân tích lệnh xác định (Tiếng Việt có dấu/không dấu, không LLM), cooldown per-player và khung Gift Mapping chỉ cosmetic.
- **Scope:** `Command Parser`, `Rule Engine`, bảng đăng ký 17 lệnh MVP của `cultivation_online`, Gift Mapping UI + Anti-P2W enforcement.
- **Dependencies:** `GD04`, `GD05`.
- **Deliverables:** Deterministic parser, cooldown tracker theo `SimulationClock`, Gift Mapping cosmetic-only validator.
- **Acceptance criteria:** Bình luận thường bị bỏ qua; 1 comment tối đa 1 lệnh; không cho phép điều khiển người chơi khác; gift mapping tuyệt đối không thể gắn hành động cộng XP/ATK/HP (AC16).
- **Test requirements:** Unit tests đủ 17 lệnh + aliases có dấu, injection/chuỗi dài, cooldown chính xác, security test Anti-P2W.
- **Out-of-scope requirements:** Không dùng LLM parse chat; không triển khai chiến đấu boss.

### GD07 – Asset Library & Importer
- **Objective:** Xây dựng hệ thống nhập, kiểm định (SHA-256, GLB header, path safety, license, LOD metadata), quản lý phiên bản và phân phát asset cục bộ.
- **Scope:** `Asset Library`, `Asset Importer`, `Asset Validator`, `Asset Registry`, bảng `assets`/`asset_versions`/`asset_dependencies`, bộ **Placeholder Assets** chuẩn cho `GAME001` (`TT_MAP001`, `TT_CHAR001`, `TT_CHAR002`, `TT_BOSS001`), UI Asset Library / Characters / Maps / Animations.
- **Dependencies:** `GD02`, `GD03`.
- **Deliverables:** Importer + Validator hoàn chỉnh, endpoint stream asset an toàn, placeholder package vượt qua 100% kiểm định.
- **Acceptance criteria:** Chặn 100% path traversal (`../`, absolute path, symlink, file `.exe`/`.py`), phát hiện sai hash/GLB giả, tự fallback placeholder khi thiếu asset (AC14).
- **Test requirements:** Security path traversal tests, fixture validator tests (valid/corrupt/missing license/external URI), persistence tests.
- **Out-of-scope requirements:** Không tích hợp Meshy/Tripo/AI generator/Blender; không tạo production 3D models.

### GD08 – Three.js Runtime *(gắn `TT-GD03` phần 1)*
- **Objective:** Hoàn thiện Broadcast Frontend 3D `1080×1920` với WebSocket Snapshot/Delta sync, phục hồi mất kết nối và lớp Overlay 9:16 chuẩn Safe Area.
- **Scope:** `3D Runtime` (single `WebGLRenderer`), `/ws/renderer` snapshot/delta/gap recovery, `Overlay Engine` cơ bản (Header, Footer guide, Safe Area overlay toggle), telemetry FPS/draw calls, `QWebEngineView` preview.
- **Dependencies:** `GD01`, `GD05`, `GD07`.
- **Deliverables:** Frontend runtime đồng bộ trạng thái real-time từ Backend, chịu được reload/disconnect.
- **Acceptance criteria:** Disconnect/reconnect tự đồng bộ lại đúng snapshot không reset gameplay (AC11); output dọc 9:16 rõ chữ trong Safe Area (AC17); không lỗi console và dispose sạch VRAM khi đóng.
- **Test requirements:** `tsc`, `vite build`, WebSocket gap-recovery tests, browser E2E smoke test + screenshot kiểm chứng.
- **Out-of-scope requirements:** Không tính toán luật gameplay phía frontend; không tạo WebGLRenderer thứ 2.

### GD09 – Character & Animation Engine *(gắn `TT-GD03` phần 2)*
- **Objective:** Triển khai quản lý thực thể nhân vật trong thế giới chung, animation state machine, nameplate chống chồng và cơ chế LOD/crowd cơ bản.
- **Scope:** `Character Engine`, `Animation Engine`, spawn/despawn 100 nhân vật placeholder (có tách simulation state vs render budget), ánh xạ clip chuẩn (`idle`, `walk`, `run`, `meditation`, `cast`, `sword_attack`, `hit`, `defeat`, `celebrate`), LOD switching & animation throttling.
- **Dependencies:** `GD07`, `GD08`.
- **Deliverables:** Character actor pool, animation mixer controller với fallback `idle`, sơ bộ đo hiệu năng crowd 1/20/50/100 placeholder.
- **Acceptance criteria:** Spawn/despawn 100 nhân vật không rò rỉ bộ nhớ GPU; thiếu clip không spam lỗi; tên hiển thị escape HTML và giới hạn hiển thị gần camera.
- **Test requirements:** Frontend unit tests, memory disposal soak check, XSS nameplate test.
- **Out-of-scope requirements:** Không phụ thuộc production mesh `TT-AS02/03/04`.

### GD10 – Map, Navigation & Camera Director *(gắn `TT-GD03` phần 3)*
- **Objective:** Nạp bản đồ tách zone (`TT_MAP001` placeholder/validated), cấp phát ≥100 slot tu luyện, di chuyển waypoint và vận hành Camera Director (`CAM01`–`CAM05` + tối đa 1 PiP).
- **Scope:** `Map Manager` (6 zones Thanh Vân Tông), `Navigation Engine`, `Camera Director` (priority `90/80/50/30/20/10`, `min_hold=5s`, transition `0.6s`, scissor PiP on/off, GM override `20s`).
- **Dependencies:** `GD08`, `GD09`.
- **Deliverables:** Hệ thống map/slot/waypoint và Camera Director hoàn chỉnh cả Backend intent lẫn Frontend camera controller.
- **Acceptance criteria:** 100+ người chơi phân bổ slot không trùng, vượt slot vào waitlist hình ảnh nhưng gameplay vẫn chạy; `!find` không ngắt camera Boss (AC10); tắt PiP giảm tải GPU rõ rệt.
- **Test requirements:** Unit test priority preemption, min_hold, pathfinding hội tụ, visual check 5 góc máy + PiP.
- **Out-of-scope requirements:** Không chỉnh sửa kết quả gameplay từ camera.

### GD11 – Tu Tien Player Progression *(gắn `TT-GD02`)*
- **Objective:** Triển khai hoàn chỉnh nhập môn, chọn ngoại hình/nghề, tự tu luyện, lưu tiến trình bền vững và kiểm soát hoạt động của `GAME001`.
- **Scope:** Bảng `g_cultivation_characters`, `g_cultivation_progress`, `g_cultivation_realm_history`; lệnh `!join`, `!nam`/`!nu`, `!kiem`/`!dan`/`!the`, `!tuluyen`, `!nghi`, `!roi`; Auto Cultivation (`2 XP/s`, cap `2 × cost`, tick 1s, checkpoint 10s), idle `5m` / ẩn render `10m`, GM anonymize (`ADR-012`).
- **Dependencies:** `GD05`, `GD06`, `GD10`.
- **Deliverables:** Domain services & repositories cho progression GAME001, Alembic migration `g_cultivation_*`.
- **Acceptance criteria:** Đạt `AC01` (20 `!join` đồng thời không duplicate), `AC02` (rejoin sau restart giữ đủ dữ liệu), `AC03` (10 tick +20 XP, pause không cộng, không cộng XP offline).
- **Test requirements:** Concurrency test 20 `!join`, restart persistence test, clock-injected cultivation & idle timeout tests.
- **Out-of-scope requirements:** Không triển khai Boss và Độ kiếp trong GD11.

### GD12 – Event Scheduler & Event Director *(gắn `TT-GD04`)*
- **Objective:** Vận hành lịch sự kiện tự động, trọng tài xung đột World/Personal event, hàng chờ FIFO hữu hạn và Game Master Panel đầy đủ cho GAME001.
- **Scope:** `Event Scheduler`, `Event Director`, `Event Queue`, `Game Master` (`Semi-auto/Auto/Manual`, Emergency Pause/Stop, audit logs), 10 widget GAME001 trên Desktop UI.
- **Dependencies:** `GD03`, `GD05`, `GD11`.
- **Deliverables:** Lịch 0–5–15–25 phút, cơ chế lùi Boss khi kiếp đang chạy (không chạy bù hàng loạt), Game Master Panel hoàn chỉnh.
- **Acceptance criteria:** Đạt `AC13` (Pause đóng băng clock, Stop hủy có refund và lưu dữ liệu); không chạy chồng 2 World Event; mọi thao tác hủy/reset có xác nhận và ghi `audit_logs`.
- **Test requirements:** Deterministic timeline simulation tests, conflict matrix tests, UI E2E GM controls.
- **Out-of-scope requirements:** Không triển khai logic sát thương Boss chi tiết (thuộc GD13).

### GD13 – World Boss & Reward Engine *(gắn `TT-GD05`)*
- **Objective:** Triển khai `Reward Ledger` dùng chung toàn Platform và toàn bộ sự kiện World Boss **Bạch Lang Vương** (`GAME001`).
- **Scope:** `Reward Ledger` (`UK(event_id, player_id, reward_kind)`), bảng `g_cultivation_boss_events`, `g_cultivation_boss_participants`, vòng đời 8 trạng thái, luật chiến đấu tick `2s` / phản công `6s`, kỹ năng 3 nghề (`!boss`, `!skill`, `!defend`), thưởng thắng/thua & khôi phục `REWARDING` idempotent.
- **Dependencies:** `GD11`, `GD12`.
- **Deliverables:** Platform `Reward Ledger` module + GAME001 Boss Combat Engine + Boss HUD/Control UI.
- **Acceptance criteria:** Đạt `AC07` (thắng/thua/hết giờ xác định, tính đóng góp & forfeit đúng) và `AC08` (replay và crash giữa `REWARDING` không cấp thưởng trùng).
- **Test requirements:** Deterministic combat math unit tests (3 nghề, defend + hộ thể không nhân chồng), crash-mid-reward recovery test, replay idempotency test.
- **Out-of-scope requirements:** Không nhiều boss, không PvP.

### GD14 – Breakthrough & Tribulation *(gắn `TT-GD06`)*
- **Objective:** Triển khai đột phá tăng tầng thường và hệ thống **Tiểu Thiên Kiếp** vượt đại cảnh giới (Luyện Khí → Trúc Cơ, Trúc Cơ → Kim Đan) với độ an toàn transaction tuyệt đối.
- **Scope:** Bảng `g_cultivation_tribulation_queue`, `g_cultivation_tribulation_results`; lệnh `!dotpha`, `!dokiep`, `!hothe`; giữ/giải phóng `xp_reserved`, hàng chờ FIFO tối đa 20, 5 đợt thiên lôi (`17%` / `22%` trên thang `1000` HP nguyên, không RNG), phạt `10%` khi thất bại, hoàn `100%` khi hủy/lỗi hệ thống.
- **Dependencies:** `GD11`, `GD12`, `GD13`.
- **Deliverables:** Breakthrough & Tribulation Engine, Tribulation Queue UI, Crash Recovery hoàn `xp_reserved`.
- **Acceptance criteria:** Đạt `AC04` (đủ/thiếu XP), `AC05` (20 yêu cầu FIFO, không giữ XP 2 lần, không chạy khi boss sắp mở trong 30s hoặc đang active), `AC06` (thất bại/hủy/restart xử lý XP chính xác 100%).
- **Test requirements:** Unit tests thang 1000 HP & auto/manual hộ thể, concurrency test chống giữ XP trùng, crash recovery test trong `ACTIVE`.
- **Out-of-scope requirements:** Không mở cảnh giới Nguyên Anh sau Kim Đan viên mãn; không RNG hay quà trả phí tăng tỷ lệ.

### GD15 – Inventory & Items *(gắn `TT-GD05` bổ sung)*
- **Objective:** Hoàn thiện kho vật phẩm người chơi, tiêu hao nguyên tử và tích hợp thưởng vật phẩm từ World Boss.
- **Scope:** Bảng `g_cultivation_inventory`, cấp 3 Hồi linh đan khi nhập môn, +1 khi thắng Boss, lệnh `!heal` (cooldown `20s`, hồi `30%` HP tối đa, chặn khi chết hoặc đầy HP, trừ trong cùng transaction).
- **Dependencies:** `GD11`, `GD13`.
- **Deliverables:** Inventory repository & service, tích hợp `!heal` trong Boss combat và hiển thị trong `!info` / Player List.
- **Acceptance criteria:** Không bao giờ có `quantity < 0`; chống double-spend khi gửi 2 lệnh `!heal` đồng thời; đồng bộ chính xác với `reward_ledger`.
- **Test requirements:** Atomic transaction & concurrency tests, edge cases (đầy HP, đã chết, hết đan).
- **Out-of-scope requirements:** Không chợ giao dịch P2P, không chế tạo/luyện đan sâu, không trang bị đầy đủ.

### GD16 – Notifications, Audio & Leaderboard *(gắn `TT-GD07` phần 1)*
- **Objective:** Hoàn thiện trải nghiệm truyền thông trên Broadcast Output: thông báo gộp, bảng xếp hạng, lệnh thông tin cá nhân, hiệu ứng quà cosmetic và âm thanh có kiểm soát.
- **Scope:** `Notification Engine` (template Tiếng Việt, gộp người mới/đột phá, TTS tùy chọn `1/5s`, cấm đọc raw chat), `Audio Engine` (BGM/SFX/mute/volume), lệnh `!info`/`!status`, `!find`/`!me`, `!rank`, `!help`, Leaderboard luân phiên 5 phút, giới hạn VFX cosmetic (1 lớn, 3 nhỏ, queue 20, TTL 15s, giảm nhấp nháy).
- **Dependencies:** `GD08`, `GD10`, `GD11`, `GD13`.
- **Deliverables:** Full HUD/Overlay polish, Notification/Audio services, Cosmetic Gift FX queue.
- **Acceptance criteria:** Đạt `AC10` (overlay TTL/queue, không ngắt boss), `AC16` (gift lặp dedupe, chỉ cosmetic).
- **Test requirements:** Rate-limit/TTL tests, XSS/TTS sanitization tests, multi-SFX concurrency check.
- **Out-of-scope requirements:** Không dùng AI giọng nói hội thoại NPC.

### GD17 – Authorized TikTok Integration *(gắn `TT-GD08` phần 1 — HARD GATE)*
- **Objective:** Tích hợp kết nối sự kiện TikTok LIVE **chỉ từ nguồn chính thức hoặc nhà cung cấp trung gian được cấp quyền** sau khi chủ dự án xác minh quyền truy cập.
- **Scope:** Triển khai `AuthorizedTikTokAdapter` trong `modules/tiktok_connector`, ánh xạ `ConnectorCapabilities`, heartbeat/reconnect/grace period 15s, bảo vệ credential qua `SecretStr`/OS storage, màn hình cấu hình Connector.
- **Dependencies:** `GD04`, `GD12`, xác nhận quyền truy cập từ chủ dự án (`TIKTOK_INTEGRATION_FEASIBILITY.md`).
- **Deliverables:** Authorized Connector adapter, báo cáo xác minh năng lực và giới hạn thực tế, kết quả `AC18`.
- **Acceptance criteria:** Đạt `AC12` (mất kết nối pause sau 15s) và `AC18` (Authorized Live Smoke Test trên kênh thật với tài liệu quyền & giới hạn rõ ràng). Nếu chưa có quyền truy cập hợp pháp, trạng thái bắt buộc ghi `BLOCKED`.
- **Test requirements:** Contract tests, reconnect chaos test, Authorized Live Smoke Test (ghi log chứng cứ thực tế).
- **Out-of-scope requirements:** Cấm scraping, cấm reverse-engineering giao thức lậu, cấm thu thập cookie phiên trái phép.

### GD18 – Live Studio & OBS Integration *(gắn `TT-GD07` phần 2 & `TT-GD08` phần 2)*
- **Objective:** Hoàn thiện quy trình vận hành lên sóng thực tế với OBS Studio / TikTok LIVE Studio và nhập production assets đã kiểm định (`TT-AS`) nếu sẵn sàng.
- **Scope:** `Live Studio` readiness checklist, `OBS Integration` (Browser Source `1080×1920`, tùy chọn OBS WebSocket loopback, audio routing check), `Analytics` dashboard cơ bản, kiểm chứng nhập asset production không cần sửa code game.
- **Dependencies:** `GD07`, `GD10`, `GD16`.
- **Deliverables:** Live Studio screen hoàn chỉnh, tài liệu vận hành OBS, báo cáo kiểm chứng hiển thị dọc trên thiết bị di động (`AC17`).
- **Acceptance criteria:** Đạt `AC14` (nạp GLB thật/placeholder đúng version, fallback rõ) và `AC17` (chữ rõ, không bị che bởi UI TikTok trên màn hình thật); tách biệt 100% panel quản trị khỏi nguồn capture OBS.
- **Test requirements:** OBS Browser Source capture test, visual safe-area verification, optional OBS WS offline fallback test.
- **Out-of-scope requirements:** Không tự động streaming RTMP trực tiếp từ Python (OBS/TikTok LIVE Studio đảm nhiệm encoding/RTMP).

### GD19 – Performance & Reliability *(gắn `TT-GD08` phần 3)*
- **Objective:** Đo đạc thực tế, tối ưu hóa và chứng minh độ ổn định dài hạn (soak test) cùng khả năng đáp ứng tải `100 player` với OBS capture.
- **Scope:** `Analytics` benchmark exporter, kịch bản benchmark `1 / 20 / 50 / 100` nhân vật (`p50/p95 frame time`, CPU/GPU/VRAM, draw calls, queue depth, event latency), tối ưu LOD/animation throttling/VFX pooling, burst test `100 lệnh/s` trong 30s, soak test nhiều giờ không rò rỉ RAM/VRAM/handles.
- **Dependencies:** `GD13`, `GD14`, `GD15`, `GD16`, `GD18`.
- **Deliverables:** `docs/GD19_BENCHMARK_REPORT.md` kèm số đo thật và cấu hình phần cứng; các bản vá hiệu năng nếu chưa đạt ngưỡng 30 FPS.
- **Acceptance criteria:** Đạt `AC09` (burst 100/s) và `AC15` (báo cáo số đo thật 100 player với OBS — nếu phần cứng không đạt 30 FPS ở 100 nhân vật render đầy đủ, chốt ngưỡng `max_visible_characters` và LOD thực tế minh bạch).
- **Test requirements:** Automated benchmark suite, memory/VRAM leak profiling, crash recovery regression full pass.
- **Out-of-scope requirements:** Không bịa hoặc ước lượng số FPS không đo được.

### GD20 – Windows Packaging & MVP Release *(gắn `TT-GD08` phần 4)*
- **Objective:** Đóng gói ứng dụng Windows Desktop hoàn chỉnh, dễ cài đặt/chạy local, thực hiện hồi quy toàn bộ AC01–AC18 và phát hành MVP v1.0.0.
- **Scope:** Build pipeline đóng gói Python Backend + PySide6 Desktop + built `frontend/dist` + placeholder/validated assets, khởi động/tắt tiến trình con không để orphan process, hướng dẫn vận hành cho Host, backup/restore DB tool, bộ kiểm thử hồi quy tổng thể.
- **Dependencies:** `GD01`–`GD19`.
- **Deliverables:** Gói bản dựng Windows local-first, Release Notes, `docs/GD20_RELEASE_REPORT.md` phân loại rõ `PASS/FAIL/SKIP/NOT RUN/BLOCKED` cho từng AC01–AC18.
- **Acceptance criteria:** Toàn bộ AC01–AC18 đạt `PASS` cho bản live (nếu chưa qua GD17 hoặc thiếu asset production thì phát hành trạng thái `PARTIAL / SIMULATOR-READY MVP` trung thực); khởi chạy sạch trên thư mục mới và thoát không còn tiến trình treo.
- **Test requirements:** Clean-directory install/run smoke test, full regression suite, shutdown orphan-process audit.
- **Out-of-scope requirements:** Không auto-updater cloud, không telemetry gửi ra ngoài internet, không cổng thanh toán.

---

## 3. Asset Roadmap Độc Lập (`TT-AS`) — Sản xuất Bên ngoài Platform

Luồng mỹ thuật chạy **độc lập hoàn toàn** với tiến độ code `GD01`–`GD16` (Platform dùng Placeholder hợp lệ cho tới khi gói `TT-AS` vượt qua `Asset Validator` ở `GD07`+). Mọi gói phải giao nộp đúng chuẩn `docs/platform/ASSET_CONTRACT.md` (GLB/glTF 2.0, mét, Y-up, pivot chân, SHA-256, license & provenance).

| Mã Asset | Tên gói tài nguyên | Asset ID mục tiêu | Loại | Ngưỡng kỹ thuật mục tiêu (cần kiểm định) | Trạng thái |
|---|---|---|---|---|---|
| **TT-AS01** | Art Style Guide & Color Palette (Stylized Chibi 3D Xianxia) | — *(Spec trong `asset_production/`)* | Style Spec | Bảng màu Thanh Vân Tông (xanh ngọc, đá sáng, vàng nhạt, mây), tỷ lệ Chibi | Planned |
| **TT-AS02** | Nhân vật Đệ Tử Nam | `TT_CHAR001` | `character` | GLB, `humanoid_chibi_v1`, LOD `5-8k / 2-3k / 0.5-1k`, texture 512–1024 | Planned |
| **TT-AS03** | Nhân vật Đệ Tử Nữ | `TT_CHAR002` | `character` | GLB, dùng chung rig `humanoid_chibi_v1`, LOD `5-8k / 2-3k / 0.5-1k`, texture 512–1024 | Planned |
| **TT-AS04** | Rigging & Bộ Animation nhân vật chuẩn | `TT_ANIM_CORE` | `animation` | 9 clip: `idle`, `walk`, `run`, `meditation`, `cast`, `sword_attack`, `hit`, `defeat`, `celebrate` | Planned |
| **TT-AS05** | Concept Map & Layout 6 Zone Thanh Vân Tông | — *(Spec)* | Map Spec | Bố cục dọc 9:16: `spawn_gate`, `cultivation_court` (≥100 slot), `boss_arena`, `tribulation_platform`, `sect_hall`, `paths` | Planned |
| **TT-AS06** | Bộ Props Tiên Hiệp & Vũ khí | `TT_PROP_*` | `prop` | Cổng sơn môn, đại điện, sàn đá, bồ đoàn/đài tu luyện, đài kiếp, cây, núi mây, đèn lồng, kiếm | Planned |
| **TT-AS07** | Bản đồ 3D Thanh Vân Tông hoàn chỉnh | `TT_MAP001` | `map` | GLB tách lớp (`decor_*`, `collision_*`, `walkable_*`) + `zones.json` | Planned |
| **TT-AS08** | Bộ Hiệu ứng VFX & Âm thanh có bản quyền | `TT_VFX_*`, `TT_SFX_*`, `TT_BGM_*` | `effect` / `audio` | Aura đột phá, kiếm khí, thiên lôi, boss hit, quà cosmetic (hoa sen, kiếm bay, linh quang, rồng) + license livestream | Planned |
| **TT-AS09** | World Boss — Bạch Lang Vương + Animations | `TT_BOSS001` | `character` | GLB Boss (texture tối đa 2K nếu VRAM đạt), 4 clip: `idle`, `attack`, `hit`, `defeat` | Planned |
