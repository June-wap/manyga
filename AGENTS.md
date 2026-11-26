# AGENTS.md — Quy tắc phối hợp Codex & Antigravity

Tài liệu này là hiến chương kỹ thuật bắt buộc cho mọi agent (Codex, Antigravity) và kỹ sư tham gia phát triển **LiveGame Studio** tại workspace chính thức `D:\Tiktok Mini Game`.

---

## 1. Phạm vi & Phân công vai trò (Role Ownership)

| Agent | Phạm vi phụ trách chính | Quyền hạn mặc định |
|---|---|---|
| **Codex** | Architecture implementation, Python/FastAPI Backend, Core/Modules, SQLAlchemy/Alembic DB, Event Pipeline, Game Plugin Domain (`games/<plugin_id>/`), Integration & Backend Tests | Triển khai code backend/domain/integration trên branch riêng theo task được giao |
| **Antigravity** | Independent Architecture/Code/Security Review, PySide6 Desktop UI/UX, Three.js / TypeScript Frontend Renderer (theo từng task được giao), E2E Validation & Acceptance Verification | Review độc lập không sửa source thuộc phạm vi Codex khi ở chế độ Review; triển khai UI/Frontend khi được giao task cụ thể |

### Quy tắc sở hữu file (File Ownership Matrix)
Để tránh xung đột và ghi đè chéo, **tuyệt đối không sửa cùng một nhóm file đồng thời**:

- **Nhóm Backend / Domain (Codex sở hữu khi implement):** `core/`, `modules/`, `games/`, `apps/backend/`, `scripts/`, `tests/backend/`, `tests/games/`.
- **Nhóm UI / Renderer (Antigravity sở hữu khi implement UI/Render; chỉ đọc khi Review):** `apps/desktop/`, `frontend/`, `tests/ui/`, `tests/frontend/`.
- **Nhóm Contract & Tài liệu kiến trúc (`docs/platform/*.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`):** Chỉ thay đổi qua đề xuất rõ ràng, cập nhật ADR trong `docs/DECISIONS.md` và `docs/CHANGELOG.md` trước hoặc cùng commit thay đổi contract.
- **Nhóm GDD chính thức (`docs/games/cultivation_online/GDD.md`):** Nguồn sự thật duy nhất (Single Source of Truth) cho luật gameplay GAME001. **Không tự ý ghi đè** khi chưa có phê duyệt từ chủ dự án; mọi sửa đổi phải ghi rõ Revision History và ADR liên quan.

---

## 2. Nguyên tắc bất di bất dịch (Non-Negotiable Constraints)

Mọi agent phải tuân thủ tuyệt đối các giới hạn sau:

1. **Workspace duy nhất:** Chỉ làm việc trong `D:\Tiktok Mini Game`. Không tạo `D:\LiveGameStudio` hay repo trùng lặp.
2. **Không tự ý đổi Technology Stack:**
   - Windows Desktop, Local-first, Modular Monolith.
   - Backend: Python 3.11+, FastAPI, SQLite, SQLAlchemy 2.x, Alembic, Pydantic v2, REST + WebSocket.
   - Desktop UI: PySide6.
   - Frontend Renderer: TypeScript + Vite + Three.js (3D) và Phaser.js (2D trong tương lai).
3. **Không tự ý mở rộng Scope:** Chỉ thực hiện đúng deliverables của giai đoạn `GDxx` hoặc task `TT-GDxx` đang được giao. Không làm trước giai đoạn sau.
4. **Không tích hợp AI Asset / Blender runtime:**
   - Không tích hợp Meshy API, Tripo API, AI Asset Generator hoặc Blender runtime trong ứng dụng.
   - Không tự tạo production 3D assets trong giai đoạn nền tảng; chỉ dùng placeholder hợp lệ theo `docs/platform/ASSET_CONTRACT.md`.
5. **Tuân thủ pháp lý & TikTok:**
   - Không triển khai kết nối TikTok trái phép, scraping lậu hoặc thu thập credential không được cấp quyền.
   - Không biến quà tặng trả phí (TikTok Gift) thành cơ chế đặt cược, gacha trả tiền, pay-to-win hoặc tăng xác suất đột phá/chiến đấu.
6. **Phân tách Platform vs Game Plugin:**
   - `core/` và `modules/` **tuyệt đối không import** từ `games/*`.
   - `games/cultivation_online/` chỉ gọi Platform qua contract (`GamePlugin`, Application Services, Event/Camera/Overlay/Asset interfaces).

---

## 3. Quy trình Git & Branching

- Mỗi giai đoạn hoặc task chạy trên branch/worktree tách biệt theo quy ước:
  - Thiết kế: `design/gd00`
  - Giai đoạn Platform: `feat/gd01-foundation`, `feat/gd02-database`, ...
  - Task game: `feat/tt-gd01-skeleton`, ...
  - Sửa lỗi review: `fix/gd01-r1-...`
- **Không tự ý `git push` lên remote** và **không tự ý merge vào `main`** khi chưa có lệnh xác nhận trực tiếp từ người dùng.
- Không commit file nhạy cảm hoặc sinh ra lúc runtime: `.env`, secrets, tokens, `*.db`/`*.sqlite`, `node_modules/`, `.venv/`, `*.blend`, build artifacts.

---

## 4. Chính sách thay đổi Contract (Contract Governance)

Các tài liệu sau là **Nguồn sự thật kỹ thuật (Single Source of Truth)**:
- `docs/platform/API_CONTRACT.md`
- `docs/platform/EVENT_CONTRACT.md`
- `docs/platform/GAME_PLUGIN_CONTRACT.md`
- `docs/platform/ASSET_CONTRACT.md`
- `docs/platform/DATABASE_DESIGN.md`

Quy trình khi cần thay đổi bất kỳ contract nào:
1. Ghi nhận lý do và đánh giá tác động (breaking vs non-breaking) trong `docs/DECISIONS.md` (tạo ADR mới).
2. Cập nhật tài liệu contract tương ứng và tăng version schema nếu có breaking change.
3. Ghi nhận vào `docs/CHANGELOG.md`.
4. Yêu cầu agent còn lại review đối chiếu trước khi chốt.

---

## 5. Chính sách trung thực về Kiểm thử & Báo cáo (Testing Truth Policy)

- **Tuyệt đối không ghi nhận test chưa chạy là `PASS`.**
- Mọi báo cáo bàn giao và review phải phân biệt rạch ròi 5 trạng thái:
  - `PASS` — Đã thực thi thực tế và đạt tiêu chí.
  - `FAIL` — Đã thực thi thực tế và thất bại.
  - `SKIP` — Có lý do bỏ qua tường minh (ghi rõ nguyên nhân).
  - `NOT RUN` — Chưa chạy trong phiên này.
  - `BLOCKED` — Bị chặn bởi phụ thuộc bên ngoài / môi trường / quyền truy cập.
- Simulator `PASS` **không đồng nghĩa** Live TikTok `PASS`.
- Không sửa test hoặc xóa assertion để che giấu lỗi thật.
- Không khẳng định hiệu năng (FPS, 100 players, VRAM) nếu chưa có số đo benchmark thực tế kèm cấu hình phần cứng.

---

## 6. Định dạng bàn giao tiêu chuẩn

Mỗi task hoàn tất phải có:
1. Commit sạch trên branch đúng quy ước (không file rác, không secret).
2. Báo cáo bàn giao (`docs/GDxx_DELIVERY_REPORT.md` hoặc `docs/games/<plugin>/TT-GDxx_DELIVERY_REPORT.md`) nêu rõ thay đổi, kết quả test thực tế, known issues và trạng thái acceptance (`PASS` / `PARTIAL` / `FAIL` / `BLOCKED`).
3. Cập nhật `docs/PROJECT_STATUS.md` và `docs/CHANGELOG.md`.
