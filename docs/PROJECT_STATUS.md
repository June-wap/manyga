# PROJECT STATUS — LIVEGAME STUDIO

**Ngày cập nhật:** 2026-11-26  
**Workspace chính thức:** `D:\Tiktok Mini Game`  
**Branch hiện tại:** `design/gd00`  
**Giai đoạn hiện tại:** `GD00 – Project Design & Initialization`  
**Trạng thái tổng thể GD00:** `PASS WITH OPEN ITEMS (UNVERIFIED GDD PARAMS & TIKTOK PROVIDER)` *(chi tiết tiêu chí nghiệm thu tại `docs/GD00_DELIVERY_REPORT.md`)*

---

## 1. Bảng tiến độ giai đoạn (Roadmap Tracker)

| Giai đoạn | Tên | Trạng thái | Ghi chú |
|---|---|---|---|
| **GD00** | Project Design & Initialization | **COMPLETED (Pending Review/Approval)** | Toàn bộ 21 tài liệu nền tảng + cấu trúc thư mục + `.gitignore` đã tạo trên `design/gd00` |
| GD01 | Platform Foundation | `NOT STARTED` | Chờ duyệt GD00; sẽ khởi tạo Python `.venv`, FastAPI skeleton, PySide6 shell, Vite/Three.js skeleton |
| GD02 | Database & Application Services | `NOT STARTED` | Phụ thuộc GD01 |
| GD03 | Desktop Shell & Game Master UI | `NOT STARTED` | Phụ thuộc GD01–GD02 |
| GD04 | Event Gateway & Simulator | `NOT STARTED` | Phụ thuộc GD02 |
| GD05 | Game Plugin Engine | `NOT STARTED` | Phụ thuộc GD02, GD04 |
| GD06–GD20 | Platform Modules, GAME001 Vertical Slice & Packaging | `NOT STARTED` | Theo `docs/ROADMAP.md` |

---

## 2. Trạng thái kiểm tra GDD GAME001

- **File tìm thấy:** `GDD_Tu_Tien_Online_v0.1.md` (phiên bản `0.1.0`, 274 dòng, tại root workspace).
- **Trạng thái đọc:** Đã đọc đầy đủ 100%, không chỉnh sửa/ghi đè.
- **Tài liệu đối chiếu:** `docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md`.
- **Trạng thái GDD:** Bản thiết kế MVP chờ người dùng phê duyệt và cân bằng số liệu (`v0.1.0`).

---

## 3. Các vấn đề chưa xác minh & Điểm chờ quyết định (Open Risks / Unverified Items)

| ID | Hạng mục | Trạng thái | Tác động | Giai đoạn giải quyết |
|---|---|---|---|---|
| OPEN-01 | Nguồn tiếp nhận sự kiện TikTok LIVE được cấp quyền (comment, gift, like, join) | `UNVERIFIED` | Chặn Live Smoke Test (AC18); Simulator dùng để phát triển GD01–GD16 | GD17 Gate |
| OPEN-02 | Khả năng render 100 nhân vật Chibi 3D ở 30/60 FPS (`1080×1920`) cùng OBS trên RTX 4050 Laptop (4GB VRAM) | `UNVERIFIED` | Ảnh hưởng LOD budget & kỹ thuật crowd rendering (SkinnedMesh batching) | GD09, GD19 Benchmark |
| OPEN-03 | Thông số cân bằng gameplay GAME001 (XP=2/s, Boss HP=`500+180*N`, Thiên lôi 17%/22%, auto-hộ thể mặc định ON) | `PROPOSED` | Cần chốt trước khóa balance MVP | GD11–GD14 Playtest |
| OPEN-04 | Vị trí lưu GDD chuẩn (`GDD_Tu_Tien_Online_v0.1.md` ở root vs `docs/games/cultivation_online/GDD.md`) | `PENDING APPROVAL` | Không chặn kỹ thuật, cần xác nhận để đồng bộ đường dẫn (ADR-007) | Trước GD05 |
| OPEN-05 | Alias `!hotheauto off` được nhắc ở Mục 10 GDD nhưng chưa có trong bảng lệnh Mục 6 GDD | `CLARIFICATION NEEDED` | Cần xác nhận đưa vào bảng lệnh MVP hay để config GM | Trước GD14 |
| OPEN-06 | Quyền sử dụng thương mại/livestream cho assets 3D, animations, BGM/SFX | `UNVERIFIED` | Bắt buộc có `license` & `provenance` hợp lệ trước khi nhập production asset | TT-AS01..09 / GD07 |
| OPEN-07 | Dung lượng trống ổ `D:\` hiện còn `29.83 GB` | `MONITOR` | Đủ cho GD00–GD05, cần theo dõi khi có `node_modules`, `.venv`, asset GLB và OBS recordings | Liên tục |

---

## 4. Bước tiếp theo (Next Actions)

1. Chủ dự án phê duyệt kết quả `GD00` và xác nhận các mục tại Mục 3 (đặc biệt ADR-007 và định hướng cân bằng GDD v0.1.0).
2. Sau khi được yêu cầu rõ ràng, merge `design/gd00` (hoặc tạo branch `feat/gd01-foundation` từ `design/gd00`).
3. Khởi động **GD01 – Platform Foundation** (Codex triển khai foundation backend/desktop/frontend skeleton; Antigravity thực hiện independent review GD01-R1).
