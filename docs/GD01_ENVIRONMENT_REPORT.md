# GD01 ENVIRONMENT REPORT

Ngày kiểm chứng: 2026-11-26 (Asia/Saigon). Workspace: `D:\Tiktok Mini Game`.

| Hạng mục | Đã đo trực tiếp |
|---|---|
| OS | Microsoft Windows 11 Home Single Language, 64-bit |
| CPU | 12th Gen Intel Core i5-12450H |
| RAM tổng | 16,491,000 KiB, khoảng 15.73 GiB (Win32_OperatingSystem) |
| GPU rời | NVIDIA GeForce RTX 4050 Laptop GPU |
| Tổng VRAM GPU rời | 6141 MiB, NVIDIA driver 591.59 |
| GPU thực sự dùng cho embedded preview | ANGLE Intel UHD Graphics, Direct3D11, lấy từ WebGL debug renderer info |
| Python | 3.11.9, `.venv` riêng, không global site-packages |
| SQLite | 3.45.1 (Python sqlite3) |
| Node / npm | 24.19.0 / 11.17.0 |
| Git | 2.49.0.windows.1 |
| D: trống tại lần đo | 31,087,792,128 bytes, khoảng 28.95 GiB; thay đổi theo thời điểm |
| PowerShell chạy script | Windows PowerShell 5.1, không yêu cầu administrator |

Đây là inventory và capability smoke, không phải benchmark. Không đo FPS, 100 players, VRAM sử dụng, OBS hoặc soak 4 giờ. Không suy từ GPU NVIDIA hiện diện rằng preview chạy trên NVIDIA: kết quả embedded thực tế dùng Intel.

Các dependency chính đã cài và chạy kiểm thử: FastAPI 0.165.0, Uvicorn 0.54.0, Pydantic 2.14.4, pydantic-settings 2.16.3, SQLAlchemy 2.1.9, PySide6 6.12.0, HTTPX 0.28.1, pytest 9.2.0, pytest-qt 4.5.0, Ruff 0.17.6. Danh sách Python transitive đầy đủ được pin trong `requirements.lock`; `pip check` PASS.

Frontend: TypeScript 7.0.2, Vite 8.3.8, Three.js/@types/three 0.187.0, Vitest 5.1.2, Playwright 1.65.1. `npm ci` đã chạy lại thành công; npm audit khi cài báo 0 vulnerabilities. Chromium 159.0.8154.6 được Playwright cài qua cache browser tiêu chuẩn; không phải dependency runtime của ứng dụng.

`setup_dev.ps1` đã chạy lại sau bootstrap, xác minh idempotent trên môi trường hiện có. Chưa kiểm chứng bootstrap trên một máy Windows sạch khác. Không cài package ứng dụng toàn hệ thống.

Embedded QWebEngine đã chạy với WebGL 2.0, không bật cờ GPU đặc biệt, không tắt sandbox hay web security. Bằng chứng: [embedded smoke](evidence/gd01/embedded-smoke.json), [Desktop preview](evidence/gd01/desktop-preview.png), [browser 1080×1920](evidence/gd01/browser-preview.png).
