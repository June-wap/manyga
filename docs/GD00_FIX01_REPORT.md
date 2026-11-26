# GD00-FIX01 REPORT — RESOLVE OPEN DESIGN DECISIONS

**Ngày thực hiện:** 2026-11-26  
**Workspace chính thức:** `D:\Tiktok Mini Game`  
**Git Branch:** `design/gd00` *(không push remote, không merge vào `main`, không triển khai GD01)*  
**Baseline Commit:** `be4d84d` (`be4d84d1e1d6aa2a22a5820074166e0c5c41bd8a`)  
**Fix Implementation Commit:** `fda1b1a` (`fda1b1af7d9b7a8e367117558e24040a3303d2b3`)  
**Trạng thái:** **`PASS` (Sẵn sàng cho Antigravity Independent Review)**

---

## 1. Các quyết định đã được giải quyết (Resolved Decisions)

| ID | Nội dung | Trạng thái | Ghi nhận chính thức |
|---|---|---|---|
| **ADR-007 / CONF-03 / OPEN-04** | Chuyển GDD gốc từ root sang `docs/games/cultivation_online/GDD.md`, xác minh toàn vẹn SHA-256, loại bỏ tình trạng tồn tại hai nguồn GDD và đồng bộ toàn bộ tham chiếu trong repo | **`RESOLVED`** | `docs/DECISIONS.md` (`ADR-007`), `docs/games/cultivation_online/GDD.md` là Single Source of Truth duy nhất |
| **CONF-04 / OPEN-05 / ADR-015** | Chuẩn hóa bộ lệnh hộ thể MVP: `!hothe`, `!hotheauto`, `!hotheauto on`, `!hotheauto off`; hộ thể tự động mặc định bật, GM cấu hình được mặc định, tính theo server-side event timing hỗ trợ độ trễ livestream, không đòi hỏi phản ứng animation và không dùng quà trả phí tăng xác suất độ kiếp; giữ nguyên thông số cân bằng gốc v0.1.0 | **`RESOLVED`** | `docs/games/cultivation_online/GDD.md` (Amendment `v0.1.1`), `ADR-015`, `EVENT_CONTRACT.md`, `GAME_PLUGIN_CONTRACT.md`, `DATABASE_DESIGN.md`, `TESTING_POLICY.md`, `ROADMAP.md` |
| **TASK 04 (Hardware Verification)** | Xác minh phần cứng thực tế bằng `nvidia-smi` và lệnh hệ thống; khắc phục sai số WMI 32-bit 4 GB, phân biệt rõ Tổng VRAM (`6141 MiB`) với VRAM khả dụng (`5820 MiB`) và Tổng RAM (`15.73 GB`) với RAM khả dụng (`3.14 GB`) | **`RESOLVED`** | `docs/GD00_ENVIRONMENT_REPORT.md` |
| **TASK 05 (Performance Targets)** | Bổ sung đầy đủ mục tiêu benchmark MVP (`1080×1920`, `30 FPS`, `100` players, single `WebGLRenderer`, max `1` PiP, LOD, resource disposal, **4-hour continuous session test**, **CPU/RAM/GPU/VRAM monitoring**) và ghi rõ là mục tiêu kiểm thử, chưa phải kết quả đo | **`RESOLVED`** | `docs/PROJECT_SPEC.md`, `docs/platform/TDD.md`, `docs/platform/TESTING_POLICY.md`, `docs/ROADMAP.md` |

---

## 2. Danh sách File thay đổi (Files Changed)

*(Đối chiếu trực tiếp từ `git diff --name-status be4d84d..fda1b1a` cộng thêm báo cáo này)*

| Trạng thái | Đường dẫn file | Mục đích thay đổi |
|---|---|---|
| `R093` | `GDD_Tu_Tien_Online_v0.1.md` → `docs/games/cultivation_online/GDD.md` | Di chuyển bằng `git mv` (xác minh SHA-256 100% nguyên vẹn trước khi sửa), sau đó áp dụng Amendment `v0.1.1` |
| `M` | `AGENTS.md` | Cập nhật nguồn GDD duy nhất `docs/games/cultivation_online/GDD.md` |
| `M` | `README.md` | Cập nhật sơ đồ thư mục và liên kết trực tiếp tới `docs/games/cultivation_online/GDD.md` + `docs/GD00_FIX01_REPORT.md` |
| `M` | `docs/PROJECT_SPEC.md` | Cập nhật tham chiếu GDD và bổ sung bảng mục tiêu benchmark + 4-hour soak test |
| `M` | `docs/DECISIONS.md` | Chốt `ADR-007` (`Accepted & Resolved`) và bổ sung `ADR-015` (lệnh `!hotheauto` & server-side timing) |
| `M` | `docs/PROJECT_STATUS.md` | Đóng `OPEN-04`, `OPEN-05`; cập nhật thông số VRAM thật (`6141 MiB` / `5820 MiB`) và RAM khả dụng |
| `M` | `docs/CHANGELOG.md` | Bổ sung mục `[0.0.2-gd00-fix01]` |
| `M` | `docs/ROADMAP.md` | Cập nhật phạm vi & test lệnh `!hotheauto` ở `GD06`/`GD14` và mục tiêu benchmark + soak test 4 giờ ở `GD19` |
| `M` | `docs/GD00_ENVIRONMENT_REPORT.md` | Ghi nhận kết quả `nvidia-smi`, phân biệt Total vs Available VRAM/RAM, Disk `D:\` & `C:\` |
| `M` | `docs/GD00_DELIVERY_REPORT.md` | Đánh dấu đã giải quyết `ADR-007` và `CONF-04`/`OPEN-05`, trỏ sang `GD00_FIX01_REPORT.md` |
| `M` | `docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md` | Đóng `CONF-03`, `CONF-04`; cập nhật lệnh hộ thể tự động, server-side timing và thông số VRAM thực tế |
| `M` | `docs/platform/TDD.md` | Bổ sung Mục 7.1 về Mục tiêu Benchmark MVP (bao gồm 4-hour continuous session test & CPU/RAM/GPU/VRAM monitoring) |
| `M` | `docs/platform/EVENT_CONTRACT.md` | Cập nhật đường dẫn `GDD.md`, thêm cooldown `!hotheauto`/`on`/`off` (5s) và nhấn mạnh server-side `SimulationClock` |
| `M` | `docs/platform/GAME_PLUGIN_CONTRACT.md` | Bổ sung hỗ trợ subcommand tường minh và server-side event timing trong `handle_command()` |
| `M` | `docs/platform/DATABASE_DESIGN.md` | Cập nhật tham chiếu `GDD.md` và thêm cột `auto_guard_enabled` (`DEFAULT 1`) vào `g_cultivation_characters` |
| `M` | `docs/platform/MODULE_DESIGN.md` | Cập nhật test strategy của `Command Parser` bao phủ đầy đủ `!hothe`, `!hotheauto`, `!hotheauto on`, `!hotheauto off` |
| `M` | `docs/platform/TESTING_POLICY.md` | Cập nhật tham chiếu `GDD.md`, mở rộng `AC06` (hộ thể tự động) và `AC15` (4-hour soak test + CPU/RAM/GPU/VRAM) |
| `A` | `docs/GD00_FIX01_REPORT.md` | Báo cáo bàn giao `GD00-FIX01` này |

---

## 3. Bằng chứng toàn vẹn Checksum GDD (Original & Relocated SHA-256)

Quy trình di chuyển được thực hiện bằng `git mv` trước mọi chỉnh sửa:

| Giai đoạn | Đường dẫn | Kích thước | SHA-256 | Kết quả |
|---|---|---|---|---|
| **Trước di chuyển (Baseline v0.1.0)** | `GDD_Tu_Tien_Online_v0.1.md` | `31,380 bytes` | `0A4F9D8B3D2005D0947A7C48E85F87D6B143ECC851DEB0E6345D27B2FF4AE534` | Baseline |
| **Ngay sau `git mv` (Chưa sửa)** | `docs/games/cultivation_online/GDD.md` | `31,380 bytes` | `0A4F9D8B3D2005D0947A7C48E85F87D6B143ECC851DEB0E6345D27B2FF4AE534` | **`MATCH: True` (100% nguyên vẹn)** |
| **Sau Amendment v0.1.1** | `docs/games/cultivation_online/GDD.md` | `33,093 bytes` | `9AE22943227E2096B6FCF82F5E983DAEDE7CD6A498437854512D75737680E2AB` | Đã ghi rõ Revision History `v0.1.1` |

- Kiểm tra tồn tại file cũ `GDD_Tu_Tien_Online_v0.1.md`: `False` (không giữ hai nguồn GDD chính thức).

---

## 4. Chi tiết GDD Amendment `v0.1.1`

- **Phiên bản:** `0.1.0` → `0.1.1` (ghi nhận tại tiêu đề và Mục 22 *Lịch sử sửa đổi* của `docs/games/cultivation_online/GDD.md`).
- **Nội dung bổ sung (Mục 6 & Mục 10):**
  - Bổ sung tường minh 4 lệnh/dạng lệnh MVP: `!hothe` (`8s`, chỉ trong kiếp), `!hotheauto` (`5s`, xem trạng thái), `!hotheauto on` (`5s`, bật hộ thể tự động), `!hotheauto off` (`5s`, tắt hộ thể tự động để chơi thủ công).
  - Khẳng định quy tắc:
    1. Hộ thể tự động **mặc định bật** (`auto_guard_enabled = 1`).
    2. Người chơi tự bật/tắt qua bình luận; Game Master cấu hình được chính sách mặc định cho lượt kiếp mới.
    3. Tính toán hoàn toàn dựa trên **server-side event timing (`SimulationClock`)**, hỗ trợ độ trễ livestream, không yêu cầu phản ứng khớp khung hình animation.
    4. Tuyệt đối không dùng quà tặng trả phí tăng xác suất độ kiếp hay mua hộ thể.
- **Bảo toàn thông số cân bằng gốc:** Không thay đổi bất kỳ thông số cân bằng nào của `v0.1.0` (XP `2/s`, chi phí cảnh giới, `Boss HP = 500 + 180×N`, thiên lôi `17%` / `22%`, 5 đợt cách 4s, thang `1000` HP, phạt `10%` khi thất bại, cooldown `60s`).

---

## 5. Kết quả Xác minh Phần cứng Thực tế (Hardware Verification)

Đo trực tiếp trên máy chủ phát triển Windows tại thời điểm `2026-11-26 07:43 +07:00`:

| Hạng mục | Kết quả đo thực tế | Ghi chú kỹ thuật |
|---|---|---|
| **CPU** | 12th Gen Intel(R) Core(TM) i5-12450H (`8 Cores / 12 Threads`, MaxClock reported `2000 MHz`) | Đủ cho Backend + Desktop + Renderer |
| **RAM (Tổng / Khả dụng)** | **Tổng:** `15.73 GB` \| **Khả dụng:** `3.14 GB` | Cần đóng ứng dụng nền và theo dõi RAM trong bài soak test 4 giờ |
| **GPU Model (`nvidia-smi`)** | **NVIDIA GeForce RTX 4050 Laptop GPU** (Driver `591.59`) | Xác minh trực tiếp từ `nvidia-smi` |
| **GPU VRAM (Tổng vs Khả dụng)** | **Tổng VRAM:** `6141 MiB` (~6.00 GB) \| **Đang dùng:** `101 MiB` \| **Khả dụng:** `5820 MiB` (~5.68 GB) | Đã đính chính sai số 4 GB do giới hạn 32-bit của WMI `AdapterRAM` (~220 MiB system reserved) |
| **Disk Space (Available / Total)** | **`D:\`** (Workspace): `29.83 GB` trống / `80.00 GB` \| **`C:\`**: `76.40 GB` trống / `395.79 GB` | Theo dõi dung lượng ổ `D:\` từ GD01 trở đi |
| **Python** | `Python 3.11.9` | Khớp chuẩn Python 3.11+ |
| **Node.js / npm** | `Node v24.19.0` / `npm 11.17.0` | Đáp ứng Vite + TypeScript + Three.js |
| **Git** | `git version 2.49.0.windows.1` | Hoạt động bình thường |

---

## 6. Kết quả Đối chiếu Nhất quán Tài liệu (Documentation Cross-Check)

Đã kiểm tra chéo đầy đủ 14 tài liệu mục tiêu (`AGENTS.md`, `README.md`, `PROJECT_SPEC.md`, `ARCHITECTURE.md`, `TDD.md`, `ROADMAP.md`, `GAME_PLUGIN_CONTRACT.md`, `EVENT_CONTRACT.md`, `DATABASE_DESIGN.md`, `TESTING_POLICY.md`, `GDD.md`, `GDD_REQUIREMENTS_MAPPING.md`, `DECISIONS.md`, `PROJECT_STATUS.md`) cùng `CHANGELOG.md`, `GD00_ENVIRONMENT_REPORT.md` và `GD00_DELIVERY_REPORT.md`:

| Tiêu chí đối chiếu | Kết quả | Bằng chứng |
|---|---|---|
| Workspace duy nhất (`D:\Tiktok Mini Game`) | `PASS` | Không có repo trùng lặp, đồng nhất 100% |
| GAME001 (`cultivation_online`, Tu Tiên Online) | `PASS` | Đồng nhất 4 cảnh giới, 3 nghề, 1 map, 1 boss |
| Shared World & Single Broadcast Output (`1080×1920`, Single WebGLRenderer, max 1 PiP) | `PASS` | Không xung đột giữa `PROJECT_SPEC`, `ARCHITECTURE`, `TDD`, `UI_GUIDELINES`, `GDD` |
| Command list & Tribulation behavior (`!hothe`, `!hotheauto`, `on`/`off`, mặc định bật, server-side timing) | `PASS` | Khớp 100% giữa `GDD.md` v0.1.1, `EVENT_CONTRACT`, `GAME_PLUGIN_CONTRACT`, `DATABASE_DESIGN`, `TESTING_POLICY`, `ROADMAP` |
| Player persistence (`auto_guard_enabled`, SQLite WAL/UoW, anonymize policy) | `PASS` | Khớp giữa `DATABASE_DESIGN`, `GDD.md`, `DECISIONS` (`ADR-012`, `ADR-015`) |
| Asset production separation (no Meshy/Tripo/AI generator/Blender runtime) | `PASS` | Đồng nhất toàn bộ tài liệu |
| Development scope (không triển khai GD01 / runtime benchmark trong GD00) | `PASS` | `CODE_OR_BINARY_FILES: 0` |
| Toàn bộ Markdown links trong repository | `PASS` | `23` tệp `.md`, `22/22` local Markdown links hợp lệ (`0` broken links) |
| Xóa sạch tham chiếu sai `4GB VRAM` cũ | `PASS` | `0` kết quả tìm thấy trên toàn repo |

---

## 7. Các vấn đề mở còn lại (Remaining Open Issues — Ngoài phạm vi GD00-FIX01)

| ID | Hạng mục | Trạng thái | Cổng giải quyết |
|---|---|---|---|
| `OPEN-01` | Xác minh nguồn tiếp nhận sự kiện TikTok LIVE được cấp quyền (comment, gift, like, join) | `UNVERIFIED` | `GD17` Gate |
| `OPEN-02` | Đo benchmark thực tế mục tiêu MVP (`1080×1920`, `30 FPS`, `100` players, 4-hour soak test, CPU/RAM/GPU/VRAM + OBS) | `UNVERIFIED` | `GD09` / `GD19` |
| `OPEN-03` | Playtest & chốt cân bằng số liệu GAME001 (XP, Boss HP, Thiên lôi — giữ nguyên v0.1.0) | `PROPOSED` | `GD11`–`GD14` |
| `OPEN-06` | Xác minh bản quyền/license thực tế từng gói production asset & BGM/SFX | `UNVERIFIED` | `TT-AS01..09` / `GD07` |
| `OPEN-07` | Theo dõi dung lượng trống ổ `D:\` (`29.83 GB`) và RAM khả dụng (`3.14 GB`) khi cài môi trường & soak test | `MONITOR` | Liên tục từ `GD01` |

---

## 8. Lịch sử Git Commit trên `design/gd00`

- `be4d84d` — Baseline `GD00` (`docs(gd00): initialize LiveGame Studio architecture, contracts, and roadmap`).
- `fda1b1a` — Thực thi `GD00-FIX01` (`fix(gd00): resolve ADR-007, CONF-04/OPEN-05, hardware check, and MVP perf targets`).
- Commit tiếp theo trên `design/gd00` — Ghi nhận tệp báo cáo bàn giao này (`docs/GD00_FIX01_REPORT.md`).
- **Xác nhận Git Policy:** Đang ở nhánh `design/gd00`, chưa `git push`, chưa `git merge` vào `main`.
