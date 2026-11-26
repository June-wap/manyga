# PROJECT STATUS — LIVEGAME STUDIO

**Ngày cập nhật:** 2026-11-26  
**Workspace chính thức:** `D:\Tiktok Mini Game`  
**Branch hiện tại:** `integration/gd01`

**Giai đoạn hiện tại:** `GD01 – Platform Foundation`

**Deployment decision:** `ADR-021 — STANDALONE LOCAL DESKTOP`, mỗi thiết bị/Windows user độc lập, Hybrid Cloud cũ superseded. GD01 tiếp tục; GD02 schema/seed/migrations và GD20 installer chưa triển khai. Xem `docs/GD01_ARCHITECTURE_UPDATE_REPORT.md` cho trạng thái kiểm thử/review của cập nhật portability, phân biệt với kết quả baseline bên dưới.

**Trạng thái tổng thể GD01:** `PARTIAL — IMPLEMENTATION VERIFIED, INDEPENDENT REVIEW PENDING`. Regression sau ADR-021: 47 automated tests PASS (41 pytest + 3 Vitest + 3 Playwright); real Desktop/QWebEngine, PowerShell start/stop và không orphan PASS. Delta contract review Antigravity đã thử nhưng `BLOCKED` bởi quyền command của CLI headless; full GD01 independent acceptance vẫn NOT RUN. Chờ review trước khi chốt phase gate.
**Trạng thái tổng thể GD00:** `PASS — READY FOR GD01 APPROVAL (GD00 + GD00-FIX01 + GD00-FIX02 COMPLETE)` *(toàn bộ 6 HIGH, 4 MEDIUM và 1 LOW design findings đã được kiểm chứng và giải quyết tại `docs/GD00_INDEPENDENT_REVIEW.md` và `docs/GD00_FIX02_REPORT.md`)*

---

## 1. Bảng tiến độ giai đoạn (Roadmap Tracker)

| Giai đoạn | Tên | Trạng thái | Ghi chú |
|---|---|---|---|
| **GD00** | Project Design & Initialization (`+ FIX01 + FIX02`) | **COMPLETED (Design Review Findings Resolved)** | Toàn bộ 24 tài liệu nền tảng + `GD01_SCOPE.md` + `GD00_INDEPENDENT_REVIEW.md` + `GD00_FIX02_REPORT.md` trên `design/gd00` |
| GD01 | Platform Foundation | `IMPLEMENTED / REVIEW PENDING` | Sau ADR-021: 41 pytest + 3 Vitest + 3 Playwright PASS; GUI/WebGL/owned shutdown PASS; delta review BLOCKED, full independent acceptance pending |
| GD02 | Database & Application Services | `NOT STARTED` | Phụ thuộc GD01 |
| GD03 | Desktop Shell & Game Master UI | `NOT STARTED` | Phụ thuộc GD01–GD02 |
| GD04 | Event Gateway & Simulator | `NOT STARTED` | Phụ thuộc GD02 |
| GD05 | Game Plugin Engine | `NOT STARTED` | Phụ thuộc GD02, GD04 |
| GD06–GD20 | Platform Modules, GAME001 Vertical Slice & Packaging | `NOT STARTED` | Theo `docs/ROADMAP.md` |

---

## 2. Trạng thái kiểm tra GDD GAME001

- **File chính thức duy nhất (Single Source of Truth):** `docs/games/cultivation_online/GDD.md` (phiên bản `0.1.1` — di chuyển từ `GDD_Tu_Tien_Online_v0.1.md` qua `git mv` với SHA-256 xác minh trùng khớp 100%, bổ sung Amendment `v0.1.1` cho bộ lệnh `!hotheauto`).
- **Tài liệu đối chiếu:** `docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md`.
- **Trạng thái GDD:** Đã giải quyết `ADR-007` và `CONF-04`/`OPEN-05`; thông số cân bằng gốc giữ nguyên chờ playtest ở GD11–GD14.

---

## 3. Các vấn đề chưa xác minh & Điểm chờ quyết định (Open Risks / Unverified Items)

| ID | Hạng mục | Trạng thái | Tác động | Giai đoạn giải quyết |
|---|---|---|---|---|
| OPEN-01 | Nguồn tiếp nhận sự kiện TikTok LIVE được cấp quyền (comment, gift, like, join) | `UNVERIFIED` | Chặn Live Smoke Test (AC18); Simulator dùng để phát triển GD01–GD16 | GD17 Gate |
| OPEN-02 | Mục tiêu benchmark MVP (`1080×1920`, `30 FPS`, `100` players, single `WebGLRenderer`, max `1` PiP, LOD, resource disposal, **4-hour continuous session**) cùng OBS trên RTX 4050 Laptop (`6141 MiB` tổng VRAM / `5820 MiB` khả dụng) | `UNVERIFIED` | Ảnh hưởng LOD budget & kỹ thuật crowd rendering (SkinnedMesh batching); cần giám sát CPU/RAM/GPU/VRAM | GD09, GD19 Benchmark |
| OPEN-03 | Thông số cân bằng gameplay GAME001 (XP=2/s, Boss HP=`500+180*N` — rủi ro Phàm Nhân DPS thấp & tử trận sớm, Thiên lôi 17%/22%, giữ nguyên v0.1.0; yêu cầu **Combat Balance Simulator** ở GD13 & đánh giá **Tribulation Queue Waiting Time** ở GD14) | `PROPOSED` | Cần số liệu mô phỏng & playtest trước khi khóa balance MVP | GD11–GD14 Playtest & Sim |
| OPEN-04 | Vị trí lưu GDD chuẩn (`docs/games/cultivation_online/GDD.md`) | `RESOLVED` (`GD00-FIX01`, `ADR-007`) | Đã di chuyển bằng `git mv`, xác minh SHA-256, chỉ còn 1 nguồn GDD chính thức | Hoàn tất GD00-FIX01 |
| OPEN-05 | Bộ lệnh hộ thể tự động (`!hothe`, `!hotheauto`, `!hotheauto on`, `!hotheauto off`) | `RESOLVED` (`GD00-FIX01`, `ADR-015`) | Đã chuẩn hóa trong GDD `v0.1.1`, Command Contract, DB schema và AC06 | Hoàn tất GD00-FIX01 |
| OPEN-06 | Quyền sử dụng thương mại/livestream cho assets 3D, animations, BGM/SFX | `UNVERIFIED` | Bắt buộc có `license` & `provenance` hợp lệ trước khi nhập production asset | TT-AS01..09 / GD07 |
| OPEN-07 | Dung lượng trống ổ `D:\` (`29.83 GB / 80.00 GB`) và RAM khả dụng tại thời điểm đo (`3.14 GB / 15.73 GB`) | `MONITOR` | Đủ cho GD00–GD05, cần giám sát chặt khi cài `.venv`/`node_modules`, asset GLB và chạy soak test 4 giờ | Liên tục |

---

## 4. Bước tiếp theo (Next Actions)

1. Review độc lập GD01 theo hướng dẫn tại `docs/GD01_DELIVERY_REPORT.md`, đối chiếu đúng 13 mục `GD01_SCOPE.md`; chưa bắt đầu GD02.
2. GD00 gate: đã đọc final review `PASS / READY_FOR_GD01` tại `592db85`. Tệp final review chưa commit sau đó không còn trong workspace; chủ dự án xác nhận trong chat dùng kết luận PASS đã đọc và ghi rõ ở báo cáo. Không tái tạo hoặc tự nhận là tác giả của review gốc.
3. Không tự push hoặc merge. Nhánh bàn giao theo yêu cầu task là `integration/gd01`.
4. Đối chiếu ADR-021: default user-local paths và smoke foundation GD01; first-run zero-player production DB/migration preservation GD02, multi-hardware benchmark GD19, actual multi-user Windows installer/relocation/update GD20. Không mở cloud scope/GD21–GD26, không thay ownership hoặc GDD.
