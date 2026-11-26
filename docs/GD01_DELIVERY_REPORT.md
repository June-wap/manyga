# GD01 — FOUNDATION DELIVERY REPORT

Ngày: 2026-11-26 (Asia/Saigon). **Overall status: PARTIAL** — implementation và kiểm thử GD01 đã hoàn tất; **independent Antigravity review: NOT RUN**, chưa chốt phase gate theo `TESTING_POLICY.md` mục 5. Không chuyển GD02.

**Addendum cùng ngày:** ADR-021 thay default paths sang `%LOCALAPPDATA%\LiveGameStudio` và chốt Standalone deployment. Kết quả 37 tests trong báo cáo này là baseline tại `2fa9fc7`, không phải kết quả chạy lại update. Xem [architecture update report](GD01_ARCHITECTURE_UPDATE_REPORT.md) cho changes, tests và review mới; giữ lịch sử bàn giao baseline.

## Baseline và Git

- Baseline: `592db8512de13fff24cd894b2468c328176e70b4` (`592db85`). Branch: `integration/gd01`, theo yêu cầu task.
- Đã kiểm tra git status/history trước triển khai; không ghi đè thay đổi người dùng, không tạo repo/worktree khác, không push/merge.
- GD00 final review đã được đọc thực tế trong phiên: reviewed commit `592db85`, `Final Decision: PASS`, `Gate Determination: READY_FOR_GD01`, 0 blockers GD01. Review có LOW nonblocking về recovery protocol dành cho GD05.
- Tệp `GD00_FINAL_REVIEW.md` xuất hiện ở trạng thái untracked trong lúc kiểm tra rồi không còn trên đĩa; Codex không sửa/xóa tệp đó. Chủ dự án đã xác nhận qua chat: **“Dùng kết luận PASS đã đọc; ghi rõ trong báo cáo”**. Báo cáo này ghi nhận quan sát và xác nhận đó, không thay thế review gốc.
- Implementation commit: `2fa9fc7b62a075f2e70f5eddb58e85ae271ace7a` (`2fa9fc7`). Documentation finalization commit là commit chứa bản báo cáo này, xác định bằng `git log -1 --format=%H -- docs/GD01_DELIVERY_REPORT.md`; hash được ghi trong phản hồi bàn giao. Các tài liệu GD00 và GDD giữ nguyên, ngoại trừ README, PROJECT_STATUS và CHANGELOG được cập nhật đúng deliverables.
- Sau commit implementation, các ảnh `.jfif` không thuộc task xuất hiện ở root. Giữ nguyên, không stage/commit/xóa. Vì vậy status toàn workspace có external untracked files; không gọi working tree hoàn toàn sạch. Commit GD01 chỉ chứa source, lockfiles, tài liệu và evidence được yêu cầu; không database/log/secret/build artifacts.

## Environment / dependencies

Windows 11 x64, i5-12450H, 15.73 GiB RAM, RTX 4050 Laptop 6141 MiB; Python 3.11.9, SQLite 3.45.1, Node 24.19.0, npm 11.17.0, Git 2.49.0.windows.1. Embedded preview thực tế nhận diện **Intel UHD / ANGLE Direct3D11**. Không có số liệu benchmark FPS, 100 players, OBS hoặc soak 4 giờ.

Xem [environment report](GD01_ENVIRONMENT_REPORT.md). Python packages cùng transitive versions pin trong `requirements.lock`, npm pin trong `frontend/package-lock.json`. `.venv` riêng, không global install. `pip check`, `npm ci`, setup idempotence và PowerShell 5.1 parsing đã chạy PASS.

## Files / implemented components

| Nhóm | Files tạo |
|---|---|
| Manifest/config | `pyproject.toml`, `requirements.lock`, `.env.example` |
| Core | `core/__init__.py`, `core/app/__init__.py`, `core/config/__init__.py`, `core/logging/__init__.py`, `core/security.py`, `core/sqlite_smoke.py` |
| Backend | `apps/__init__.py`, `apps/backend/__init__.py`, `apps/backend/main.py`, `apps/backend/__main__.py` |
| Desktop | `apps/desktop/__init__.py`, `apps/desktop/__main__.py`, `apps/desktop/supervisor.py`, `apps/desktop/window.py` |
| Frontend | `frontend/package.json`, `package-lock.json`, `tsconfig.json`, `vite.config.ts`, `playwright.config.ts`, `index.html`, `src/main.ts`, `src/runtime.ts`, `src/style.css`, `src/runtime.test.ts` |
| Scripts | `common.ps1`, `check_environment.ps1`, `setup_dev.ps1`, `start_backend.ps1`, `start_runtime.ps1`, `start_desktop.ps1`, `start_dev.ps1`, `stop_dev.ps1`, `run_tests.ps1`, `gui_smoke.py`, `verify_integration.py`, `verify_dev_scripts.py` trong `scripts/` |
| Tests | `tests/conftest.py`, `tests/backend/test_foundation.py`, `tests/ui/test_shell.py`, `tests/ui/test_forced_shutdown.py`, `tests/frontend/runtime.spec.ts` |
| Delivery | Hai báo cáo GD01; JSON evidence và bốn PNG thật trong `docs/evidence/gd01/`; README/PROJECT_STATUS/CHANGELOG cập nhật |

Core có version, environment detection/validation, project-relative path resolution độc lập CWD, startup/shutdown, rotating JSONL/console logs, UTF-8 và traceback đã redact. Không import `games` hoặc `apps` từ core.

Desktop chỉ lấy DB status qua health API; không mở SQLite. Dashboard không tạo player/session metrics giả. Game Library ghi GAME001 / Tu Tiên Online là danh mục dự kiến, chưa chơi được. Settings chỉ hiện cấu hình đang áp dụng; các trang tương lai ghi `Planned / Not implemented in GD01` và phase tương ứng. Live Studio chỉ mở Foundation Demo, không phải live session.

Supervisor dùng QProcess và Qt asynchronous HTTP polling, finite readiness deadline, retry/Backend Unavailable. Mặc định tự sở hữu backend và direct Node/Vite process; port conflict báo lỗi, không chiếm process khác. Backend nhận STOP/EOF qua private stdin pipe, không block GUI. Khi quá 5s, Windows fallback chỉ target `/PID <QProcess còn sống> /T`, không kill theo tên executable hoặc PID cache. Test thật chứng minh xóa cả grandchild của worker không phản hồi. Connect mode không sở hữu service bên ngoài. `stop_dev.ps1` yêu cầu UI close qua marker ngẫu nhiên, không terminate PID từ marker.

## API / security verification

| Kiểm tra đã thực thi | Status / evidence |
|---|---|
| Public `GET /api/v1/health` | PASS, HTTP 200, envelope chuẩn `ok/data/meta`; data chỉ có status/version/db_smoke_ok/uptime_s |
| Bind | PASS, inspect socket Windows thực tế thấy `127.0.0.1`; config từ chối non-loopback |
| Trusted Host | PASS, Host lạ / DNS-rebinding hostname bị 400 |
| Origin / CORS | PASS, allowlist local tường minh; Origin lạ/null bị 403; preflight local hoạt động; không wildcard |
| Session keys | PASS, hai `SecretStr` ngẫu nhiên `token_urlsafe(32)`, in-memory, constant-time admin comparator |
| Privileged boundary | PASS, `/dev/admin-ping` chỉ ở development; missing/invalid/renderer token bị 401, admin hợp lệ 200; test environment không đăng ký endpoint |
| Safe errors / input | PASS, 422/500 không echo secret/input/path/traceback; tests inject riêng route lỗi, không thêm production endpoint lỗi |
| Logs | PASS, JSONL timestamp/level/module, UTF-8, rotation, nested keys và traceback redact; raw runtime session secrets thay thế trước khi xuất |

GD01 chưa có privileged Desktop operations nên chưa cấp credential cho Desktop qua IPC, chưa có renderer stream/token URL, chưa có production REST CRUD hoặc WebSocket authentication. Credentials hiện chỉ bảo vệ foundation/dev boundary; không tuyên bố production auth đã hoàn tất. Uvicorn access logs tắt để tránh ghi URL chứa dữ liệu nhạy cảm. Không sửa API Contract: `/dev/admin-ping` được ghi rõ development-only, không là API ứng dụng production.

## SQLite verification

PASS trên file thật: create/open/close, SQLite 3.45.1, WAL, FK ON, busy_timeout 5000ms, commit UTF-8, explicit rollback, lỗi FK rollback nguyên transaction và reopen persistence. Hai bảng `foundation_smoke*` chỉ tồn tại trong smoke database riêng. Không ORM schema/repositories, migrations, production tables hoặc write coordinator GD02. Startup thất bại đóng logging resources sạch.

## Desktop / Three.js / integration verification

- PASS: Desktop hiển thị thực tế, điều hướng đủ 14 mục, health Connected, SQLite smoke status thật, Backend Unavailable khi dừng actual backend, đóng cửa sổ sạch.
- PASS: QWebEngine tải Vite local origin, WebGL 2.0 thực tế không workaround sandbox/GPU; scene camera/ambient/directional light/ground/geometric humanoid quay và chuyển động nhẹ.
- PASS: single WebGLRenderer, 9:16, browser framebuffer 1080×1920 đọc được nhiều màu thực tế, resize vẫn 9:16, animation thay đổi rotation, dispose dừng loop và GPU geometry count về 0. Browser tests kiểm tra cả WebGL unavailable và mất context thật.
- PASS: private backend control pipe graceful shutdown exit 0, Vite thoát, Windows process inventory không còn descendants đã theo dõi (kể cả real Python grandchild, QtWebEngineProcess và conhost); xem JSON evidence.
- PASS: user-facing PowerShell `start_dev.ps1` và `stop_dev.ps1`, desktop exit 0, không còn listeners của hai service sau shutdown.

Screenshot thực tế: [Dashboard](evidence/gd01/desktop-dashboard.png), [embedded preview](evidence/gd01/desktop-preview.png), [Backend Unavailable](evidence/gd01/desktop-offline.png), [browser 1080×1920](evidence/gd01/browser-preview.png).

Machine-readable: [embedded + descendant checks](evidence/gd01/embedded-smoke.json), [PowerShell flow](evidence/gd01/dev-script-smoke.json). Frame counter/draw-call count dùng để chứng minh loop/render hoạt động, không là FPS benchmark.

## Test commands và kết quả thực tế

Final combined command (Windows PowerShell 5.1):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run_tests.ps1 -Browser -Embedded
```

| Suite/check | PASS | FAIL | SKIP | NOT RUN | BLOCKED |
|---|---:|---:|---:|---:|---:|
| pytest backend/config/log/security/SQLite/UI/process | 31 | 0 | 0 | 0 | 0 |
| Vitest | 3 | 0 | 0 | 0 | 0 |
| Playwright real browser | 3 | 0 | 0 | 0 | 0 |
| Automated test total | **37** | **0** | **0** | **0** | **0** |
| Independent GD01 review (separate acceptance item) | 0 | 0 | 0 | **1** | 0 |

Ngoài test count: Ruff PASS, `tsc --noEmit` + `vite build` PASS, real GUI/integration 8 checks PASS, start/stop script smoke PASS, PowerShell syntax parse PASS, dependency checks/setup PASS. Không cộng các check này vào 37 test cases.

Các lệnh đã thực thi riêng: `setup_dev.ps1`, `check_environment.ps1`, `python -m pip check`, `python scripts/verify_integration.py`, `python scripts/verify_dev_scripts.py`, `npm run build`, `npm test`, `npm run test:e2e` và `npx playwright install chromium`.

Lịch sử debug không bị gọi PASS: iteration đầu có failure Qt closeEvent reentrant, một lần Qt abort khi teardown request đang pending, CLI import incompatibility Qt/Pydantic. Đã sửa deferred close, abort pending network replies khi stop và eager config import trước Qt hook; final combined run PASS. Script smoke ban đầu dùng HTTP timeout quá ngắn để kết luận socket đóng trên Windows; thay bằng kiểm tra Windows LISTEN sockets trực tiếp, không nới assertion service còn sống. Không xóa assertion hoặc test để che lỗi.

## Known issues / blockers / limits

- Không còn critical/high defect đã biết ảnh hưởng bộ kiểm tra GD01 cuối. Blocker môi trường: NONE; GUI và WebGL đều đã chạy.
- Independent review NOT RUN, vì vậy overall PARTIAL và phase gate chưa đóng. Không tự gọi kết quả Codex là review độc lập.
- Starlette phát một deprecation warning về TestClient HTTPX 0.28.1; bộ test vẫn PASS. Chưa cần thêm HTTPX2 ngoài dependency đã yêu cầu.
- Vite cảnh báo chunk khoảng 542 kB (Three.js); không lỗi build. Chưa tối ưu bundle hoặc benchmark foundation này.
- Khi cố ý gây WebGL context failure/loss, Three.js xuất diagnostic warning/error đúng kịch bản; normal render test không có unhandled page errors.
- Fresh-machine setup, OBS capture, hardware benchmark/soak, production packaging và crash-kill recovery toàn Desktop chưa kiểm chứng; ngoài acceptance smoke phiên này. Normal close, backend EOF và forced owned-worker cleanup có kiểm chứng.

## Out-of-scope verification

Không có runtime game trong `games/`, không 22-table schema/Alembic, full application services, plugin engine/player manager, scheduler/gameplay, asset importer/registry/production GLB, TikTok connector, OBS integration, Meshy/Tripo/AI assets hoặc Blender runtime. Không chỉnh GDD hay contract/ADR. Live TikTok, gameplay/production assets, WebSocket sync và GD19 benchmark **NOT RUN — thuộc giai đoạn sau**, không tính là GD01 tests và không được gọi PASS.

## Run / independent review handoff

```powershell
.\scripts\setup_dev.ps1 -WithBrowser
.\scripts\start_dev.ps1
# Mở Live Studio để xem procedural preview. Đóng cửa sổ hoặc từ terminal khác:
.\scripts\stop_dev.ps1
```

Antigravity cần review read-only implementation trên `integration/gd01`, diff từ `592db85`, rồi chạy lại `run_tests.ps1 -Browser -Embedded` trong phiên GUI Windows. Đối chiếu 13 deliverables GD01_SCOPE và ADR-017: host/origin/secret boundaries, development-only admin ping, startup import order, no DB access from Desktop, actual WebGL framebuffer/disposal, async polling và owned process trees/port conflicts. Kiểm tra ảnh và JSON evidence, thử external connect mode, config không hợp lệ và shutdown. Ghi findings/acceptance độc lập vào báo cáo GD01 review; không sửa đồng thời source đang bàn giao. Kiểm tra lại LOW recovery protocol của GD00 khi tới GD05, không mở scope GD01. Không merge/push nếu chưa có lệnh trực tiếp của chủ dự án.
