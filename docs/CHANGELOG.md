# CHANGELOG — LIVEGAME STUDIO

Mọi thay đổi đáng chú ý của dự án được ghi nhận tại đây theo chuẩn [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
