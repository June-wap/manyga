# GD01-RC1 — Release Candidate & Review Evidence

Ngày thực thi: **2026-11-26**, Asia/Saigon. Đây là **Codex implementation self-audit**, không thay thế independent review.

| Status field | Kết quả |
|---|---|
| IMPLEMENTATION_STATUS | IMPLEMENTED — GD01 RC1 scope, hai lỗi logging phát hiện đã sửa |
| AUTOMATED_TEST_STATUS | PASS — 49 pytest + 3 Vitest + 5 Playwright = **57**, 0 FAIL / 0 SKIP trong final regression |
| INTEGRATION_TEST_STATUS | PASS — real backend/processes, GUI/QWebEngine, dev/static WebGL, shutdown và tracked-descendant cleanup |
| INDEPENDENT_REVIEW_STATUS | **BLOCKED** — Antigravity CLI headless command permission denial đã ghi nhận từ phiên trước; không retry trong RC1 |
| OVERALL_ACCEPTANCE_STATUS | **PARTIAL — READY_FOR_INDEPENDENT_REVIEW**, chưa GD01 Final Acceptance PASS |

## Repository / reviewed commit

- Workspace duy nhất: `D:\Tiktok Mini Game`; giữ branch `integration/gd01`, không branch/repo/worktree mới.
- Accepted GD00 baseline: `592db8512de13fff24cd894b2468c328176e70b4`. Git object/history đã kiểm tra. Final GD00 review từng được đọc PASS/READY_FOR_GD01 và chủ dự án cho phép dùng kết luận đó; file review chưa commit sau đó biến mất, không được tái tạo ở RC1. Đây là provenance đã được chủ dự án chấp thuận, không phải independent review mới trong phiên này.
- RC1 input baseline: `959bb3a44b2daa062acc2fbbe2000eb4e907de65`.
- **Reviewed and tested source commit: `f60bf4ac283e769ca5e79a441a8ee8298eddaabc` (`f60bf4a`).** Các thay đổi sau source commit để đóng gói RC1 chỉ là tài liệu/evidence. `commands.json` ghi đúng commit đang checkout khi chạy, runner kiểm tra manifest không đổi giữa đầu và cuối regression.
- Working tree đầu RC1: không có tracked modification, có **5 ảnh `.jfif` untracked** ngoài task; giữ nguyên, không stage/xóa. Vì vậy không gọi toàn bộ working tree sạch, dù tracked source và commit bàn giao sạch.
- Không push, không merge main. Không sửa GDD/contracts, không triển khai GD02.

## Source tree / audit coverage

Danh sách đầy đủ: [source-tree.txt](evidence/gd01/rc1/source-tree.txt). [source-manifest.json](evidence/gd01/rc1/source-manifest.json) lưu SHA-256 byte của working-tree files tại lúc chạy (line endings có thể khác checkout khác cấu hình Git).

```text
core/
  app/__init__.py          version, startup/shutdown, composition
  config/__init__.py       typed settings, LOCALAPPDATA, explicit local paths
  logging/__init__.py      rotating JSONL/console, redaction, Uvicorn handlers
  security.py             in-memory admin/renderer SecretStr credentials
  sqlite_smoke.py          isolated smoke DB, WAL/FK/transactions/reopen
apps/backend/
  main.py                 factory, safe responses, Host/Origin/admin boundary
  __main__.py             loopback Uvicorn, supervised STOP/EOF
apps/desktop/
  __init__.py              eager config import before Qt hook
  __main__.py              developer entrypoint and stop marker
  supervisor.py            QProcess ownership, asynchronous readiness/cleanup
  window.py                shell/navigation/status/QWebEngine preview
frontend/
  src/runtime.ts          single renderer, procedural scene, resize/disposal
  src/main.ts             mount/pagehide/HMR cleanup
  src/style.css           portrait viewport, Foundation Demo labels
  src/runtime.test.ts     aspect-fitting tests
  index.html              local resources only
  package*.json           pinned stack and dependency lock
  tsconfig.json           strict TypeScript
  vite.config.ts          loopback dev runtime
  playwright.config.ts    dev and static-build preview servers
scripts/
  *.ps1                   environment/setup/start/stop/tests
  gui_smoke.py            actual visible GUI/embedded evidence
  verify_integration.py   descendant shutdown verification
  verify_dev_scripts.py   actual PowerShell entrypoint/stop verification
  prepare_rc1_evidence.py recorded command outputs/exits/source provenance
tests/
  backend/                config/log/security/SQLite + RC1 real subprocesses
  ui/                     navigation/readiness/ownership/graceful/forced stop
  frontend/               actual browser WebGL and static production tests
```

Đã đọc các source trên, package initializers, PowerShell launch/setup helpers, dependency manifests/locks và tests. `core/` không import `apps/modules/games`; `modules/` và `games/` chỉ có baseline `.gitkeep`, chưa có production modules/plugin/schema. Desktop không mở kết nối DB: DB status đến từ health API. Frontend không chứa gameplay simulation hoặc admin operations.

## Audit findings và fixes

| ID / đánh giá Codex | Bằng chứng trước fix | Fix và retest |
|---|---|---|
| RC1-SEC-01 / HIGH: free-text header redaction thiếu phần giá trị | Hai test mới thực sự FAIL: `Authorization: Basic …` còn payload; Cookie nhiều cặp còn refresh value | Redact toàn bộ Authorization/Cookie/Set-Cookie header value tới newline, giữ nested-key/registered-secret redaction; tests PASS |
| RC1-SEC-02 / HIGH: Uvicorn re-log raw ASGI exception | Test actual Uvicorn/HTTP trả safe 500 nhưng console vẫn có fake registered credential trong traceback: thực sự FAIL | Đặt SafeFormatter với runtime-secret registration trên Uvicorn console handlers; actual-server test chứng minh cả response/console không chứa credential, shutdown exit 0 |
| RC1-EV-01 / evidence gap: prior browser tests chỉ dùng Vite dev server | Prior build PASS không chứng minh bản static đã render | Bổ sung actual browser test phục vụ `dist` bằng Vite preview, local-only requests, không `@vite/client`, screenshot/WebGL draw calls |
| RC1-EV-02 / evidence gap: chưa chứng minh Unicode CWD bằng backend process thật và external ownership | Prior tests dùng path configuration/temp DB và owned backend | Bổ sung subprocess từ Unicode/space CWD, A/B isolation + restart, CLI port conflict, actual HTTP rejects, Qt connect-mode không kill backend ngoài; forced-stop test có unrelated process sống nguyên |

Không xóa/nới assertion để che defect. Các lần FAIL trước fix không được tính PASS; final regression sau fix là 57/57. Test-only fault route ở subprocess fixture, không được thêm vào production API. Capture helper ban đầu dùng PIPE chưa drain bị HTTP timeout khi traceback đầy buffer; đã chuyển sang file tạm trong ignored runtime test directory để kiểm tra lỗi logging thực, không thay expected 500/redaction assertions.

Console ứng dụng cấu hình UTF-8 khi stream hỗ trợ. Không bật wildcard CORS, không tắt sandbox/web security, không thêm quyền Antigravity hoặc Windows execution-policy override. Script smoke hiện dùng policy Windows hiện có (CurrentUser RemoteSigned), không `ExecutionPolicy Bypass`.

## GD01_SCOPE acceptance mapping (13 deliverables)

| # | Deliverable | Implementation / evidence | Status |
|---|---|---|---|
| 1 | Environment bootstrap | `.venv`, Python lock, npm package lock; existing environment hoạt động, dependency check | PASS cho môi trường dev hiện có; fresh-PC setup NOT RUN RC1 |
| 2 | Python environment | `.venv` Python 3.11.9, pinned packages, `pip check` | PASS |
| 3 | Application Core | Lifespan startup/shutdown/failure cleanup, supervised EOF/STOP, process tests | PASS |
| 4 | Configuration | LOCALAPPDATA separation, local overrides, invalid values, Unicode roots/CWD/restart | PASS foundation |
| 5 | Logging | JSONL rotation/UTF-8/nested fields/header and Uvicorn redaction | PASS |
| 6 | FastAPI/security | Factory, loopback, TrustedHost, restricted Origin, dev admin ping auth | PASS foundation |
| 7 | Public health | HTTP 200, minimal `ok/data/meta`, exact non-sensitive data fields | PASS |
| 8 | SQLite smoke | Real file/WAL/FK/5000ms timeout/commit/rollback/reopen/A-B isolation | PASS smoke only |
| 9 | Desktop shell | 14 nav entries, planned labels, real status, actual visible window, unavailable/close | PASS shell |
| 10 | TS/Vite/Three.js | Typecheck/build/unit/browser tests, single renderer/disposal | PASS |
| 11 | Procedural 9:16 | Actual framebuffer/render, portrait resize, 1080×1920 browser, procedural geometry | PASS |
| 12 | Automated tests | 49 pytest + 3 Vitest + 5 Playwright | PASS |
| 13 | Dev scripts | User-facing start/stop, readiness, syntax/source audit, recorded command runner | PASS current Windows dev environment |

Các PASS ở bảng là implementation/testing evidence; **không đóng independent phase gate**. Không chạy installer/GD02 schema để thay thế smoke acceptance.

## Commands / exit codes / actual output

Entry command đã chạy:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_rc1_evidence.py
```

Runner exit **0**, không gọi Antigravity. Command arrays, working directories và exit code từng bước: [commands.json](evidence/gd01/rc1/commands.json). Frontend npm chạy bằng Node + npm CLI được resolve từ PATH, tương đương các `npm` commands sau.

| Command | Exit | Output / final result |
|---|---:|---|
| `python -m ruff check core apps scripts tests` | 0 | [ruff.txt](evidence/gd01/rc1/ruff.txt), All checks passed |
| `python -m pytest -q --basetemp=runtime/rc1-pytest --junitxml=runtime/rc1-pytest.xml` | 0 | [pytest.txt](evidence/gd01/rc1/pytest.txt), **49 passed**, 1 deprecation warning |
| `npm run typecheck` | 0 | [typecheck.txt](evidence/gd01/rc1/typecheck.txt), `tsc --noEmit` |
| `npm run build` | 0 | [production-build.txt](evidence/gd01/rc1/production-build.txt), Vite static dist built |
| `npm test` | 0 | [vitest.txt](evidence/gd01/rc1/vitest.txt), **3 passed** |
| `npm run test:e2e` | 0 | [playwright.txt](evidence/gd01/rc1/playwright.txt), **5 passed** |
| `python scripts/verify_integration.py` | 0 | [embedded-and-cleanup.txt](evidence/gd01/rc1/embedded-and-cleanup.txt), 8 GUI/socket/render/cleanup checks PASS |
| `python scripts/verify_dev_scripts.py` | 0 | [desktop-start-stop.txt](evidence/gd01/rc1/desktop-start-stop.txt), start/stop PASS, desktop exit 0, listeners empty |
| `python -m pip check` | 0 | [pip-check.txt](evidence/gd01/rc1/pip-check.txt), no broken requirements |

Final test counts: **57 PASS, 0 FAIL, 0 SKIP, 0 NOT RUN, 0 BLOCKED trong ba automated suites**. Independent review là một mục acceptance riêng bị BLOCKED, không cộng/trộn vào số test cases. Deferred tests GD02/GD19/GD20 liệt kê riêng phía dưới. Command outputs là capture thật sau fix, đã thay user-profile prefix bằng `<USERPROFILE>`; không phải runtime app logs hoặc output dựng lại. Raw temporary pytest XML/database/app logs không commit.

## API / security verification boundaries

| Item | Thực thi / kết quả |
|---|---|
| Loopback bind | Actual Windows LISTEN socket `127.0.0.1`, [embedded-smoke.json](evidence/gd01/rc1/embedded-smoke.json); Settings từ chối non-loopback |
| Trusted Host | TestClient + real backend HTTP Host lạ → 400 |
| Restricted Origin/CORS | TestClient + real backend Origin lạ/null → 403, no allow-origin wildcard; allowed local origin/preflight tested |
| Admin vs renderer | In-memory random separate SecretStr, constant-time comparator; TestClient admin success 200 vs renderer/missing/invalid 401 |
| Actual privileged HTTP rejects | Real dev `/dev/admin-ping` thiếu/sai token → 401. Chưa có Desktop privileged operations/secure IPC issuance; không nhận production admin integration PASS |
| Public health | Exact data keys `status/version/db_smoke_ok/uptime_s`, no credential, no internal path, no traceback; no admin token cần cho health |
| Safe errors/input | TestClient 422/500 safe response; actual Uvicorn 500 + console registered-secret redaction |
| Credential exposure | Health/log tests, app access logs disabled, no credentials in frontend URLs/resources; developer ping chỉ ở development |
| Process ownership | Qt owned tree only; actual unrelated worker vẫn sống sau forced cleanup. Connect mode external backend vẫn alive/healthy sau supervisor stop |

Các credential trong logging fault tests là dữ liệu giả, không phát hành token thật ra evidence. Chưa triển khai WebSocket, renderer token transport, full privileged REST CRUD, production settings hoặc asset endpoints. Không gọi các mục đó PASS.

## Standalone / portability / SQLite evidence

| Check | Kết quả / phạm vi |
|---|---|
| No mandatory Cloud Backend/DB/sync/global cloud players | PASS authored-source/dependency audit: không có cloud service hoặc global player schema/module; authored runtime HTTP URLs chỉ local; static resource test chỉ localhost. Dependency tải qua npm/pip là developer setup, không cloud runtime architecture |
| Developer-specific runtime paths | PASS source scan: không hardcode developer drive/profile; root resolve từ source/standard Windows user root. Evidence command paths là inventory của lần chạy, không hardcoded application config |
| Installation vs user data | PASS config default data/log/DB outside installation, explicit overrides và relocation resolver tests. Actual readonly installer NOT RUN |
| Development vs distribution | GD01 dùng Python/Node/Vite dev tooling + checkout `.env`/control markers. GD20 bundle/installed-resource resolution chưa implement; không gọi candidate này là installer |
| Space/Unicode working directory | PASS actual Python backend process khởi động từ temp directory tên có Unicode/dấu cách; code resolve qua explicit PYTHONPATH, không copy repository |
| Temp data directories / A-B isolation | PASS actual backend + real smoke files: row 42 chỉ DB A, DB B không có; không fake player tables |
| Restart same data | PASS shutdown backend A exit 0 rồi khởi động lại cùng data root, đọc lại committed row 42 |
| SQLite foundation | PASS WAL/FK/busy_timeout 5000ms, commit/rollback/foreign-key failure/reopen; chỉ hai bảng `foundation_smoke*` |
| Backend port conflict | PASS CLI process thứ hai exit nonzero như mong đợi; original owner vẫn running và health 200. Không kill owner |
| Optional GPU tool absent | PASS controlled absence của `nvidia-smi` trong child shell, environment script exit 0; không thay machine PATH/policy |
| Optional GPU debug extension absent | PASS controlled null `WEBGL_debug_renderer_info`, actual WebGL vẫn running/draw calls >0, diagnostic `unavailable` |
| Static production frontend | PASS actual dist resources, no Vite client/external requests, WebGL running/1080×1920/screenshot. Static build ≠ GD20 packaging |
| Graceful / forced cleanup | PASS private STOP/EOF backend exit 0, Vite/Qt helpers tracked exited, no listeners; forced worker/grandchild cleanup không ảnh hưởng unrelated process |

Tất cả chạy trên **một máy Windows**, không chứng minh multi-PC compatibility. User-root tests mô phỏng profile roots, không phải đăng nhập nhiều Windows users thật. Chưa kiểm thử mounted remote drive thực tế, toàn bộ cloud-sync providers/junctions hoặc actual installation relocation. Default/UNC validation tests không thay cho các acceptance đó.

## GUI / actual WebGL / cleanup artifacts

- [Desktop dashboard](evidence/gd01/rc1/desktop-dashboard.png), [embedded preview](evidence/gd01/rc1/desktop-preview.png), [Backend Unavailable](evidence/gd01/rc1/desktop-offline.png): actual QWidget grabs; đã inspect bằng mắt.
- [Browser 1080×1920](evidence/gd01/rc1/browser-preview.png), [static production WebGL](evidence/gd01/rc1/static-production.png): Playwright screenshots thật; static screenshot đã inspect bằng mắt.
- [embedded-smoke.json](evidence/gd01/rc1/embedded-smoke.json): actual WebGL 2.0 / ANGLE Intel UHD Direct3D11, 9:16 aspect, 8 draw calls ở snapshot, no special GPU/sandbox flags. Frame counter không phải FPS benchmark.
- Browser tests đọc framebuffer nhiều màu, rotation thay đổi, resize giữ tỷ lệ, geometry GPU memory về 0 sau dispose; loop không tăng frame sau dispose. Intentional WebGL unavailable/context-loss có error state và cleanup.
- JSON ghi exact PIDs/descendants, backend exit 0, `process_survivors: []`; [dev-script-smoke.json](evidence/gd01/rc1/dev-script-smoke.json) ghi `remaining_listeners: []`. Không suy từ QProcess parent exit rằng grandchild đã thoát mà không kiểm tra.

## Future asset requirements — tracking only, không GD01 implementation

| Requirement đã thống nhất | Phase mapping | Bằng chứng/acceptance cần ở phase tương ứng |
|---|---|---|
| External Blender asset production | External TT-AS + **GD07** import/validation | GLB/manifest/license/provenance/integrity/rig/LOD validation; Blender chỉ ở production pipeline ngoài ứng dụng, không Blender runtime |
| CharacterAssetCache | **GD07/GD08**, character integration **GD09** | Cache validated versions/resources; lifetime/disposal có ownership rõ; không loader/cache mới trong GD01 |
| CharacterFactory | **GD09**, dùng runtime GD08/cache GD07 | Factory tạo instance từ validated template, không hardcode game vào core |
| SkeletonUtils.clone / independent skeleton instances | **GD09** | Nhân bản skinned character để bones riêng; không dùng Object3D.clone thường làm bằng chứng skeleton độc lập |
| Shared geometry / shared textures | **GD08/GD09**, benchmark **GD19** | Reuse immutable resources; không dispose shared geometry/texture khi instance khác còn dùng |
| Texture variants | Asset metadata **GD07**, renderer **GD09**, local choice **GD11** | Variant IDs hợp lệ, per-instance material binding không mutate shared appearance của nhân vật khác |
| Modular character appearance | **GD07/GD09**, persistence **GD11** | Compatible modular parts/materials và fallback khi thiếu dependency; chưa production assets GD01 |
| Independent animation state | **GD09** | Skeleton/animation mixer/action state độc lập, test hai nhân vật chạy animation khác nhau |
| Dynamic LOD | Metadata **GD07**, runtime **GD09**, budgets **GD19** | LOD chuyển theo visibility/distance/budget và số đo, không giảm/xóa gameplay state |
| Local appearance persistence | **GD11**, asset references GD07/GD09 | Lưu trusted appearance/variant IDs theo local player/profile/plugin/world; reload/live mới giữ, không cloud sync |
| Multi-hardware resource/appearance/LOD validation | **GD19** | Đo 1/20/50/100 actors, CPU/GPU/RAM/VRAM, dispose/soak trên nhiều máy/presets; không bịa FPS từ RC1 |

Đây là tracker cho reviewer/handoff, không thay contract/GDD hoặc kéo implementation lên GD01. Các module trên **chưa triển khai**. No production character/map/rig/cache/factory được tạo ở RC1.

## Known limitations / deferred implementation

- **Independent review BLOCKED** như dưới; không có Final Acceptance PASS.
- Dev shell vẫn dùng checkout Vite/Node và control-marker directory, không phải installed readonly application. Production packaging/first run schema/default seed/migration/data-preserving upgrade: **NOT RUN**, thuộc GD02/GD20.
- Full gameplay progression, local appearance persistence/character assets/factory/LOD, renderer WS sync, TikTok LIVE/OBS: **NOT RUN**, chưa phase tương ứng.
- Multi-PC/multiple actual Windows profiles, GD19 performance/VRAM/soak/OBS: **NOT RUN**. Optional GPU absence tests là controlled scenarios, không certification mọi hardware.
- Mất WebGL context hiển thị lỗi/cleanup và yêu cầu reload; không có automatic context restoration. Runtime là foundation demo single-use, không production scene manager.
- Whole-Desktop crash-kill recovery chưa được chứng minh; normal close, backend control-pipe EOF/STOP và forced owned-worker cleanup có tests.
- Starlette TestClient HTTPX deprecation, Vite ~542 kB chunk warning, Playwright FORCE_COLOR/NO_COLOR warning; intentional context-failure tests xuất Three.js diagnostic. Không ảnh hưởng final exit 0, không được gọi performance optimization đã hoàn thành.
- Không phát hiện critical/high defect chưa xử lý trong self-audit và các scenarios đã chạy sau fix; độc lập review có thể tìm thêm vấn đề.

## Independent-review blocker / next action

Giữ blocker đã ghi tại `GD01_ARCHITECTURE_UPDATE_REPORT.md`: Antigravity CLI headless không thể prompt quyền `command`, tool auto-denied và không có review verdict. **RC1 không gọi lại agy/Antigravity, không chuyển agent, không đổi allow rules, không skip permissions và không sửa permission policy.**

Người phụ trách independent review cần review source `f60bf4a` + package này bằng workflow được cấp quyền chính thức, ghi report/verdict thật rồi mới xét GD01 gate. Review từ `592db85` cho full GD01, delta portability từ `959bb3a`/RC1 fixes theo lịch sử; không coi self-audit hoặc 57 tests là independent approval. GD02 vẫn NOT STARTED cho tới lệnh/gate phù hợp.
