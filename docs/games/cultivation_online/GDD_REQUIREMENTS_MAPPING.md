# GDD REQUIREMENTS MAPPING — GAME001: TU TIÊN ONLINE (`cultivation_online`)

**Trạng thái kiểm tra GDD:** `GDD_FOUND & RELOCATED (Single Source of Truth)`  
**File nguồn chính thức:** `docs/games/cultivation_online/GDD.md` (phiên bản `0.1.1` — di chuyển nguyên vẹn qua `git mv` từ `GDD_Tu_Tien_Online_v0.1.md`, xác minh SHA-256 `0A4F9D8B3D2005D0947A7C48E85F87D6B143ECC851DEB0E6345D27B2FF4AE534` trước/sau trùng khớp 100%, sau đó ghi nhận Amendment `v0.1.1` chuẩn hóa lệnh `!hotheauto`).  
**Cam kết toàn vẹn:** Giữ nguyên 100% toàn bộ thông số cân bằng gốc của `v0.1.0`; mọi thay đổi chỉ thuộc Amendment `v0.1.1` đã được phê duyệt trong `GD00-FIX01`.

---

## 1. Trích xuất Yêu cầu Gameplay từ GDD v0.1.0

### 1.1 Định danh & Cốt lõi (GDD Mục 1–4)
- **Game ID / Plugin ID:** `GAME001` / `cultivation_online` (tên quốc tế đề xuất: *Immortal Ascension*).
- **Thể loại & Hình ảnh:** Idle RPG cộng đồng 3D, phong cách Stylized Chibi 3D Xianxia, 1 thế giới chung, 1 màn hình dọc `1080×1920`, tối đa 1 PiP (tắt được).
- **Mục tiêu đồng thời:** `100` người chơi logic hoạt động đồng thời (mục tiêu thiết kế, cần benchmark ở GD19).
- **Vòng lặp chính:** Nhập môn → chọn ngoại hình/nghề (cửa sổ 60s, không chặn spawn) → tự tu luyện → tích lũy tu vi → hoạt động cộng đồng (Boss / Độ kiếp) → nhận tài nguyên → đột phá → lưu tiến trình qua nhiều phiên live (không cộng XP khi server tắt).

### 1.2 Nhận diện, Nhập môn & Bộ Lệnh tương tác MVP (GDD Mục 5–6, Amendment v0.1.1)
- Định danh bằng `player_external_id` ổn định + namespace kênh/world (không dùng nickname làm khóa; không suy luận giới tính; không tạo hồ sơ chỉ vì `room_join` hay `gift`).
- Tên hiển thị giới hạn `20` ký tự, escape HTML, lọc từ không phù hợp, hỗ trợ bí danh và opt-out `!roi` (lưu tiến trình, không xóa lịch sử thưởng) + GM xóa dữ liệu theo yêu cầu.
- Parser xác định không dùng LLM, không phân biệt hoa/thường, hỗ trợ alias Tiếng Việt có dấu tường minh, 1 comment tối đa 1 lệnh, mọi lệnh gắn chặt `sender_player_id` và tính theo **server-side event timing (`SimulationClock`)**:
  - `!join` (5s, idempotent; mặc định nam + Kiếm Tu, mở cửa sổ chọn 60s), `!nam`/`!nu` (10s, ngoài event, nhập môn trực tiếp được), `!kiem`/`!dan`/`!the` (10s, trong 60s đầu hoặc khi GM mở đổi nghề ngoài chiến đấu), `!tuluyen` (3s), `!nghi` (3s), `!dotpha` / `!dokiep` (10s chung cooldown), `!boss` (5s, pha đăng ký), `!skill` (12s, trong boss), `!defend` (8s, trong boss), `!heal` (20s, có Hồi linh đan), `!hothe` (8s, hộ thể thủ công trong kiếp), `!hotheauto` / `!hotheauto on` / `!hotheauto off` (5s, xem/bật/tắt hộ thể tự động — mặc định bật, hỗ trợ độ trễ livestream, GM cấu hình mặc định), `!info`/`!status` (60s, overlay queue), `!find`/`!me` (60s, highlight, không ngắt boss), `!rank` (60s), `!help` (30s), `!roi` (rời game, giữ thưởng).

### 1.3 Cảnh giới, Nghề & Tài nguyên (GDD Mục 7)
- **4 Cảnh giới MVP** (bậc `0..3`, 4 tầng `Sơ kỳ / Trung kỳ / Hậu kỳ / Viên mãn` cho bậc 1–3; Kim Đan Viên mãn là trần MVP):
  - Phàm Nhân (1 tầng): cost `100`, gốc `100 HP / 12 ATK / 4 DEF`.
  - Luyện Khí (4 tầng): costs `200, 300, 400, 600`, gốc `180 / 20 / 8`.
  - Trúc Cơ (4 tầng): costs `800, 1000, 1200, 1600`, gốc `300 / 32 / 14`.
  - Kim Đan (4 tầng): costs `2000, 2500, 3200, MAX`, gốc `500 / 50 / 22`.
  - Mỗi tầng sau Sơ kỳ tăng chỉ số gốc `+5%` cộng dồn tuyến tính, làm tròn xuống sau khi áp dụng hệ số nghề.
- **Auto Cultivation:** `+2 XP/giây` (tick 1s), giữ XP dư khi đột phá, cap XP tồn = `2 × chi phí tầng hiện tại`, không cộng khi đánh boss / di chuyển / độ kiếp / pause / offline / quá 5 phút không tương tác.
- **3 Nghề:**
  - Kiếm Tu (`ATK ×1.20`, skill `12s`: Kiếm khí gây `2 × auto_dmg`).
  - Đan Tu (`HP ×1.10`, skill `12s`: hồi `15%` maxHP cho bản thân + 2 đồng đội HP thấp nhất còn sống).
  - Thể Tu (`HP ×1.30`, `DEF ×1.20`, skill `12s`: Hộ thể giảm `50%` sát thương trong `6s`).
- **Tài nguyên:** Linh thạch (nguyên không âm, chưa có chợ), Hồi linh đan (nhập môn nhận `3`, thắng Boss `+1`, `!heal` hồi `30%` maxHP trừ 1 viên trong transaction). Không P2P, không đổi tiền thật, không ưu thế từ gift.

### 1.4 Trạng thái, World Boss & Tiểu Thiên Kiếp (GDD Mục 8–11)
- **State Machine:** `OFFLINE → SPAWNING → IDLE/CULTIVATING → MOVING → BOSS/TRIBULATION → RECOVERING → CULTIVATING` (cờ `SELECTING` chạy song song trong 60s). Inactive `5 phút` → ngừng tu vi/IDLE; `10 phút` → ẩn render. Mất connector → pause sau grace period `15s`.
- **World Boss — Bạch Lang Vương:** 8 trạng thái `SCHEDULED → ANNOUNCING(15s) → REGISTRATION(45s) → PREPARING(10s) → ACTIVE(<=120s) → RESOLVING → REWARDING → COMPLETED` (+ `CANCELED/FAILED`). Phút 5 lần đầu, lặp mỗi 10 phút; tối đa `100` slot; `Boss HP = 500 + 180 × N`, `DEF = 8`; tick đánh `2s` theo thứ tự ID ổn định; boss phản công `6s` chọn vòng luân phiên tối đa 3 người (`max(1, floor(24 + 2×min(N,20) - DEF))`); `defend` giảm `50%` trong `4s` (không nhân chồng với Hộ thể, lấy mức lớn nhất). Thưởng thắng (`200 XP, 100 Linh thạch, 1 Đan`) / thua (`30 XP, 10 Linh thạch`) chỉ cho người có đóng góp & không forfeit, khóa `UK(event_id, player_id, reward_kind)`.
- **Tiểu Thiên Kiếp:** 2 mốc (Luyện Khí → Trúc Cơ: `17%` maxHP/lôi; Trúc Cơ → Kim Đan: `22%` maxHP/lôi), thang `1000` HP nguyên, không RNG. Hàng chờ FIFO `(received_at, player_id)` tối đa `20`, chỉ `1` active, giữ `xp_reserved`, không mở khi Boss active hoặc sắp mở trong `30s`. Chuẩn bị `5s` → 5 lôi cách nhau `4s` → kết quả `5s`. Hộ thể tự động mặc định **bật** (`!hotheauto`, `!hotheauto on`, `!hotheauto off`; GM cấu hình chính sách mặc định); `!hothe` thủ công giảm `50%` cho đợt kế tiếp (hiệu lực `8s`, cooldown `8s`). Toàn bộ tính theo **server-side event timing (`SimulationClock`)**, hỗ trợ độ trễ livestream, không đòi hỏi phản ứng khớp khung hình animation, không dùng quà trả phí tăng xác suất. Thất bại mất `10%` XP giữ (floor) + cooldown `60s`; hủy/lỗi hệ thống hoàn `100%` XP giữ.
- **Lịch & Xung đột:** Tối đa 1 World Event active và 1 Personal Event active; Boss ưu tiên theo lịch nhưng không cắt kiếp đã chạy (lùi boss, không chạy bù hàng loạt).

### 1.5 Camera, Game Master, Quà tặng, Map & Acceptance (GDD Mục 12–19)
- 5 Camera (`CAM01`–`CAM05`), ưu tiên `90 > 80 > 50 > 30 > 20 > 10`, `min_hold 5s`, chuyển `0.6s`, manual override tự trả về auto sau `20s`.
- `!info` (hiển thị 3s, queue 20, TTL 60s), `!find` (5s, queue 10, TTL 90s).
- Gift chỉ cosmetic (1 hiệu ứng lớn, 3 nhỏ, queue 20, TTL 15s); TTS tùy chọn `1/5s`, cấm đọc raw chat.
- Map `TT_MAP001` có 6 zones (`spawn_gate`, `cultivation_court ≥100 slot`, `boss_arena`, `tribulation_platform`, `sect_hall`, `paths`).
- 18 tiêu chí nghiệm thu bắt buộc `AC01`–`AC18`.

---

## 2. Yêu cầu Platform phát sinh trực tiếp từ GDD

| Yêu cầu từ GDD | Module / Contract Platform đáp ứng |
|---|---|
| Monotonic clock không nhảy theo giờ hệ thống, đóng băng khi PAUSE | `core/clock` + `Game Session Manager` (`ADR-011`) |
| Optimistic version + transaction nguyên tử + checkpoint 10s + Crash Recovery (`CANCELED_RECOVERY`, `REWARDING` idempotent) | `Database Manager`, `Player Persistence`, `Reward Ledger` (`DATABASE_DESIGN.md`) |
| Snapshot + Revision Delta + bỏ delta cũ + yêu cầu snapshot khi gap | `API_CONTRACT.md` (`/ws/renderer`), `3D Runtime` |
| Hàng chờ FIFO hữu hạn có tie-break `player_id` + TTL + dedupe theo player | `Event Queue`, `Event Director`, `Overlay Engine` |
| Camera ưu tiên `90..10`, `min_hold`, smooth transition, 1 PiP có thể tắt, GM override 20s | `Camera Director` (`TDD.md`, `GAME_PLUGIN_CONTRACT.md`) |
| Bảo vệ Anti-P2W ở tầng kiến trúc (gift không thể sửa XP/chỉ số) | `Rule Engine`, `GamePlugin.handle_cosmetic_gift()` (`ADR-009`) |
| Quyền xóa dữ liệu theo yêu cầu nhưng giữ toàn vẹn sổ cái thưởng | `Player Manager` anonymize/tombstone policy (`ADR-012`) |
| Không tạo `InstancedMesh` mù quáng cho `SkinnedMesh` | Chiến lược LOD + visibility cap + benchmark GD09/GD19 (`ADR-008`) |
| Simulator bắt buộc + Live TikTok Connector là cổng tách biệt | `Event Simulator` (`GD04`) + `TikTok Connector` (`GD17`, `ADR-013`) |

---

## 3. Xung đột đã phát hiện & Phương án Đối chiếu (Conflicts & Reconciliations)

| ID | Nội dung xung đột / chênh lệch | Nguồn A vs Nguồn B | Hướng xử lý trong GD00 |
|---|---|---|---|
| **CONF-01** | Trùng tên & sở hữu bảng CSDL (`tt_sessions`, `tt_events`, `tt_reward_ledger`, `tt_processed_events`, `tt_action_audit`, `tt_worlds`) | GDD Mục 17 vs GD00 Mục 9 | Đã hợp nhất theo chỉ dẫn Mục 17 GDD (`ADR-005`): 14 bảng dùng chung thuộc Platform, 8 bảng `g_cultivation_*` thuộc GAME001. |
| **CONF-02** | Cấu trúc lộ trình (`TT-GD01..08` vs `GD00..GD20`) | GDD Mục 20 vs GD00 Mục 17 | Đã ánh xạ 1-N rõ ràng trong `docs/ROADMAP.md` (`ADR-006`), giữ `TT-AS01..09` độc lập. |
| **CONF-03** | Vị trí lưu file GDD gốc (`GDD_Tu_Tien_Online_v0.1.md` ở root vs `docs/games/cultivation_online/GDD.md`) | Thực tế workspace ban đầu vs GDD Mục 22 | **RESOLVED (`GD00-FIX01`, `ADR-007`):** Đã di chuyển bằng `git mv` sang `docs/games/cultivation_online/GDD.md`, xác minh SHA-256 trước/sau trùng khớp và cập nhật toàn bộ tham chiếu. |
| **CONF-04** | Bộ lệnh hộ thể tự động (`!hotheauto`, `!hotheauto on`, `!hotheauto off`) chưa được chuẩn hóa trong bảng lệnh Mục 6 GDD v0.1.0 | GDD Mục 10 vs GDD Mục 6 | **RESOLVED (`GD00-FIX01`, `ADR-015`, GDD Amendment `v0.1.1`):** Đã bổ sung đầy đủ `!hothe`, `!hotheauto`, `!hotheauto on`, `!hotheauto off`; mặc định bật, GM cấu hình mặc định, server-side event timing, không đổi thông số cân bằng gốc. |
| **CONF-05** | Yêu cầu GM xóa dữ liệu người chơi (Mục 5) vs cấm xóa lịch sử thưởng `!roi` (Mục 6) và toàn vẹn khóa ngoại `reward_ledger` | GDD Mục 5 vs Mục 6 & DB FK | Chốt chính sách `ADR-012`: `!roi` giữ toàn bộ dữ liệu; GM Data Erasure thực hiện ẩn danh hóa PII (`is_anonymized=1`) và giữ sổ cái ẩn danh. |

---

## 4. Thông số chưa được xác minh (Unverified Parameters — GDD Mục 21)

Toàn bộ các thông số sau được ghi nhận rõ là **đề xuất thiết kế chưa xác minh (Unverified / Playtest Proposed)**, không được xem là số đo thực tế hay quyết định đã khóa:
1. **Quyền tích hợp TikTok LIVE thật:** Khả năng nhận comment/gift/like/join ổn định và điều kiện phát game tự động trên tài khoản thực tế → `UNVERIFIED` (chờ GD17).
2. **Mục tiêu 100 nhân vật @ 30/60 FPS (`1080×1920`), Single WebGLRenderer, max 1 PiP, LOD, Resource Disposal & Phiên chạy liên tục 4 giờ + OBS:** Chưa có benchmark thực tế (máy dev hiện tại dùng RTX 4050 Laptop với `6141 MiB` tổng VRAM / `5820 MiB` khả dụng theo `nvidia-smi`, RAM khả dụng `3.14/15.73 GB`) → `UNVERIFIED` (chờ GD09/GD19).
3. **Thông số cân bằng số học:** Tốc độ `2 XP/s`, chi phí cảnh giới `100..3200`, `Boss HP = 500 + 180×N`, `DEF = 8`, sát thương phản công Boss, thiên lôi `17%/22%`, chính sách `auto-hộ thể` mặc định ON, idle `5m`/ẩn `10m` → `PROPOSED` (cần playtest và lưu theo `config_schema_version`).
4. **Phong cách mỹ thuật, tên gọi & Bản quyền Asset:** Phong cách Chibi, tên Thanh Vân Tông / Bạch Lang Vương chờ duyệt cuối; rig `humanoid_chibi_v1`, LOD `5-8k / 2-3k / 0.5-1k`, bản quyền nhạc/SFX/model → `UNVERIFIED` cho tới khi qua `Asset Validator` (`GD07` / `TT-AS`).
5. **Semantics Gift Streak của Provider:** Cơ chế chống trùng lặp gift streak phụ thuộc nhà cung cấp thực tế → `UNVERIFIED` (chờ GD17).
