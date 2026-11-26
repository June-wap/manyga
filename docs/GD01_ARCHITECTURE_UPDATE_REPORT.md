# GD01 — Standalone Architecture Update

Ngày: 2026-11-26 (Asia/Saigon). Branch: `integration/gd01`. Baseline trước update: `c74a1eab4e35380cf0f0137a143889857d5adea7`.

**Overall: PARTIAL — changes implemented and verified; independent contract review BLOCKED.** Quyết định deployment của chủ dự án đã ghi Accepted tại ADR-021. Chưa chốt independent architecture/contract review hoặc full GD01 acceptance. Không restart GD00, không bắt đầu GD02.

## Quyết định và tài liệu

Đã cập nhật đủ 11 file được yêu cầu: AGENTS.md, README.md, PROJECT_SPEC.md, ARCHITECTURE.md, ROADMAP.md, DECISIONS.md, PROJECT_STATUS.md, TDD.md, DATABASE_DESIGN.md, GD01_SCOPE.md, TESTING_POLICY.md; thêm CHANGELOG và addendum vào GD01_DELIVERY_REPORT. ADR-001–020 giữ nguyên lịch sử, ADR-021 supersede mọi Hybrid Cloud proposal trước đây. DATABASE_DESIGN 1.0.1 chỉ là documentation clarification, không đổi tables/API/event/gameplay schema.

Kiểm tra repository không tìm thấy DEPLOYMENT_STRATEGY.md, PORTABILITY_REQUIREMENTS.md hoặc FUTURE_CLOUD_ARCHITECTURE.md; không tạo bản Cloud design mới. Roadmap vẫn **21 phase, GD00–GD20**. Ownership Codex/Antigravity, technology stack và GDD giữ nguyên. SHA-256 GDD vẫn `9AE22943227E2096B6FCF82F5E983DAEDE7CD6A498437854512D75737680E2AB`.

Thiết kế đã đồng bộ:

- Mỗi Windows PC/user có SQLite/world độc lập. TikTok identity chỉ map trong local DB rồi vào profile theo plugin/world; không cloud identity/restore/replication. Viewer trên DB mới bắt đầu mới; live session mới trên cùng DB không reset progression.
- GD02 first-run schema version + defaults/application/game configs/trusted built-in metadata; zero viewer/player/characters/progression/inventory/reward/session/leaderboard/test accounts. Existing DB compatibility check + data-preserving migrations; lỗi/incompatible version giữ DB, không reset/copy đè sample.
- Installation readonly tách user data/DB/config/assets/cache/logs. Không DB trong Program Files/network share/cloud-sync folder. Không hardware fingerprint hoặc cross-device import/backup requirement.
- GD20 installer bundle Python/PySide6/frontend production resources. End user không phải cài developer tools; không developer DB/.env/credentials/test accounts trong installer. Không Cloud Backend/DB/Save/Auth/Analytics/subscription, Cloud Catalog/Remote Download Server hoặc GD21–GD26.
- Trusted local game management giữ static allowlist ADR-010. Future trusted package cần integrity/manifest/version/compatibility/required assets validation, không arbitrary-code plugin loader. Reset một game là deferred design với confirmation/audit, giữ game khác/settings ngoài scope/production assets.
- Multi-hardware/non-NVIDIA, graphics presets/LOD/texture quality/visibility budgets/WebGL capability và fallback; benchmark đa máy GD19, không nhận một máy PASS đại diện mọi cấu hình.

## Foundation implementation trong GD01

`core/config/__init__.py` dùng writable default `%LOCALAPPDATA%\LiveGameStudio`; fallback Windows home/AppData/Local khi biến môi trường vắng, không hardcode user/drive. `installation_dir` vẫn là checkout root ở developer GD01; bundled resource resolution GD20 chưa implement.

Các path tách biệt: `database/smoke.sqlite3`, `config/`, `assets/`, `cache/`, `logs/`. Override `LGS_DATA_DIR` đổi root; path overrides riêng `LGS_DB_PATH/LOG_DIR/CONFIG_DIR/ASSET_DIR/CACHE_DIR` còn hỗ trợ local dev/tests, relative explicit overrides resolve từ checkout độc lập CWD. `.env.example` không ép data/logs về repo nữa. `.env` hiện hữu với explicit paths vẫn có hiệu lực; không tự sửa `.env` người dùng.

Default-path switch không di chuyển/import/xóa DB smoke cũ; DB dev cũ giữ nguyên trên đĩa. GD01 chưa có production player data hay production schema cần migration. Chỉ default smoke path đổi, không có code reset dữ liệu theo app version. Không tạo production initialization, Alembic, seed games/players hoặc installer.

UNC paths bị từ chối trước resolve; Windows native GetDriveTypeW từ chối mapped remote drive. Không tuyên bố đã nhận diện mọi cloud-sync provider/junction hoặc thực thi đầy đủ production storage policy: đây là trách nhiệm validation GD02/packaging GD20. Không có mounted remote drive để kiểm thử end-to-end trong phiên; direct UNC rejection đã test.

## Kiểm thử thực tế

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run_tests.ps1 -Browser -Embedded
```

| Suite/check | Trạng thái | Kết quả đã chạy trong phiên update |
|---|---|---|
| pytest | PASS | 41 tests, 0 fail, 0 skip |
| Vitest | PASS | 3 tests |
| Playwright | PASS | 3 tests, actual WebGL/framebuffer/resize/disposal/error cases |
| Automated total | PASS | **47 PASS / 0 FAIL / 0 SKIP / 0 NOT RUN / 0 BLOCKED** test cases |
| Ruff / TypeScript / Vite build | PASS | Combined script exit 0 |
| Real Desktop/QWebEngine + process shutdown | PASS | Embedded WebGL 2.0, ANGLE Intel UHD, real backend unavailable, all tracked descendants exited |
| PowerShell start/stop flow | PASS | Desktop exit 0, no remaining service listeners |
| Documentation cross-check | PASS | 11 required docs updated + ADR-021; roadmap 21 phases, GDD checksum unchanged; local links verified before commit |

Mười test cases mới trong `tests/backend/test_portable_paths.py` kiểm tra: hai user roots Unicode dùng DB smoke thật độc lập, reopen không xóa dòng riêng A; installation-root relocation không đổi default user DB; layout config/assets/cache/logs/DB riêng và config resolution không tạo directories; 6 path fields reject UNC; relative LOCALAPPDATA lỗi rõ. Test default config cũ cập nhật theo quyết định user-local mới, vẫn kiểm tra relative explicit dev overrides.

Evidence GUI/browser được cập nhật từ lần regression hiện tại: [embedded-smoke.json](evidence/gd01/embedded-smoke.json), [dev-script-smoke.json](evidence/gd01/dev-script-smoke.json), [Desktop preview](evidence/gd01/desktop-preview.png), [browser preview](evidence/gd01/browser-preview.png). Không coi frame counter/draw calls là FPS benchmark.

## Deferred acceptance / truthful limits

| Hạng mục | Status phiên này | Phase thực hiện |
|---|---|---|
| Production first-run schema/default seeds/zero players | NOT RUN — chưa implement | GD02 |
| Production migrations/compatible update không mất dữ liệu | NOT RUN — chưa implement | GD02 và gameplay phases |
| Same-player progression qua live mới/Windows restart | NOT RUN — chưa có gameplay | GD11–GD19 |
| Actual nhiều Windows user accounts / nhiều máy | NOT RUN — tests hiện chỉ dùng temp user roots mô phỏng | GD19/GD20 |
| Installer không dev DB/tools/.env/credentials, readonly install/relocation/update | NOT RUN — chưa có installer | GD20 |
| Graphics presets/đa GPU/non-NVIDIA benchmark | NOT RUN — không suy từ một Intel embedded smoke | GD09/GD19 |
| Actual mapped remote volume / mọi cloud-sync folder detection | NOT RUN — không có share mount / production guard chưa implement | GD02/GD20 |
| Independent review của delta này | BLOCKED — xem dưới | GD01 governance |

Các mục deferred không cộng vào 47 automated tests và không được nhận PASS chỉ từ documentation/unit tests. Known warning giữ nguyên baseline: Starlette TestClient HTTPX deprecation, Vite Three.js chunk >500kB; build/tests vẫn pass. Không thay GDD, schema hoặc production gameplay để né phase gates.

## Independent Antigravity review attempt

Theo AGENTS.md mục 4, đã yêu cầu Antigravity review read-only delta architecture/database contract bằng skill `agy-subagent-runner`. `agy --version` chạy thành công: 1.3.3. Một conversation mới được gọi với sandbox, Attached mode, không skip permissions, timeout 480s, scope không edit/commit/run GUI. CLI trả:

> jetski: no output produced — a tool required the "command" permission that headless mode cannot prompt for, so it was auto-denied.

Đây là lỗi quyền CLI headless, **không phải review PASS** (dù native process trả exit 0). Không có findings/verdict độc lập. Attached call không tạo log file tại runtime directory đã chỉ định; nội dung denial được quan sát trực tiếp trong tool output và ghi nguyên excerpt ở đây. Kiểm tra diff không thấy sửa source của Antigravity.

Skill yêu cầu dừng execution branch khi không có response, không tự retry/switch agent. Vì vậy contract review để **BLOCKED**, không bật auto-approval hoặc đổi agent để nhận kết quả. Cần cấu hình quyền read-only command được cho phép cho Antigravity hoặc thực hiện review tương tác chính thức rồi review lại diff hiện tại. Không cần dừng việc hoàn thiện GD01 foundation/documents; chưa đóng contract acceptance gate.

## Git / handoff

Thay đổi trên branch GD01 hiện tại theo yêu cầu; không push/merge, không repo/worktree khác. Commit chỉ gồm source config/tests, architecture/docs và execution evidence. Giữ nguyên ba ảnh `.jfif` untracked có từ trước task; không stage/xóa. Dữ liệu runtime/logs/.env/dependencies không commit.

Commit implementation và documentation sẽ ghi trong phản hồi bàn giao; dùng `git log --oneline c74a1ea..integration/gd01` để xác định chuỗi commit update. Reviewer so sánh delta với `c74a1ea`, đọc ADR-021 và phase matrix, chạy lại combined command nếu có Windows GUI. Không tự đóng review toàn GD01 chỉ từ review architecture delta này.
