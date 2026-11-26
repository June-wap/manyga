# GD00 INDEPENDENT DESIGN REVIEW & RESOLUTION LOG

**Dự án:** LiveGame Studio (`D:\Tiktok Mini Game`)  
**Nhánh kiểm tra:** `design/gd00`  
**Baseline được review:** `709f762` (`709f76204a9b84ef4d4bcbd882f05dd04a515999`)  
**Ngày kiểm chứng & giải quyết (`GD00-FIX02`):** 2026-11-26  
**Kết luận sau `GD00-FIX02`:** **`PASS` (11/11 findings đã xác minh bằng nội dung repository thực tế và giải quyết triệt để; 7/7 Additional Cross-Checks đạt `PASS`; 0 runtime code GD01 được triển khai).**

---

## 1. Bảng tổng hợp Findings (`HIGH-001` – `LOW-001`)

| Finding ID | Mức độ | Chủ đề | Trạng thái sau `GD00-FIX02` | Implementation Phase |
|---|---|---|---|---|
| `HIGH-001` | HIGH | GD01 Scope Alignment & `GD01_SCOPE.md` | `RESOLVED` | `GD01` (scope lock ở `GD00`) |
| `HIGH-002` | HIGH | Development vs Production Asset Policy | `RESOLVED` | `GD07`, `GD18` |
| `HIGH-003` | HIGH | SQLite Database-Wide Single Writer | `RESOLVED` | `GD02` (design ở `GD00`) |
| `HIGH-004` | HIGH | Local API Security & Phased Security Criteria | `RESOLVED` | `GD01`–`GD17` (bắt đầu `GD01`) |
| `HIGH-005` | HIGH | Crash Recovery Matrix & Plugin-Delegated Recovery | `RESOLVED` | `GD05`, `GD12`, `GD13`, `GD14` |
| `HIGH-006` | HIGH | Snapshot/Delta Protocol (`stream_epoch`, stale/overlap/gap) | `RESOLVED` | `GD08` |
| `MEDIUM-001` | MEDIUM | World Boss Balance Risks & Combat Balance Simulator | `RESOLVED` | `GD13` |
| `MEDIUM-002` | MEDIUM | Tribulation 3-Queue Separation & Waiting Time Eval | `RESOLVED` | `GD14` (+ Post-MVP extension) |
| `MEDIUM-003` | MEDIUM | Command Contract & Plugin-Driven `commands.json` | `RESOLVED` | `GD06` |
| `MEDIUM-004` | MEDIUM | Backpressure 100% Full-Queue Policy | `RESOLVED` | `GD04` |
| `LOW-001` | LOW | Documentation Consistency & Local Markdown Links | `RESOLVED` | `GD00` |

---

## 2. Chi tiết từng Finding (Verified Against Repository Baseline `709f762`)

### HIGH-001 — GD01 Scope
- **Finding ID:** `HIGH-001`
- **Original evidence:** Tại baseline `709f762`, chưa tồn tại `docs/platform/GD01_SCOPE.md`; `docs/platform/API_CONTRACT.md:40-46` gộp chung `/health`, `/metrics`, `/settings` dưới tiêu đề `GD01+`; `docs/platform/UI_GUIDELINES.md:59-72` gán `Game Library (GD01 / GD05)` và `Asset Library (GD01 / GD07)` không ghi rõ chỉ là nav placeholder trong `GD01`, dễ gây hiểu nhầm triển khai sớm DB schema, Plugin Engine hoặc Asset Library trong `GD01`.
- **Verification result:** **CONFIRMED** trên nội dung repository `709f762`.
- **Resolution:** Chốt `docs/ROADMAP.md` là nguồn thẩm quyền duy nhất về phạm vi giai đoạn; tạo mới `docs/platform/GD01_SCOPE.md` đóng khung đúng 13 hạng mục được phép trong `GD01` và liệt kê rõ loại trừ (`GD02` DB migrations & Application Services, `GD05` Game Plugin Engine & `cultivation_online` skeleton, `GD07` Asset Library); đồng bộ phase cột/bảng trong `ROADMAP.md`, `API_CONTRACT.md` và `UI_GUIDELINES.md`.
- **Files changed:** `docs/platform/GD01_SCOPE.md`, `docs/ROADMAP.md`, `docs/platform/API_CONTRACT.md`, `docs/platform/UI_GUIDELINES.md`, `README.md`.
- **Acceptance criteria:** `GD01` chỉ triển khai đúng 13 hạng mục trong `GD01_SCOPE.md`; không có full Alembic migrations (`GD02`), không có `games/cultivation_online/` (`GD05`), không có Asset Importer/Library (`GD07`); các tab GD02+ trên Desktop UI chỉ là placeholder được gắn nhãn rõ ràng.
- **Implementation phase:** `GD01` (scope lock hoàn tất ở `GD00`).
- **Status:** `RESOLVED`

### HIGH-002 — Development Asset Policy
- **Finding ID:** `HIGH-002`
- **Original evidence:** Tại baseline `709f762`, `docs/platform/ASSET_CONTRACT.md:52,130-133` chỉ mô tả `is_placeholder: true` và fallback chung chung, chưa tách rạch ròi 2 chế độ vận hành `DEVELOPMENT` và `PRODUCTION`, cũng chưa chặn việc đánh dấu `production-ready` khi thiếu dependency hoặc dùng placeholder chưa phê duyệt.
- **Verification result:** **CONFIRMED** trên nội dung repository `709f762`.
- **Resolution:** Thiết kế đầy đủ chính sách hai chế độ `DEVELOPMENT` vs `PRODUCTION` (`ADR-016`): `DEVELOPMENT` cho phép placeholder tương thích kèm cảnh báo nổi bật và không đòi hỏi production asset; `PRODUCTION` bắt buộc tồn tại đủ `required_assets`, đúng semver, `validation_status = VALID`, cấm tự bỏ qua dependency thiếu và cấm đánh dấu `PRODUCTION_READY` khi còn placeholder chưa phê duyệt.
- **Files changed:** `docs/platform/ASSET_CONTRACT.md`, `docs/platform/GAME_PLUGIN_CONTRACT.md`, `docs/platform/MODULE_DESIGN.md`, `docs/ROADMAP.md`, `docs/platform/TESTING_POLICY.md`, `docs/DECISIONS.md`.
- **Acceptance criteria:** Kiểm thử thành công ở `GD07`/`GD18` cả 2 chế độ: `DEVELOPMENT` fallback kèm cảnh báo `PLACEHOLDER_ACTIVE`, `PRODUCTION` chặn readiness khi thiếu required asset hoặc dùng placeholder chưa duyệt (`AC14`).
- **Implementation phase:** `GD07` (Asset Registry/Validator), `GD18` (Live Studio Readiness).
- **Status:** `RESOLVED`

### HIGH-003 — SQLite Single Writer
- **Finding ID:** `HIGH-003`
- **Original evidence:** Tại baseline `709f762`, `docs/platform/TDD.md:51` viết *"với serialization hợp lý theo `player_id` hoặc hàng đợi ghi tập trung"*, ngụ ý khóa theo từng `player_id` có thể thay thế serialization ghi toàn DB, đồng thời thiếu `transaction_timeout` và cơ chế drain hàng đợi ghi khi shutdown.
- **Verification result:** **CONFIRMED** — vì SQLite khóa toàn bộ file DB khi ghi (kể cả trong `WAL`), per-player lock không ngăn được `SQLITE_BUSY` khi 2 người chơi khác nhau ghi đồng thời.
- **Resolution:** Cập nhật `ADR-014`, `TDD.md`, `DATABASE_DESIGN.md` và `MODULE_DESIGN.md` chốt **Centralized Write Coordinator** (database-wide global write serializer / bounded write queue `max_write_queue = 512`, tối đa **1 write transaction toàn DB tại một thời điểm**), `UnitOfWork`, `WAL`, `foreign_keys=ON`, `busy_timeout=5000ms`, `transaction_timeout_ms=5000`, rollback tự động khi lỗi/timeout và drain + `wal_checkpoint(TRUNCATE)` khi shutdown; khẳng định rõ per-player lock không đủ cho SQLite write contention.
- **Files changed:** `docs/platform/TDD.md`, `docs/platform/DATABASE_DESIGN.md`, `docs/platform/MODULE_DESIGN.md`, `docs/ROADMAP.md`, `docs/DECISIONS.md`.
- **Acceptance criteria:** Multi-player concurrent write integration test ở `GD02` không phát sinh `SQLITE_BUSY`; transaction vượt timeout tự rollback nguyên tử; graceful shutdown không mất transaction đã nhận.
- **Implementation phase:** `GD02` (chỉ thiết kế ở `GD00`).
- **Status:** `RESOLVED`

### HIGH-004 — Local API Security
- **Finding ID:** `HIGH-004`
- **Original evidence:** Tại baseline `709f762`, `git grep -n "CORS\|Trusted\|Origin\|auth\|token" docs/platform/API_CONTRACT.md` trả về **0 kết quả**; chỉ có loopback binding `127.0.0.1` mà chưa có Trusted Host, restricted Origin/no wildcard CORS, local session auth, phân quyền Admin vs Renderer, WS auth+Origin validation hay security criteria theo giai đoạn.
- **Verification result:** **CONFIRMED** trên nội dung repository `709f762`.
- **Resolution:** Bổ sung hoàn chỉnh Mục 1.5 *Local API Security Model* trong `API_CONTRACT.md` và `ADR-017`: loopback `127.0.0.1`, `TrustedHostMiddleware`, restricted Origin (**cấm wildcard CORS `*`**), khóa phiên ngẫu nhiên mật mã tách quyền `ADMIN_SESSION_TOKEN` (privileged REST + `/ws/admin`) vs `RENDERER_STREAM_TOKEN` (read-only `/ws/renderer` + validated asset stream), phân biệt `GET /api/v1/health` công khai cục bộ tối thiểu với privileged endpoints, cấm đặt Admin Token trong Broadcast URL, cấm log credentials, cấm expose arbitrary file paths; bổ sung bảng Phased Security Acceptance Criteria từ `GD01` đến `GD17` trong `TESTING_POLICY.md`, `GD01_SCOPE.md` và `ROADMAP.md`.
- **Files changed:** `docs/platform/API_CONTRACT.md`, `docs/ARCHITECTURE.md`, `docs/platform/GD01_SCOPE.md`, `docs/platform/TESTING_POLICY.md`, `docs/platform/UI_GUIDELINES.md`, `docs/platform/MODULE_DESIGN.md`, `docs/ROADMAP.md`, `docs/DECISIONS.md`.
- **Acceptance criteria:** Đạt đầy đủ bảng *Phased Security Acceptance Criteria* (`TESTING_POLICY.md` Mục 4.5) bắt đầu ngay từ `GD01` (loopback, TrustedHost, no wildcard CORS, health vs auth boundary, log redaction).
- **Implementation phase:** `GD01` (nền tảng bảo mật loopback/Host/CORS/auth boundary), tiếp nối `GD02`, `GD03`, `GD05`, `GD07`, `GD08`, `GD17`.
- **Status:** `RESOLVED`

### HIGH-005 — Crash Recovery
- **Finding ID:** `HIGH-005`
- **Original evidence:** Tại baseline `709f762`: (1) `docs/platform/TDD.md:113` dùng tên trạng thái `PAUSING` lệch với CHECK constraint của `DATABASE_DESIGN.md:346` (`PAUSED`/`STOPPING`); (2) `TDD.md:116` và `DATABASE_DESIGN.md:408-409` ghi trực tiếp bảng `g_cultivation_tribulation_queue`/`g_cultivation_boss_events` bên trong luồng recovery tầng Platform; (3) thiếu ma trận recovery đầy đủ cho `RESOLVING` (pre vs post-commit immutable outcome), `REWARDING`, `COMPLETED`, `CANCELED`, `FAILED` và thiếu cột `outcome_committed` / `outcome_snapshot_json` trong ERD.
- **Verification result:** **CONFIRMED** trên nội dung repository `709f762`.
- **Resolution:** Bổ sung `outcome_committed` và `outcome_snapshot_json` vào `DATABASE_DESIGN.md`; thống nhất 100% tên trạng thái session & event giữa ERD, TDD và Game Plugin Contract (loại bỏ `PAUSING`); thiết kế đầy đủ **Event Crash Recovery Matrix** trong `TDD.md` Mục 6.2 cho tất cả trạng thái (`SCHEDULED`, `ANNOUNCING`, `REGISTRATION`, `PREPARING`, `ACTIVE`, `RESOLVING` pre/post-commit, `REWARDING`, `COMPLETED`, `CANCELED`, `CANCELED_RECOVERY`, `FAILED`); tách tuyệt đối Platform Recovery Core khỏi Plugin Recovery Handlers (`plugin.recover_after_crash(uow, ctx)` — `ADR-018`).
- **Files changed:** `docs/platform/TDD.md`, `docs/platform/DATABASE_DESIGN.md`, `docs/platform/GAME_PLUGIN_CONTRACT.md`, `docs/platform/MODULE_DESIGN.md`, `docs/platform/TESTING_POLICY.md`, `docs/ROADMAP.md`, `docs/DECISIONS.md`.
- **Acceptance criteria:** Crash recovery matrix test ở `GD12`/`GD13`/`GD14` xác minh pre-commit `RESOLVING`/`ACTIVE` chuyển `CANCELED_RECOVERY` hoàn 100% `xp_reserved`, post-commit `RESOLVING`/`REWARDING` trả thưởng idempotent không trùng, terminal states là no-op, và `core/`/`modules/` không chứa bất kỳ tham chiếu nào tới bảng `g_cultivation_*` (`AC06`, `AC08`).
- **Implementation phase:** `GD05` (contract hook), `GD12` (orchestrator), `GD13`–`GD14` (plugin handlers).
- **Status:** `RESOLVED`

### HIGH-006 — Snapshot/Delta Protocol
- **Finding ID:** `HIGH-006`
- **Original evidence:** Tại baseline `709f762`, `git grep -n "epoch\|snapshot_seq\|overlap\|stale" docs/platform/API_CONTRACT.md docs/platform/TDD.md` trả về **0 kết quả**; giao thức chỉ có `revision` và `gap_detected`, thiếu `stream_epoch`, `snapshot_seq`, `request_id` correlation và xử lý stale snapshot, overlapping revision, backend restart và vòng đời resync.
- **Verification result:** **CONFIRMED** trên nội dung repository `709f762`.
- **Resolution:** Nâng cấp toàn bộ giao thức `/ws/renderer` trong `API_CONTRACT.md` Mục 3.1, `TDD.md` Mục 4 và `ADR-019`: bổ sung `stream_epoch`, `session_id`, `revision`, `snapshot_seq`, `request_id`; quy định chỉ apply delta khi khớp đồng thời `stream_epoch`, `session_id` và `from_revision == last_applied_revision`; lập bảng xử lý bắt buộc cho stale snapshot, duplicate delta, overlapping revision, revision gap, backend restart, renderer reconnect và vòng đời `DISCONNECTED → CONNECTING → AWAITING_SNAPSHOT → SYNCED ⇄ RESYNCING`.
- **Files changed:** `docs/platform/API_CONTRACT.md`, `docs/platform/TDD.md`, `docs/platform/TESTING_POLICY.md`, `docs/ROADMAP.md`, `docs/DECISIONS.md`.
- **Acceptance criteria:** Integration/frontend tests tại `GD08` xác minh 100% các kịch bản: stale snapshot bị drop, duplicate delta no-op, overlapping/gap/epoch mismatch buộc chuyển `RESYNCING` và đồng bộ lại đúng snapshot không làm sai lệch gameplay (`AC11`).
- **Implementation phase:** `GD08`.
- **Status:** `RESOLVED`

### MEDIUM-001 — World Boss Balance
- **Finding ID:** `MEDIUM-001`
- **Original evidence:** Tại baseline `709f762`, `docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md` chỉ ghi chung công thức Boss là `PROPOSED`, chưa phân tích rủi ro cụ thể đối với nhóm Phàm Nhân (DPS thấp trước `DEF=8`, `100 HP` dễ tử trận sớm trước đòn phản công 6s) hay scaling tuyến tính `180×N` không tính phân bố cảnh giới, và `ROADMAP.md` (`GD13`) chưa yêu cầu **Combat Balance Simulator**.
- **Verification result:** **CONFIRMED** trên nội dung repository `709f762`.
- **Resolution:** **Giữ nguyên 100% công thức trong `GDD.md`** (không tự ý sửa); ghi nhận đầy đủ 3 rủi ro cân bằng trong `GDD_REQUIREMENTS_MAPPING.md` và `PROJECT_STATUS.md`; bổ sung yêu cầu bắt buộc **Combat Balance Simulator** tại `GD13` (`ROADMAP.md`, `TESTING_POLICY.md`) mô phỏng các nhóm `1, 5, 10, 20, 50, 100` người chơi, đa cảnh giới, đa nghề, auto-attack only, active skills, mixed player activity và boss retaliation.
- **Files changed:** `docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md`, `docs/ROADMAP.md`, `docs/platform/TESTING_POLICY.md`, `docs/PROJECT_STATUS.md`.
- **Acceptance criteria:** `GD13` xuất báo cáo mô phỏng cân bằng đầy đủ cho toàn bộ tổ hợp cohort trước khi đề xuất điều chỉnh config cân bằng cho chủ dự án duyệt (`AC07`).
- **Implementation phase:** `GD13`.
- **Status:** `RESOLVED`

### MEDIUM-002 — Tribulation Queue
- **Finding ID:** `MEDIUM-002`
- **Original evidence:** Tại baseline `709f762`, `docs/platform/TDD.md`, `MODULE_DESIGN.md` và `ROADMAP.md` (`GD14`) chưa tách tường minh 3 loại hàng chờ (Gameplay Execution vs Camera Focus vs Event Presentation), chưa nêu rõ sự kiện cá nhân không bắt buộc chiếm camera chính, chưa yêu cầu đánh giá queue waiting time và chưa ghi đề xuất mở rộng parallel/batch hậu MVP.
- **Verification result:** **CONFIRMED** trên nội dung repository `709f762`.
- **Resolution:** Giữ nguyên luật MVP (`max 1 active`, FIFO tối đa `20`, không đổi balance); tách bạch 3 hàng chờ độc lập (`Gameplay Execution Queue`, `Camera Focus Queue`, `Event Presentation Queue` — `ADR-020`) trong `TDD.md`, `MODULE_DESIGN.md` và `GDD_REQUIREMENTS_MAPPING.md`; khẳng định sự kiện cá nhân không bắt buộc chiếm camera chính; bổ sung yêu cầu đo **queue waiting time** tại `GD14` và ghi nhận hướng mở rộng hậu MVP (Parallel/Batch Tribulation).
- **Files changed:** `docs/platform/TDD.md`, `docs/platform/MODULE_DESIGN.md`, `docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md`, `docs/ROADMAP.md`, `docs/platform/TESTING_POLICY.md`, `docs/DECISIONS.md`.
- **Acceptance criteria:** `GD14` chứng minh 3 hàng chờ hoạt động độc lập, không ép camera chính cho mọi sự kiện cá nhân, và có báo cáo đo queue waiting time với 20 yêu cầu đồng thời (`AC05`).
- **Implementation phase:** `GD14` (parallel/batch extension: Post-MVP).
- **Status:** `RESOLVED`

### MEDIUM-003 — Command Contract
- **Finding ID:** `MEDIUM-003`
- **Original evidence:** Tại baseline `709f762`, `docs/platform/EVENT_CONTRACT.md:76` thiếu `!roi` (opt-out) trong danh sách cooldown, và cả `GAME_PLUGIN_CONTRACT.md` lẫn `EVENT_CONTRACT.md` chưa có bảng đặc tả đầy đủ `commands.json` (canonical, aliases, args, cooldown groups, preconditions, validation, ownership, error codes, opt-out) cũng như quy tắc tường minh cấm Platform `Command Parser` hardcode lệnh của `cultivation_online`.
- **Verification result:** **CONFIRMED** trên nội dung repository `709f762`.
- **Resolution:** Bổ sung schema `commands.json` trong `GAME_PLUGIN_CONTRACT.md` Mục 4.1.1 và bảng đối chiếu đầy đủ toàn bộ lệnh MVP (gồm cả `!hotheauto`/`on`/`off` và `!roi` opt-out) trong `EVENT_CONTRACT.md` Mục 3.5; khẳng định rõ trong `MODULE_DESIGN.md` và `GAME_PLUGIN_CONTRACT.md` rằng Platform `Command Parser` nạp động 100% từ `commands.json` của từng plugin và tuyệt đối không hardcode lệnh `cultivation_online`.
- **Files changed:** `docs/platform/EVENT_CONTRACT.md`, `docs/platform/GAME_PLUGIN_CONTRACT.md`, `docs/platform/MODULE_DESIGN.md`.
- **Acceptance criteria:** Ở `GD06`, Platform `Command Parser` pass bộ test với `commands.json` của `cultivation_online` và 1 plugin giả lập khác mà không chứa chuỗi lệnh cứng nào của GAME001 trong `modules/command_parser/`.
- **Implementation phase:** `GD06`.
- **Status:** `RESOLVED`

### MEDIUM-004 — Backpressure
- **Finding ID:** `MEDIUM-004`
- **Original evidence:** Tại baseline `709f762`, `docs/platform/EVENT_CONTRACT.md:78-80` chỉ quy định load shedding tại ngưỡng `70%` và `90%`, chưa định nghĩa chính sách khi hàng đợi đạt **`100%`** (explicit rejection, admission control, bounded retries, non-blocking Event Gateway, metrics/auditability, phân biệt target throughput với guaranteed delivery).
- **Verification result:** **CONFIRMED** trên nội dung repository `709f762`.
- **Resolution:** Bổ sung đầy đủ chính sách ngưỡng `100%` trong `EVENT_CONTRACT.md` Mục 3.3, `DATABASE_DESIGN.md` (`REJECTED_BACKPRESSURE`), `MODULE_DESIGN.md` (`Event Gateway`, `Event Bus`) và `ADR-020`: phân biệt rõ Target Throughput (`100 lệnh/s` burst 30s) với Guaranteed Delivery; khi đầy `100%` thực hiện Admission Control trả `INGESTION_QUEUE_FULL` (`HTTP 429`), enqueue timeout hữu hạn (`50ms`, retry `<=2`), tuyệt đối không silently drop lệnh gameplay và không block vô hạn Event Gateway, ghi đầy đủ metrics và auditability.
- **Files changed:** `docs/platform/EVENT_CONTRACT.md`, `docs/platform/DATABASE_DESIGN.md`, `docs/platform/MODULE_DESIGN.md`, `docs/platform/TESTING_POLICY.md`, `docs/DECISIONS.md`.
- **Acceptance criteria:** Burst & overflow tests tại `GD04`/`GD19` chứng minh khi ép đầy `100%`, Gateway trả `INGESTION_QUEUE_FULL` trong `<= 150ms`, không treo, không silently drop lệnh gameplay và ghi đủ metrics/audit (`AC09`).
- **Implementation phase:** `GD04` (core policy), `GD19` (burst verification).
- **Status:** `RESOLVED`

### LOW-001 — Documentation Consistency
- **Finding ID:** `LOW-001`
- **Original evidence:** Sau khi bổ sung `GD01_SCOPE.md`, `ADR-016`–`ADR-020`, `GD00_INDEPENDENT_REVIEW.md` và `GD00_FIX02_REPORT.md`, cần đồng bộ đầy đủ `GDD.md` v0.1.1, `README.md`, `ROADMAP.md`, `PROJECT_STATUS.md`, `DECISIONS.md`, `CHANGELOG.md` và kiểm tra 100% local Markdown links.
- **Verification result:** **CONFIRMED** và đã thực thi kiểm tra tự động trên toàn bộ tệp `.md`.
- **Resolution:** Đồng bộ toàn bộ tài liệu quản trị và hợp đồng; xác minh `0` broken local Markdown links trên toàn bộ repository, `0` tham chiếu sai `4GB VRAM`, `0` trạng thái `PAUSING` lệch chuẩn, và `0` file code runtime GD01.
- **Files changed:** `README.md`, `docs/PROJECT_STATUS.md`, `docs/DECISIONS.md`, `docs/CHANGELOG.md`, `docs/ROADMAP.md`, `docs/GD00_INDEPENDENT_REVIEW.md`, `docs/GD00_FIX02_REPORT.md`.
- **Acceptance criteria:** Automated cross-check đạt `0` broken links, `0` mâu thuẫn tên trạng thái/phase/scope.
- **Implementation phase:** `GD00` (hoàn tất ngay trong `GD00-FIX02`).
- **Status:** `RESOLVED`

---

## 3. Kết quả Kiểm tra Bổ sung (Additional Cross-Checks — 7/7 `PASS`)

| # | Hạng mục kiểm tra bổ sung | Kết quả | Bằng chứng xác minh trong repository |
|---|---|---|---|
| 1 | Platform không import `cultivation_online` trực tiếp | **`PASS`** | Khóa cứng trong `AGENTS.md`, `ARCHITECTURE.md` Mục 2, `MODULE_DESIGN.md` Mục 1 & 8, `TDD.md` Mục 6.1 (đã gỡ toàn bộ hardcode `g_cultivation_*` khỏi Platform recovery) và `EVENT_CONTRACT.md` Mục 3.5 (cấm hardcode lệnh trong `Command Parser`). |
| 2 | Plugin security dựa trên static trusted allowlist, không chỉ module path prefix | **`PASS`** | Đã củng cố trong `GAME_PLUGIN_CONTRACT.md` Mục 2, `ARCHITECTURE.md` Mục 6, `MODULE_DESIGN.md` Module 6, `DECISIONS.md` (`ADR-010`) và `TESTING_POLICY.md` Mục 4.5 (`GD05` gate). |
| 3 | Không phát sinh dependency cycle | **`PASS`** | DAG một chiều giữ vững: `core/` → (none); `modules/` → `core/` + lower-tier `modules/`; `games/` → `core/` + `modules/` facades; `apps/` → composition root; `frontend/` → JSON/WS protocol only. |
| 4 | Database state names thống nhất giữa ERD, TDD và Plugin Contract | **`PASS`** | Đã sửa lệch `PAUSING` ở `TDD.md`; thống nhất 100% 7 session states (`CREATED`, `RUNNING`, `PAUSED`, `PAUSED_ERROR`, `STOPPING`, `COMPLETED`, `INTERRUPTED_RECOVERED`), 11 event states (`SCHEDULED`, `ANNOUNCING`, `REGISTRATION`, `PREPARING`, `ACTIVE`, `RESOLVING`, `REWARDING`, `COMPLETED`, `CANCELED`, `CANCELED_RECOVERY`, `FAILED`) và 5 ingestion states (`ACCEPTED`, `DUPLICATE`, `REJECTED`, `RATE_LIMITED`, `REJECTED_BACKPRESSURE`). |
| 5 | API implementation phase thống nhất với `ROADMAP.md` & `GD01_SCOPE.md` | **`PASS`** | Toàn bộ bảng endpoint trong `API_CONTRACT.md` Mục 2 & 3 đã gắn cột `Auth Scope` và `Phase` khớp 1-1 với `ROADMAP.md` và `GD01_SCOPE.md` (chỉ `GET /api/v1/health` thuộc `GD01`). |
| 6 | Production asset không chặn development | **`PASS`** | Đã chuẩn hóa chế độ `DEVELOPMENT` vs `PRODUCTION` trong `ASSET_CONTRACT.md`, `GAME_PLUGIN_CONTRACT.md` và `ADR-016`; `TT-AS01`–`TT-AS09` tách độc lập hoàn toàn. |
| 7 | Không mở rộng sang `GD01` / không tạo runtime code | **`PASS`** | `CODE_OR_BINARY_FILES: 0` (không có tệp `.py`, `.ts`, `.js`, `.glb`, `.db` trong workspace). |
