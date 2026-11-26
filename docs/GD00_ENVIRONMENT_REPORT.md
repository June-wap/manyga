# GD00 ENVIRONMENT INSPECTION REPORT

**Ngày kiểm tra:** 2026-11-26  
**Workspace chính thức:** `D:\Tiktok Mini Game`  
**Phương pháp:** Kiểm tra trực tiếp bằng lệnh hệ thống trên máy chủ phát triển Windows thực tế.

---

## 1. Trạng thái Workspace & Git

| Hạng mục | Kết quả kiểm tra thực tế |
|---|---|
| Đường dẫn Workspace | `D:\Tiktok Mini Game` (tồn tại, là workspace duy nhất) |
| Trạng thái ban đầu trước GD00 | Có `.git` (remote `origin` trỏ `https://github.com/June-wap/manyga.git`, 0 commits) và tệp `GDD_Tu_Tien_Online_v0.1.md` (`31,380 bytes`, 274 dòng) |
| Git Version | `git version 2.49.0.windows.1` |
| Git User Config | `Basic <anhquang657@gmail.com>` |
| Branch GD00 | `design/gd00` (tạo mới, chưa push remote, chưa merge vào `main`) |

---

## 2. Hệ điều hành & Phần cứng (Host Hardware Baseline)

| Thành phần | Thông số đo được thực tế | Ghi chú cho GD01–GD20 |
|---|---|---|
| **OS** | Microsoft Windows 11 Home Single Language `10.0.26300` (64-bit) | Đáp ứng mục tiêu Windows Desktop 64-bit |
| **CPU** | 12th Gen Intel Core i5-12450H (`8 Cores / 12 Threads`) | Đủ cho FastAPI + PySide6 + Chromium/OBS dev |
| **RAM** | `15.73 GB` | Đủ dev; cần theo dõi RAM khi chạy đồng thời OBS + WebGL + IDE |
| **GPU rời** | NVIDIA GeForce RTX 4050 Laptop GPU (`~4 GB VRAM` reported `AdapterRAM`, driver `32.0.15.9159`) | Hỗ trợ WebGL2 tốt; **4 GB VRAM** là ràng buộc quan trọng cho texture 512–1024 và LOD ở GD19 |
| **GPU tích hợp** | Intel(R) UHD Graphics (`~2 GB`, driver `32.0.101.7082`) | Lưu ý Windows hybrid GPU: cần đảm bảo WebView/OBS dùng đúng GPU khi benchmark |
| **Ổ đĩa `D:\`** | Còn trống **`29.83 GB`** | Đủ cho GD00–GD05; cần giám sát dung lượng khi thêm `.venv`, `node_modules`, assets 3D và file ghi OBS |

---

## 3. Công cụ & Toolchain hiện có

| Công cụ | Phiên bản / Trạng thái | Đường dẫn / Ghi chú |
|---|---|---|
| **Python (PATH mặc định)** | `Python 3.11.9` (64-bit, MSC v.1938) | `C:\Users\GIGABUYTE\AppData\Local\Programs\Python\Python311\python.exe` — khớp yêu cầu Python 3.11+ |
| **Python Launcher (`py`)** | `3.13` (default launcher), `3.12`, `3.11` | Khuyến nghị chốt cố định `Python 3.11` hoặc `3.12` khi tạo `.venv` ở GD01 (tương thích PySide6 tốt nhất) |
| **pip / uv** | `pip 24.0` (Py 3.11), `uv` có sẵn | `C:\Users\GIGABUYTE\AppData\Local\Microsoft\WinGet\Links\uv.exe` (`poetry` không cài) |
| **SQLite (Python stdlib)** | `sqlite3` library `3.45.1` | Hỗ trợ đầy đủ WAL, FK, Partial Indexes, JSON1 (`sqlite3.exe` CLI rời chưa cài — không chặn vì dùng Python/SQLAlchemy) |
| **Node.js** | `v24.19.0` | `C:\Program Files\nodejs\node.exe` |
| **npm / pnpm** | `npm 11.17.0` (`pnpm` chưa cài) | Dùng `npm` chuẩn cho `frontend/` (TypeScript + Vite + Three.js) ở GD01 |

---

## 4. Trạng thái thư viện Python toàn cục (Tham khảo trước khi tạo `.venv` ở GD01)

| Thư viện | Trạng thái trên global Python 3.11 | Hành động dự kiến tại GD01 |
|---|---|---|
| `fastapi` | `0.110.2` (installed globally) | Cài phiên bản pin chuẩn trong `.venv` riêng của dự án |
| `uvicorn` | `0.29.0` (installed globally) | Cài trong `.venv` |
| `pydantic` | `2.14.4` (installed globally) | Cài trong `.venv` |
| `httpx` | `0.27.2` (installed globally) | Cài trong `.venv` |
| `websockets` | `17.4` (installed globally) | Cài trong `.venv` |
| `sqlalchemy` | `NOT_INSTALLED` | Bắt buộc cài `sqlalchemy>=2.0` trong `.venv` ở GD01/GD02 |
| `alembic` | `NOT_INSTALLED` | Bắt buộc cài `alembic` trong `.venv` ở GD02 |
| `PySide6` | `NOT_INSTALLED` | Bắt buộc cài `PySide6` (+ WebEngine nếu dùng nhúng) trong `.venv` ở GD01 |
| `pytest` | `NOT_INSTALLED` | Bắt buộc cài `pytest` + `pytest-asyncio` trong `.venv` ở GD01 |

---

## 5. Kết luận & Rủi ro môi trường

1. **Đủ điều kiện triển khai GD01:** Máy đã có sẵn Python 3.11/3.12, `uv`/`pip`, Node.js 24, `npm` 11, Git 2.49, SQLite 3.45.1 và GPU RTX 4050 Laptop.
2. **Bắt buộc dùng Virtual Environment (`.venv`) tại GD01:** Không dùng gói cài toàn cục tránh xung đột phiên bản; khóa dependency qua `pyproject.toml` / `requirements.txt` và `package-lock.json`.
3. **Lưu ý phần cứng khi tới GD19:** Dung lượng ổ `D:\` còn `29.83 GB` và VRAM RTX 4050 Laptop ~4 GB cần được theo dõi sát trong benchmark 100 nhân vật cùng OBS.
