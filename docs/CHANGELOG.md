# CHANGELOG — LIVEGAME STUDIO

Mọi thay đổi đáng chú ý của dự án được ghi nhận tại đây theo chuẩn [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.1.0-gd01-rc1] - 2026-11-26

### Fixed
- Tái hiện/sửa free-text Authorization Basic/multi-cookie redaction còn lộ giá trị và Uvicorn re-log ASGI exception ngoài safe logger. Console handlers dùng cùng registered-secret redaction; UTF-8 console được cấu hình khi hỗ trợ.

### Review evidence
- Source candidate `f60bf4a`, baseline `959bb3a`; thêm recorded RC1 runner, source manifest/tree, command outputs/exit codes, GUI/static WebGL screenshots và descendant cleanup evidence.
- Final regression **57 PASS** (49 pytest, 3 Vitest, 5 Playwright), gồm actual Unicode CWD, temp A/B DB isolation/restart, real CLI port conflict/HTTP security, optional GPU-tool/debug-extension absence, external/unrelated process preservation và static production rendering.
- Tạo `GD01_REVIEW_EVIDENCE.md`, cập nhật delivery/status, ghi tracker asset/cache/factory/skeleton/appearance/LOD/persistence cho GD07/GD08/GD09/GD11/GD19; không implement GD01.
- Independent review giữ BLOCKED; không retry Antigravity, không chuyển agent hoặc bypass permission/execution policy. Overall PARTIAL/READY_FOR_INDEPENDENT_REVIEW; không GD02, không push/merge.

---

## [0.1.0-gd01-standalone] - 2026-11-26

### Architecture / scope clarification
- ADR-021 chốt Standalone Local-first Windows Desktop: độc lập theo thiết bị/Windows user, TikTok identity và progression chỉ trong local DB/game/world; supersede các đề xuất Hybrid Cloud cũ, giữ lịch sử ADR.
- Cập nhật AGENTS, README, PROJECT_SPEC, ARCHITECTURE, ROADMAP, PROJECT_STATUS, TDD, DATABASE_DESIGN, GD01_SCOPE, TESTING_POLICY và DECISIONS. Không thay schema/gameplay/API version; DATABASE_DESIGN 1.0.1 là documentation clarification.
- First-run/default seed/zero-player DB và data-preserving migrations thuộc GD02; no developer DB/test accounts/.env/credentials trong installer, bundled runtime/end-user portability GD20. Không Cloud requirements/GD21–GD26; multi-hardware/non-NVIDIA acceptance GD19. Reset game là deferred design; cross-device backup/restore không bắt buộc MVP.

### Foundation
- Mặc định `%LOCALAPPDATA%\LiveGameStudio` thay cho checkout data/logs; tách database/config/assets/cache/logs, giữ explicit local dev overrides và không auto move/import DB cũ. Chặn UNC/mapped network paths; thêm smoke/Unicode/path-isolation/relocation tests, không implement production initialization/migrations.
- Kết quả test và independent contract review ghi tại `docs/GD01_ARCHITECTURE_UPDATE_REPORT.md`; không tái sử dụng PASS baseline để nhận các chức năng GD02/GD20 đã hoàn tất.

---

## [0.1.0-gd01-foundation] - 2026-11-26

### Added
- Application Core, typed `LGS_*` config, UTF-8 rotating JSONL/console logging với redaction, error handling và SQLite smoke thật (WAL/FK/5000ms timeout/commit/rollback/reopen).
- FastAPI factory, minimal public health, loopback-only CLI, Trusted Host, explicit local Origin/CORS policy; credentials phiên chỉ ở memory và development-only admin boundary smoke.
- PySide6 Desktop shell Dark/Purple, 14 navigation entries với placeholder đúng phase, Dashboard dữ liệu thật, Settings readonly, QWebEngine Foundation Demo và process supervisor bất đồng bộ.
- TypeScript/Vite/Three.js procedural scene 9:16, một renderer, resize/animation/disposal/WebGL error states, browser preview 1080×1920.
- Pinned Python/frontend dependency locks, PowerShell setup/start/stop/test scripts, 37 automated tests và GUI/script integration evidence.
- `GD01_ENVIRONMENT_REPORT.md`, `GD01_DELIVERY_REPORT.md` và screenshots thật trong `docs/evidence/gd01/`.

### Verified / Scope
- Final combined run: 31 pytest, 3 Vitest, 3 Playwright PASS; real GUI/embedded WebGL, owned tree shutdown và PowerShell start/stop PASS. Independent review NOT RUN; overall GD01 PARTIAL pending phase gate.
- Giữ nguyên GD00 design/contracts và GDD. Không triển khai GD02 schema/services, GD05 plugin/gameplay, GD07 assets, WebSocket, TikTok hoặc OBS.

---

## [0.0.3-gd00-fix02] - 2026-11-26

### Added
- `docs/platform/GD01_SCOPE.md` — Đặc tả phạm vi đóng khung cho `GD01` đồng bộ 100% với `docs/ROADMAP.md` (`HIGH-001`).
- `docs/GD00_INDEPENDENT_REVIEW.md` — Hồ sơ kiểm chứng độc lập toàn bộ findings (`HIGH-001`..`HIGH-006`, `MEDIUM-001`..`MEDIUM-004`, `LOW-001` và 7 mục Cross-Check).
- `docs/GD00_FIX02_REPORT.md` — Báo cáo bàn giao giải quyết toàn bộ findings trước khi bước sang GD01.
- Các quyết định kiến trúc `ADR-016`–`ADR-020` và củng cố `ADR-010`, `ADR-014` trong `docs/DECISIONS.md`.

### Changed
- **HIGH-001 (GD01 Scope):** Đồng bộ `ROADMAP.md`, `API_CONTRACT.md` và `UI_GUIDELINES.md` theo `GD01_SCOPE.md` (chốt DB migrations/services thuộc `GD02`, Plugin Engine/`cultivation_online` skeleton thuộc `GD05`, Asset Library thuộc `GD07`).
- **HIGH-002 (Development vs Production Asset Policy):** Thiết kế hai chế độ `DEVELOPMENT` và `PRODUCTION` trong `ASSET_CONTRACT.md`, `GAME_PLUGIN_CONTRACT.md`, `MODULE_DESIGN.md` và `ROADMAP.md`.
- **HIGH-003 (SQLite Single Writer):** Chốt **Centralized Write Coordinator** (database-wide single-writer serialization, bounded write queue, `transaction_timeout`, rollback & shutdown drain) trong `TDD.md`, `DATABASE_DESIGN.md`, `MODULE_DESIGN.md` và `ADR-014`.
- **HIGH-004 (Local API Security):** Bổ sung mô hình bảo mật cục bộ đầy đủ (`127.0.0.1`, `TrustedHost`, no wildcard CORS, tách `ADMIN_SESSION_TOKEN` vs `RENDERER_STREAM_TOKEN`, WS Auth+Origin, public `/health` vs privileged REST, phased security acceptance criteria từ GD01+) trong `API_CONTRACT.md`, `ARCHITECTURE.md`, `TESTING_POLICY.md` và `GD01_SCOPE.md`.
- **HIGH-005 (Crash Recovery Matrix):** Bổ sung ma trận phục hồi cho mọi trạng thái (`RESOLVING` pre/post-commit immutable `outcome_snapshot_json`, `REWARDING`, `COMPLETED`, `CANCELED`, `FAILED`) và tách biệt hoàn toàn Platform Recovery Core với Plugin Recovery Handlers trong `TDD.md`, `DATABASE_DESIGN.md`, `GAME_PLUGIN_CONTRACT.md` và `MODULE_DESIGN.md`.
- **HIGH-006 (Snapshot/Delta Protocol):** Bổ sung `stream_epoch`, `snapshot_seq`, `request_id`, quy tắc apply nghiêm ngặt, xử lý stale snapshot / duplicate / overlapping / gap / backend restart / renderer reconnect và vòng đời Resync trong `API_CONTRACT.md` và `TDD.md`.
- **MEDIUM-001..004 & LOW-001:** Ghi nhận rủi ro cân bằng World Boss + Combat Balance Simulator tại `GD13` (không sửa công thức GDD); tách 3 hàng chờ Tiểu Thiên Kiếp + đánh giá queue waiting time tại `GD14` + đề xuất parallel/batch hậu MVP; chuẩn hóa đầy đủ `commands.json` & cấm hardcode lệnh game trong Platform `Command Parser`; bổ sung chính sách Backpressure `100%` (explicit rejection `INGESTION_QUEUE_FULL`, không silent drop gameplay, không block vô hạn Gateway); củng cố static trusted plugin allowlist và đồng bộ toàn bộ tài liệu + links.

---

## [0.0.2-gd00-fix01] - 2026-11-26

### Changed
- **ADR-007 Resolved:** Di chuyển nguyên vẹn GDD GAME001 bằng `git mv` từ `GDD_Tu_Tien_Online_v0.1.md` sang `docs/games/cultivation_online/GDD.md` (xác minh SHA-256 trước/sau trùng khớp `0A4F9D8B3D2005D0947A7C48E85F87D6B143ECC851DEB0E6345D27B2FF4AE534`) và đồng bộ toàn bộ đường dẫn tham chiếu trong repo.
- **CONF-04 / OPEN-05 Resolved (`ADR-015`):** Ban hành GDD Amendment `v0.1.1` bổ sung bộ lệnh MVP `!hothe`, `!hotheauto`, `!hotheauto on`, `!hotheauto off` (hộ thể tự động mặc định bật, server-side event timing hỗ trợ độ trễ livestream, GM cấu hình mặc định, giữ nguyên toàn bộ thông số cân bằng gốc v0.1.0); cập nhật `EVENT_CONTRACT.md`, `GAME_PLUGIN_CONTRACT.md`, `DATABASE_DESIGN.md` (`auto_guard_enabled`), `MODULE_DESIGN.md`, `TESTING_POLICY.md`, `ROADMAP.md` và `GDD_REQUIREMENTS_MAPPING.md`.
- **Hardware Verification:** Đo xác minh thực tế bằng `nvidia-smi` (RTX 4050 Laptop: Tổng VRAM `6141 MiB`, Đang dùng `101 MiB`, Khả dụng `5820 MiB`; RAM Tổng `15.73 GB` / Khả dụng `3.14 GB`; Disk `D:\` `29.83/80 GB`, `C:\` `76.40/395.79 GB`) và cập nhật `docs/GD00_ENVIRONMENT_REPORT.md`.
- **Performance Targets:** Bổ sung đầy đủ mục tiêu kiểm thử MVP (gồm phiên chạy liên tục **4 giờ** và giám sát **CPU/RAM/GPU/VRAM**) vào `PROJECT_SPEC.md`, `TDD.md`, `TESTING_POLICY.md` và `ROADMAP.md` (ghi rõ là mục tiêu benchmark, chưa phải số đo đạt được).

### Added
- `docs/GD00_FIX01_REPORT.md` — Báo cáo bàn giao đầy đủ kết quả `GD00-FIX01`.

---

## [0.0.1-gd00] - 2026-11-26

### Added
- Khởi tạo nhánh thiết kế `design/gd00` và cấu trúc thư mục chuẩn (`apps/`, `core/`, `modules/`, `games/`, `frontend/`, `assets/`, `asset_production/`, `docs/`, `scripts/`, `tests/`).
- Tạo `.gitignore` cho Python, Node.js/Vite, Windows và raw Blender assets.
- Tạo bộ tài liệu quản trị & đặc tả nền tảng:
  - `AGENTS.md`, `README.md`, `docs/PROJECT_SPEC.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`, `docs/PROJECT_STATUS.md`, `docs/CHANGELOG.md`.
- Tạo bộ tài liệu thiết kế kỹ thuật Platform (`docs/platform/`):
  - `TDD.md`, `MODULE_DESIGN.md` (37 modules), `DATABASE_DESIGN.md` (14 bảng Platform + 8 bảng GAME001 + ERD), `GAME_PLUGIN_CONTRACT.md`, `ASSET_CONTRACT.md`, `API_CONTRACT.md`, `EVENT_CONTRACT.md`, `UI_GUIDELINES.md`, `TESTING_POLICY.md`, `TIKTOK_INTEGRATION_FEASIBILITY.md`.
- Kiểm tra và lập bảng đối chiếu GDD gốc `GDD_Tu_Tien_Online_v0.1.md` tại `docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md`.
- Lập báo cáo môi trường thực tế `docs/GD00_ENVIRONMENT_REPORT.md` và báo cáo bàn giao `docs/GD00_DELIVERY_REPORT.md`.

### Notes
- Không triển khai mã nguồn runtime GD01, không tạo production assets, không chỉnh sửa file gốc `GDD_Tu_Tien_Online_v0.1.md`.
