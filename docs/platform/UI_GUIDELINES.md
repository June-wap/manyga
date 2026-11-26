# UI / UX GUIDELINES — LIVEGAME STUDIO

**Phiên bản:** 1.0.0 (GD00 Baseline)  
**Công nghệ UI:** PySide6 (Desktop Control Application) + HTML/CSS/Three.js (Broadcast Output `1080×1920`).

---

## 1. Nguyên tắc phân tách Bề mặt (Strict Surface Separation)

> **Quy tắc bất di bất dịch:** Tuyệt đối **không nhầm lẫn** Màn hình quản trị (dành cho Game Master trên Desktop) với Màn hình phát sóng (dành cho khán giả livestream `1080×1920`).

| Đặc tính | Màn hình Quản trị (PySide6 Desktop) | Màn hình Phát sóng (Broadcast Output 9:16) |
|---|---|---|
| **Người dùng** | Host / Game Master | Hàng trăm/nghìn khán giả TikTok LIVE |
| **Tỷ lệ khung hình** | Responsive Desktop (`1280×800` tối thiểu, tối ưu `1920×1080`) | Cố định dọc `9:16` (`1080×1920`) |
| **Nội dung** | Bảng điều khiển, log lỗi, trạng thái connector, cấu hình, kiểm duyệt, nút Emergency Pause | Thế giới 3D chung, nhân vật, Boss, Thiên kiếp, HUD gọn, hướng dẫn lệnh |
| **Cấm hiển thị** | Không được capture nhầm lên OBS | Cấm lộ nút admin, IP/port, log kỹ thuật, secret, danh sách kiểm duyệt |

---

## 2. Hệ thống thị giác Desktop (Visual Direction & Design Tokens)

### 2.1 Bảng màu Dark Theme + Purple Accent
| Token | Giá trị Hex | Công dụng |
|---|---|---|
| `bg.canvas` | `#0F1117` | Nền chính ứng dụng |
| `bg.surface` | `#161925` | Nền card, panel, sidebar |
| `bg.elevated` | `#1E2233` | Nền modal, dropdown, hover row |
| `border.subtle` | `#2A3045` | Viền phân tách panel và bảng |
| `accent.primary` | `#8B5CF6` | Purple accent chủ đạo (active nav, primary CTA) |
| `accent.hover` | `#A78BFA` | Trạng thái hover của nút chính |
| `accent.muted` | `#4C1D95` | Nền badge / tag nổi bật |
| `text.primary` | `#F3F4F6` | Tiêu đề, nội dung chính (contrast ≥ 12:1) |
| `text.secondary` | `#9CA3AF` | Nhãn phụ, metadata |
| `status.success` | `#10B981` | Connected, PASS, Running |
| `status.warning` | `#F59E0B` | Paused, Degraded, Simulator Mode, Placeholder |
| `status.danger` | `#EF4444` | Emergency Pause, Error, Disconnected, Backend Offline |

### 2.2 Typography & Hỗ trợ Tiếng Việt UTF-8
- **Font ưu tiên trên Windows:** `Segoe UI Variable`, `Segoe UI`, `Inter`, fallback `Arial` (hỗ trợ đầy đủ dấu thanh Tiếng Việt, không bị lệch baseline).
- **Font số liệu & logs:** `Cascadia Mono`, `Consolas`, monospace (dùng tabular numerals cho đồng hồ phiên, HP, FPS, queue depth).
- **Thang chữ chuẩn:** Page Title `20px SemiBold`, Section Header `15px SemiBold`, Body/Table `13px Regular`, Caption/Badge `11px Medium`.
- **Chính trực giao diện (No Fake UI):** Tính năng chưa triển khai ở giai đoạn hiện tại phải ẩn hoặc gắn badge `Sắp ra mắt (GDxx)` ở trạng thái disabled rõ ràng — **tuyệt đối không hiển thị nút giả mạo như đang hoạt động**.

### 2.3 Trạng thái chuẩn bắt buộc trên mọi màn hình
- **Empty State:** Hiển thị thông điệp rõ ràng kèm hành động kế tiếp (ví dụ: *"Chưa có người chơi nào nhập môn. Dùng Event Simulator để thử lệnh `!join`."*).
- **Loading State:** Không đóng băng main Qt UI thread (mọi lời gọi HTTP/WS chạy bất đồng bộ); hiển thị skeleton hoặc progress indicator gọn.
- **Error State:** Hiển thị banner lỗi rõ nguyên nhân + nút Thử lại.
- **Backend Unavailable State:** Banner đỏ cố định ở top bar báo mất kết nối Backend `127.0.0.1`, vô hiệu hóa nút ghi thao tác và tự thử kết nối lại có đếm ngược.

---

## 3. Kiến trúc Điều hướng Desktop (14 Màn hình Platform)

Sidebar trái thu gọn được (`220px` mở rộng / `64px` thu gọn), nhóm logic thành 4 cụm rõ ràng:

| Nhóm | # | Màn hình | Chức năng chính | Giai đoạn |
|---|---|---|---|---|
| **Vận hành (Operate)** | 1 | **Dashboard** | Tổng quan sức khỏe Backend/DB, phiên gần nhất, game đang chọn, cảnh báo nhanh | `GD01` (health shell) / `GD03` (full) |
| | 2 | **Game Library** | Danh sách mini game (`GAME001`–`GAME007+`), trạng thái tương thích, chọn active game | `GD01` (nav placeholder) / `GD05` (full) |
| | 3 | **Live Studio** | Checklist sẵn sàng phát sóng (`DEVELOPMENT`/`PRODUCTION` asset mode), Broadcast Preview 9:16, URL OBS Browser Source (không chứa admin token), trạng thái Connector | `GD03` / `GD18` |
| | 4 | **Game Master** | Trung tâm điều hành trực tiếp trong lúc live (gắn Extension Panel của game đang chạy) | `GD03` / `GD12` |
| **Luật & Sự kiện (Rules)** | 5 | **Event Scheduler** | Lịch sự kiện tự động/thủ công, timeline sắp diễn ra, trạng thái xung đột | `GD12` |
| | 6 | **Gift Mapping** | Ánh xạ quà tặng sang **hiệu ứng cosmetic** (kèm cảnh báo khóa Anti-P2W) | `GD06` / `GD16` |
| | 7 | **Players** | Danh sách người chơi, tìm kiếm, trạng thái hoạt động, kiểm duyệt tên, xóa/ẩn danh hóa | `GD03` / `GD11` |
| **Tài nguyên (Assets)** | 8 | **Asset Library** | Kho tổng hợp mọi asset, trạng thái validation & cảnh báo placeholder, nút Import gói ngoài | `GD01` (nav placeholder) / `GD07` (full) |
| | 9 | **Characters** | Lọc nhanh asset `character`, phiên bản, placeholder/production, skeleton profile | `GD07` / `GD09` |
| | 10 | **Maps** | Lọc nhanh asset `map`, kiểm tra zone anchors (`spawn_gate`, `cultivation_court`, ...) | `GD07` / `GD10` |
| | 11 | **Animations** | Lọc nhanh asset `animation`, bảng đối chiếu clip bắt buộc của game | `GD07` / `GD09` |
| **Kiểm thử & Hệ thống** | 12 | **Event Simulator** | Bảng giả lập lệnh chat/gift/burst 100/s, chạy kịch bản Replay, giả lập disconnect | `GD04` |
| | 13 | **Analytics** | Chỉ số phiên live, FPS/VRAM, latency p50/p95, thống kê Boss/Độ kiếp, xuất benchmark | `GD18` / `GD19` |
| | 14 | **Settings** | Cấu hình cổng loopback, retention log, âm lượng, giảm nhấp nháy VFX, backup DB | `GD01` (local shell) / `GD03` (full) |

---

## 4. Giao diện chuyên biệt GAME001 — Tu Tiên Online (Game Master Extension)

Khi `cultivation_online` được kích hoạt, màn hình **Game Master** hiển thị bố cục lưới responsive gồm đủ 10 khối chức năng:

1. **World Preview:** Khung xem trước thế giới 3D thu nhỏ (có nút tạm tắt preview trên panel để tiết kiệm GPU khi đang livestream).
2. **Player List:** Danh sách đạo hữu theo thời gian thực (tên, nghề, cảnh giới, tầng, tu vi, trạng thái `CULTIVATING/BOSS/TRIBULATION/IDLE`, nút Highlight / Kiểm duyệt).
3. **Boss Control:** Trạng thái World Boss Bạch Lang Vương (`SCHEDULED..COMPLETED`), thanh HP, số người đăng ký `/100`, nút Triệu hồi sớm (khi idle) và Hủy có xác nhận.
4. **Tribulation Queue:** Hàng chờ FIFO Tiểu Thiên Kiếp (`x/20`), hiển thị người đang độ kiếp, số lôi hiện tại, nút bật/tắt chính sách auto-hộ thể cho lượt mới.
5. **Cultivation Statistics:** Tổng số người đang tu luyện, phân bố theo 4 cảnh giới & 3 nghề, tốc độ XP/s, số đột phá trong phiên.
6. **Event Timeline:** Đồng hồ phiên (`SimulationClock`), sự kiện đang diễn ra và đếm ngược sự kiện kế tiếp (Boss, Leaderboard, Guide).
7. **Camera Control:** 5 nút chọn nhanh `CAM01`–`CAM05`, trạng thái Auto / Manual Override (đếm ngược 20s tự trả về Auto), công tắc bật/tắt **PiP**.
8. **Broadcast Preview:** Khung kiểm tra tỷ lệ dọc `9:16` kèm công tắc bật/tắt lưới **TikTok Safe Area**.
9. **Emergency Pause:** Thanh thao tác nổi bật màu đỏ/vàng luôn nhìn thấy ở Top Action Bar: **PAUSE (Đóng băng Simulation)**, **RESUME**, **STOP SESSION (có hộp thoại xác nhận)** và chọn chế độ `Semi-auto / Auto / Manual`.
10. **Activity Logs:** Luồng nhật ký trực tiếp gồm 2 tab: *Lệnh & Lỗi nghiệp vụ* (hiển thị `reason_code` gọn) và *Audit Logs* (mọi thao tác của GM).

---

## 5. Thiết kế Màn hình Phát sóng 9:16 (`1080×1920` Viewer Screen)

```text
┌─────────────────────────────────────┐  y = 0
│  [TOP SAFE MARGIN ~120px]           │  (Tránh thanh host/viewer TikTok)
├─────────────────────────────────────┤
│  HEADER GỌN (~100px)                │  Tên game | Số đạo hữu | Đếm ngược Event
├─────────────────────────────────────┤
│                                     │
│                                     │
│   3D SHARED WORLD VIEWPORT          │  Chiếm ~65–75% chiều cao
│   (Single WebGLRenderer)            │
│                                     │  ┌──────────────┐
│   [Boss HP Bar / Tribulation Bar    │  │ Optional PiP │ (Tối đa 1 PiP,
│    chỉ hiện khi event ACTIVE]       │  │ (CAM03)      │  cách mép phải
│                                     │  └──────────────┘  tránh icon TikTok)
│                                     │
├─────────────────────────────────────┤
│  CONTEXT OVERLAY CARD (~140px)      │  !info (3s) / Toast gộp / Leaderboard luân phiên
├─────────────────────────────────────┤
│  FOOTER COMMAND GUIDE (~90px)       │  Banner cố định/luân phiên: !join !nam !nu !boss !dotpha
├─────────────────────────────────────┤
│  [BOTTOM + RIGHT SAFE MARGIN]       │  (Tránh luồng comment ~280px đáy & icon ~110px phải)
└─────────────────────────────────────┘  y = 1920
```

### Quy tắc thiết kế Broadcast 9:16
- **Safe Area điều chỉnh được** trong Settings vì giao diện TikTok thay đổi theo dòng điện thoại (Android/iOS).
- **Không đặt chữ quan trọng sát mép phải (`x > 950px`) hoặc sát đáy (`y > 1620px`)**.
- **Độ đọc cao:** Dùng nền bán trong suốt (`rgba(15, 17, 23, 0.72)`) + viền mỏng sáng cho HUD để chữ Tiếng Việt luôn rõ trên nền mây/đá sáng của Thanh Vân Tông.
- **Chống nhiễu thị giác:** Hỗ trợ chế độ *Giảm nhấp nháy VFX (Reduced Flash)* cho thiên lôi và hiệu ứng quà tặng.
