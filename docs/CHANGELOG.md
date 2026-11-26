# CHANGELOG — LIVEGAME STUDIO

Mọi thay đổi đáng chú ý của dự án được ghi nhận tại đây theo chuẩn [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
