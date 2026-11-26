# GD01 SCOPE SPECIFICATION — PLATFORM FOUNDATION

**Phiên bản:** 1.0.0 (`GD00-FIX02`, giải quyết `HIGH-001`)  
**Nguồn thẩm quyền phạm vi giai đoạn:** `docs/ROADMAP.md` (Single Authority cho phân bổ phạm vi `GD00`–`GD20`).  
**Trạng thái:** Design Locked — **không triển khai mã nguồn GD01 trong GD00**.

---

## 1. Mục tiêu của GD01

Dựng bộ khung chạy thực tế tối thiểu và sạch kiến trúc cho cả 3 lớp của **LiveGame Studio** (Backend FastAPI, Desktop Shell PySide6, Frontend TypeScript/Vite/Three.js 9:16), đi kèm cấu hình bảo mật loopback cơ bản, kiểm thử tự động và script vận hành dev.

---

## 2. Phạm vi BẮT BUỘC trong GD01 (In-Scope Deliverables)

Chỉ bao gồm đúng 13 hạng mục sau:

| # | Hạng mục | Chi tiết triển khai được phép trong GD01 |
|---|---|---|
| 1 | **Environment bootstrap** | Khởi tạo `.venv` riêng cho dự án (`Python 3.11+`), khóa phụ thuộc (`pyproject.toml` / `requirements.txt`), khởi tạo `frontend/package.json` + `package-lock.json` |
| 2 | **Python environment** | Cài đặt tối thiểu `fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`, `PySide6`, `httpx`, `pytest` trong `.venv` (không phụ thuộc global site-packages) |
| 3 | **Application Core** | `core/app` — composition root, vòng đời khởi động/tắt sạch (`lifespan`), không để orphan process/handle |
| 4 | **Configuration** | `core/config` — nạp & kiểm định cấu hình bằng Pydantic v2 (file local + biến môi trường `LGS_*`), `SecretStr` bảo vệ giá trị nhạy cảm |
| 5 | **Logging** | `core/logging` — structured logging (JSONL xoay vòng + console UTF-8), tự động redact `token`/`secret`/`password`/`authorization`/`cookie`/`api_key` |
| 6 | **FastAPI Foundation** | `apps/backend` — bind mặc định `127.0.0.1`, `TrustedHostMiddleware`, restricted Origin policy (**cấm wildcard CORS `*`**), local admin session auth tối thiểu cho privileged endpoints |
| 7 | **Health endpoint** | `GET /api/v1/health` (công khai cục bộ trên loopback, chỉ trả trạng thái sống tối thiểu không nhạy cảm: `ok`, `status`, `version`, `db_smoke_ok`, `uptime_s`) |
| 8 | **SQLite smoke test** | Mở/tạo tệp SQLite cục bộ, áp dụng `PRAGMA journal_mode=WAL`, `PRAGMA foreign_keys=ON`, `PRAGMA busy_timeout=5000`, thực thi smoke read/write & persistence check cơ bản (**không triển khai full schema/Alembic**) |
| 9 | **PySide6 Desktop Shell** | `apps/desktop` — Main Window Dark Theme + Purple Accent, Tiếng Việt UTF-8, Sidebar điều hướng chuẩn với Dashboard, Settings cơ bản và các view placeholder được gắn nhãn rõ `Sắp ra mắt (GDxx)`, trạng thái Loading / Error / **Backend Unavailable**, thoát sạch |
| 10 | **TypeScript / Vite / Three.js Foundation** | `frontend/` — `tsconfig.json`, `vite.config.ts`, `Three.js` single `WebGLRenderer`, vòng lặp animation sạch và cơ chế `dispose()` khi unmount |
| 11 | **Procedural placeholder scene 9:16** | Khung dọc `9:16` (`1080×1920` logical aspect), scene hình học procedural tối giản (lưới/khối định hướng + camera + ánh sáng + resize handler), **không dùng production GLB** |
| 12 | **Automated tests** | `pytest` (health, config, logging redaction, SQLite smoke, security loopback/CORS/TrustedHost/auth boundary), `tsc --noEmit`, `vite build`, UI smoke test |
| 13 | **Development scripts** | `scripts/` — script bootstrap môi trường, khởi chạy Backend/Desktop/Frontend cục bộ và chạy bộ test kiểm chứng |

---

## 3. Phạm vi LOẠI TRỪ TUYỆT ĐỐI khỏi GD01 (Out-of-Scope & Target Phases)

Các hạng mục sau **KHÔNG ĐƯỢC triển khai trong GD01** và thuộc đúng giai đoạn đã chốt trong `docs/ROADMAP.md`:

| Hạng mục bị loại trừ khỏi GD01 | Giai đoạn triển khai chính thức |
|---|---|
| Toàn bộ 14 bảng Platform schema, Alembic migrations (`render_as_batch=True`), SQLite centralized write serializer & Application Services | **`GD02` – Database & Application Services** |
| Hoàn thiện khung 14 màn hình Desktop, WebSocket `/ws/admin` & Game Master controls đầy đủ | **`GD03` – Desktop Shell & Game Master UI** |
| Event Gateway, Event Bus, Event Simulator & Mock Event Provider | **`GD04` – Event Gateway & Simulator** |
| Game Plugin Engine (`Game Registry`, `Game Plugin Manager`, `Game Session Manager`) & **`cultivation_online` skeleton (`GAME001`)** | **`GD05` – Game Plugin Engine** |
| Command Parser (`commands.json`) & Rule Engine | **`GD06` – Command Parser & Rule Engine** |
| Asset Library, Asset Importer, Asset Validator, Asset Registry & Placeholder GLB packages | **`GD07` – Asset Library & Importer** |
| Snapshot/Delta WebSocket sync (`/ws/renderer`) & 9:16 Broadcast Overlay đầy đủ | **`GD08` – Three.js Runtime** |
| Meshy, Tripo, AI Asset Generator, Blender runtime, TikTok thật, Cloud, Payment, Production assets | **Cấm / Ngoài phạm vi MVP** |

---

## 4. Tiêu chí Nghiệm thu GD01 (Bao gồm Security Gate đầu tiên)

GD01 chỉ đạt `PASS` khi toàn bộ điều kiện sau được kiểm chứng thực tế:
1. **Functional:** Backend khởi chạy sạch trên `127.0.0.1`, `/api/v1/health` trả `200 OK`; SQLite smoke test chứng minh bật `WAL` + `foreign_keys=ON` và bền vững qua restart; PySide6 Desktop Shell chạy mượt không freeze, hiển thị đúng trạng thái `Backend Unavailable` khi tắt Backend, không hiển thị nút giả mạo cho tính năng GD02+; Three.js build sạch (`tsc --noEmit` + `vite build`), render scene procedural `9:16`, resize mượt, không lỗi console và gọi `dispose()` sạch.
2. **Security Acceptance Criteria (`HIGH-004` — GD01 Gate):**
   - Backend mặc định chỉ bind `127.0.0.1` (xác minh không lắng nghe `0.0.0.0`).
   - `TrustedHostMiddleware` chặn `Host` header không thuộc `127.0.0.1` / `localhost`.
   - Không tồn tại wildcard CORS (`Access-Control-Allow-Origin: *`).
   - `GET /api/v1/health` không lộ secret, đường dẫn tuyệt đối hệ thống hay stack trace.
   - Các endpoint đặc quyền (nếu đã tạo khung ở GD01, ví dụ kiểm tra admin ping/config read) yêu cầu Local Admin Session Token hợp lệ và trả `401/403` khi thiếu/sai token.
   - Structured logs chứng minh đã redact các khóa nhạy cảm (`token`, `secret`, `password`, `authorization`, `cookie`, `api_key`).
3. **Scope Hygiene:** Không có Alembic full schema (GD02), không có `games/cultivation_online/` runtime (GD05), không có Asset Library/Importer (GD07), không để orphan subprocess khi thoát ứng dụng.
