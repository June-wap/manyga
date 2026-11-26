# PROJECT SPECIFICATION — LIVEGAME STUDIO

**Phiên bản:** 1.0.0 (GD00 Baseline)  
**Workspace:** `D:\Tiktok Mini Game`  
**Cập nhật:** 2026-11-26  

---

## 1. Tầm nhìn và Mục tiêu sản phẩm

**LiveGame Studio** là một nền tảng phần mềm **Windows Desktop (Local-first)** giúp người vận hành livestream (Host / Game Master) chạy nhiều mini game tương tác thời gian thực với khán giả TikTok LIVE trên cùng một phần mềm thống nhất.

### Vấn đề giải quyết
- Các mini game livestream đơn lẻ thường bị viết cứng (monolithic script), thiếu khả năng lưu tiến trình bền vững, dễ crash khi bùng nổ comment, khó thay đổi game mới và trộn lẫn giao diện điều khiển với màn hình phát sóng.
- LiveGame Studio tách biệt rõ **Platform Core** (vận hành, sự kiện, lưu trữ, đồ họa, camera, overlay, asset, quản trị) với **Game Plugin** (luật chơi từng game), cho phép bổ sung 10 đến 100+ mini game mà không sửa lõi Platform hay làm hỏng game đã có.

### Nguyên tắc chiến lược: Vertical Slice Development
- Không xây hàng loạt module Platform rời rạc mà thiếu kiểm chứng thực tế.
- **GAME001 – Tu Tiên Online (`cultivation_online`)** là Vertical Slice đầu tiên: mọi contract và module của Platform (Event, Player, Persistence, Plugin, Asset, Three.js 3D Runtime, Camera Director, Overlay, Scheduler, Game Master) đều được thiết kế tổng quát nhưng kiểm chứng trực tiếp bằng Tu Tiên Online.
- **Ba luồng song song:**
  - **Luồng A — Platform Development:** Lõi phần mềm dùng chung (`core/`, `modules/`, `apps/`, `frontend/`).
  - **Luồng B — Game Plugin Development:** Logic riêng của `GAME001` (`games/cultivation_online/`) sử dụng Platform qua contract.
  - **Luồng C — External Asset Production:** Sản xuất asset 3D/VFX/Audio bên ngoài theo mã `TT-AS`, nhập vào Platform qua Asset Contract.

---

## 2. Danh mục Mini Game mục tiêu

| Game ID | Plugin ID | Tên | Thể loại | Engine dự kiến | Giai đoạn |
|---|---|---|---|---|---|
| `GAME001` | `cultivation_online` | Tu Tiên Online | Interactive Idle RPG 3D | Three.js | MVP (GD05–GD20) |
| `GAME002` | `bar_online` | Bar Online | Social Hangout / Ordering | Three.js / Phaser.js | Post-MVP |
| `GAME003` | `temple_online` | Chùa Online | Interactive Idle / Blessing | Three.js | Post-MVP |
| `GAME004` | `duck_race` | Đua Vịt | Crowd Racing | Three.js / Phaser.js | Post-MVP |
| `GAME005` | `tug_of_war` | Đại Chiến Kéo Co | Team Tug-of-War | Three.js / Phaser.js | Post-MVP |
| `GAME006` | `prison_online` | Nhà Tù Online | Social Escape / Roleplay | Three.js | Post-MVP |
| `GAME007` | `classroom_online` | Lớp Học Online | Interactive Quiz / Classroom | Three.js | Post-MVP |
| `GAME008+` | `<extensible>` | Mini game mở rộng tương lai | 2D / 3D Interactive | Three.js / Phaser.js | Long-term |

---

## 3. Vai trò người dùng & Bề mặt tương tác (User Roles & Surfaces)

| Vai trò | Bề mặt tương tác | Quyền hạn & Trách nhiệm |
|---|---|---|
| **Khán giả (Viewer / Player)** | Bình luận trên livestream (hoặc Event Simulator khi test) | Sở hữu nhân vật của chính mình, gửi lệnh chat điều khiển nhân vật theo cooldown; xem chung 1 màn hình livestream dọc `1080×1920`. Không có quyền điều khiển nhân vật người khác. |
| **Game Master (Host / Operator)** | Ứng dụng Desktop PySide6 (Control Panel riêng) | Chọn game, quản lý phiên live, cấu hình lịch sự kiện, bật/tắt connector, điều phối camera thủ công, kích hoạt/hủy event, kiểm duyệt tên hiển thị, dừng khẩn cấp (Emergency Pause/Stop). |
| **Technical Artist / Asset Creator** | Quy trình bên ngoài (`asset_production/`) + Asset Importer UI | Sản xuất GLB/glTF 2.0 theo Asset Contract, nhập và xác thực qua Asset Validator trước khi kích hoạt. |
| **Hệ thống (Backend & Renderer)** | FastAPI Server (`127.0.0.1`) + Three.js Broadcast Viewport | Backend là nguồn sự thật duy nhất (Single Source of Truth) về trạng thái, thời gian, luật chơi, phần thưởng. Renderer chỉ hiển thị snapshot/delta, không tự tính toán kết quả gameplay. |

> **Ranh giới bề mặt bắt buộc:** Màn hình điều khiển quản trị (PySide6 Desktop) và Màn hình phát sóng cho khán giả (`1080×1920` WebGL/Three.js capture vào OBS/TikTok LIVE Studio) phải tách biệt hoàn toàn. Không bao giờ để lộ panel điều khiển, log kỹ thuật, hoặc thông tin cấu hình lên luồng livestream.

---

## 4. Yêu cầu chức năng Platform (Platform Functional Requirements)

1. **Quản lý ứng dụng & cấu hình:** Lưu cấu hình cục bộ, logging có cấu trúc (redact secrets), quản lý vòng đời tiến trình sạch (không để orphan process khi thoát).
2. **Hệ thống Game Plugin:** Đăng ký, kiểm tra tương thích version, nạp/gỡ trusted built-in plugins, quản lý vòng đời `init → start → tick → handle_event → pause → resume → stop → shutdown` và cô lập dữ liệu theo `plugin_id`.
3. **Quản lý phiên live (Game Session):** Tạo/mở lại phiên, theo dõi đồng hồ simulation đơn điệu (`monotonic clock`), xử lý `PAUSE` / `RESUME` / `STOP` và phục hồi an toàn sau crash (`Crash Recovery`).
4. **Đường ống sự kiện (Event Pipeline):** Tiếp nhận sự kiện từ nhà cung cấp được cấp quyền hoặc **Event Simulator**, chuẩn hóa về Normalized Event Envelope, chống trùng lặp (idempotency/dedupe), rate-limit, backpressure, phân tích lệnh tường minh (deterministic Command Parser — không dùng LLM suy diễn lệnh), ghi nhật ký phục vụ Replay test.
5. **Quản lý người chơi toàn cục & lưu trữ bền vững:** Ánh xạ định danh ngoài ổn định (`provider + channel_id + external_user_id`) sang hồ sơ người chơi toàn cục và hồ sơ riêng từng game; bảo toàn tiến trình giữa các buổi livestream; hỗ trợ opt-out và xóa/ẩn danh hóa dữ liệu theo yêu cầu GM.
6. **Thư viện tài nguyên chuẩn hóa (Universal Asset System):** Nhập, kiểm tra (hash SHA-256, schema manifest, GLB/glTF 2.0, đường dẫn tương đối an toàn, tên animation, LOD metadata, license provenance), quản lý phiên bản và cung cấp fallback placeholder khi thiếu hoặc lỗi asset.
7. **Thế giới chung 3D & Đạo diễn Camera (Shared World & Camera Director):** Một WebGL renderer duy nhất xuất khung dọc `1080×1920`, nhiều camera ảo chuyển mượt theo bảng ưu tiên, hỗ trợ tối đa 1 PiP (tắt được để tiết kiệm GPU), hàng chờ Event Overlay có TTL, LOD/frustum culling và chiến lược hiển thị đám đông.
8. **Lập lịch, Quà tặng Cosmetic & Sổ cái phần thưởng:** Lịch sự kiện tránh xung đột, sổ cái phần thưởng idempotent (`reward_ledger`), ánh xạ quà tặng **chỉ cho hiệu ứng giải trí (cosmetic)** theo cấu hình.
9. **Live Studio & OBS Integration:** Xuất khung hình dọc sạch 9:16 (window capture / browser source loopback), kiểm soát safe-area TikTok, theo dõi sức khỏe hệ thống (FPS, queue depth, latency).

---

## 5. Đặc tả Vertical Slice: GAME001 — Tu Tiên Online (`cultivation_online`)

*(Trích xuất và đối chiếu từ `docs/games/cultivation_online/GDD.md` v0.1.1 — Single Source of Truth cho gameplay; chi tiết đầy đủ tại `docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md`.)*

- **Định danh:** `game_id = GAME001`, `plugin_id = cultivation_online`, Thể loại: Interactive Idle RPG, Phong cách: Stylized Chibi 3D Xianxia, Độ phân giải: `1080×1920`.
- **Mục tiêu đồng thời:** 100 người chơi hoạt động đồng thời (*mục tiêu thiết kế, bắt buộc phải benchmark thực tế tại GD19*).
- **Phạm vi MVP bắt buộc:**
  - **Nhân vật:** Nam (`TT_CHAR001`) và Nữ (`TT_CHAR002`); 3 nghề: **Kiếm Tu**, **Đan Tu**, **Thể Tu**.
  - **Bản đồ:** 1 map **Thanh Vân Tông** (`TT_MAP001`) tách rõ các zone (`spawn_gate`, `cultivation_court` ≥100 slot logic, `boss_arena`, `tribulation_platform`, `sect_hall`, `paths`).
  - **Cảnh giới (4 bậc):** Phàm Nhân (1 tầng) → Luyện Khí (4 tầng) → Trúc Cơ (4 tầng) → Kim Đan (4 tầng, giới hạn MVP).
  - **Cơ chế cốt lõi:** Nhập môn (`!join`, `!nam`/`!nu`, `!kiem`/`!dan`/`!the`), Auto Cultivation (`2 XP/s` đề xuất, tick 1s, không tăng khi server tắt), Breakthrough thường, Tiểu Thiên Kiếp (2 mốc Luyện Khí → Trúc Cơ và Trúc Cơ → Kim Đan, hàng chờ FIFO tối đa 20, không RNG), World Boss **Bạch Lang Vương** (`TT_BOSS001`, vòng đời 8 trạng thái, tick chiến đấu 2s, phản công 6s), Tài nguyên (Linh thạch, Hồi linh đan), Reward Ledger chống cấp trùng, Leaderboard, Event Scheduler, Game Master Panel, Camera Director (5 camera `CAM01`–`CAM05`), Player Persistence.
- **Quy tắc đạo đức & tuân thủ:**
  - Quà tặng trả phí **chỉ kích hoạt hiệu ứng giải trí (cosmetic)** theo cấu hình (hoa sen, kiếm bay, linh quang, rồng trang trí).
  - Tuyệt đối không cho phép quà tặng cộng XP/ATK/HP, tăng tỷ lệ đột phá, mua lượt độ kiếp, đánh cược hay đổi thưởng tiền thật.

---

## 6. Yêu cầu phi chức năng (Non-Functional Requirements)

| Hạng mục | Yêu cầu mục tiêu | Ghi chú xác minh |
|---|---|---|
| **Hiệu năng Render & Broadcast (Mục tiêu benchmark — chưa đo)** | Phát sóng `1080×1920`, mục tiêu `30 FPS` ổn định (`60 FPS` nâng cao) với `100` concurrent active players trên **1 `WebGLRenderer` duy nhất**, tối đa **1 PiP** (tắt được), áp dụng chiến lược **LOD** và **Resource Disposal** sạch | **Mục tiêu kiểm thử, không phải kết quả đã đạt.** Phải benchmark đo p50/p95 frame time, draw calls ở GD19 |
| **Độ bền phiên dài & Giám sát tài nguyên (Mục tiêu benchmark — chưa đo)** | Chạy phiên liên tục **4 giờ** (4-hour continuous session soak test) có giám sát **CPU, RAM, GPU và VRAM** không rò rỉ bộ nhớ, không suy giảm frame time | Bắt buộc đo và báo cáo kèm cấu hình phần cứng tại GD19 |
| **Tải sự kiện** | Chịu burst thử nghiệm `100 lệnh/giây` trong 30 giây không mất sự kiện hợp lệ, không crash | Kiểm chứng qua Event Simulator replay ở GD04/GD19 |
| **Bền vững dữ liệu** | SQLite WAL + Foreign Keys ON; transaction nguyên tử cho đăng ký, XP, đột phá, reward; checkpoint mỗi 10s và khi đổi mốc quan trọng | Kiểm chứng qua crash/restart tests ở GD02, GD11, GD13, GD14 |
| **Bảo mật Local-first** | Backend chỉ bind `127.0.0.1` theo mặc định; chống path traversal ở Asset/File; escape HTML trên mọi tên hiển thị; redact secrets khỏi logs/UI | Kiểm tra ở mọi review gate (`GD01+`) |
| **Khả năng mở rộng** | Thêm `GAME002`..`GAME100` chỉ cần tạo plugin mới trong `games/` tuân thủ `GAME_PLUGIN_CONTRACT.md`, không sửa `core/` hay `games/cultivation_online/` | Xác minh bằng smoke plugin thứ 2 trong test suite ở GD05 |
| **Ngôn ngữ & Encoding** | Hỗ trợ đầy đủ Tiếng Việt UTF-8 ở UI Desktop, Command aliases có dấu, Overlay và Logs | Kiểm thử đa font và ký tự đặc biệt ở GD03/GD08 |

---

## 7. Phạm vi loại trừ tuyệt đối (Explicit Out-of-Scope)

Các hạng mục sau **KHÔNG** thuộc phạm vi nền tảng LiveGame Studio MVP và bị cấm triển khai tự phát:
- Tích hợp Meshy API, Tripo API, AI Asset Generator hoặc chạy Blender runtime trong ứng dụng.
- Tự động tạo production 3D assets trong các giai đoạn foundation.
- Kết nối TikTok LIVE không được cấp quyền, reverse-engineer/scrape trái phép hoặc thu thập cookie/token không hợp lệ.
- Cơ chế đánh cược (gambling), gacha/lootbox trả phí, đổi thưởng tiền thật, giao dịch P2P giữa người chơi.
- Hạ tầng Cloud multi-tenant, server phân tán, cổng thanh toán (payment gateway), marketplace bán plugin/asset.
- Các tính năng sau MVP của GAME001: 14 cảnh giới, linh căn đầy đủ, nhiều map, nhiều boss, PvP, AI NPC hội thoại.
