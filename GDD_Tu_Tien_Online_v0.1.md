# GAME DESIGN DOCUMENT — TU TIÊN ONLINE

**LiveGame Studio | GAME001 | cultivation_online**  
**Phiên bản:** 0.1.0 — thiết kế MVP, chờ phê duyệt và cân bằng  
**Đối tượng:** Codex, Antigravity, game designer, technical artist, người vận hành livestream  
**Nền tảng:** Windows Desktop, Python/FastAPI, SQLite, TypeScript/Three.js, OBS/TikTok LIVE Studio.

## 1. Tầm nhìn sản phẩm

Tu Tiên Online (tên quốc tế đề xuất: Immortal Ascension) là game tu tiên 3D dạng idle RPG cộng đồng, điều khiển bằng bình luận trên TikTok LIVE. Một thế giới chung, một màn hình phát sóng dọc; mỗi người xem sở hữu một nhân vật và tiến trình riêng. Không yêu cầu người xem tải ứng dụng, mở tài khoản game riêng hoặc gửi quà trả phí để chơi.

Ba trụ cột: dễ nhập môn trong vài giây; luôn có hoạt động trực quan để xem; tiến trình có ý nghĩa qua nhiều phiên live. Chủ live là Game Master (Thiên Đạo), không phải người điều khiển từng nhân vật. Tất cả chỉ số, thời lượng và ngưỡng trong tài liệu là cấu hình đề xuất để playtest, chưa phải kết quả benchmark.

## 2. Phạm vi MVP và ranh giới

| Trong MVP | Sau MVP |
|---|---|
| Một map Thanh Vân Tông, hai nhân vật nam/nữ | Nhiều map, Tiên giới, linh thú |
| Nhập môn, tu luyện tự động, 4 cảnh giới | 14 cảnh giới, hệ thống linh căn đầy đủ |
| Ba nghề với kỹ năng cơ bản | Cây kỹ năng, chế tạo, luyện đan sâu |
| Một World Boss Bạch Lang Vương | Nhiều boss, phó bản, PvP |
| Đột phá và tiểu thiên kiếp | Thiên kiếp nhiều giai đoạn, phi thăng |
| Camera Director, overlay, Game Master, scheduler | AI NPC hội thoại, nhiều máy chủ |
| Tiến trình lưu local, simulator, connector được cấp quyền | Cloud, marketplace, thuê bao |

Không xây AI Asset Generator, Meshy/Tripo integration hoặc Blender runtime trong ứng dụng. Asset được sản xuất bằng prompt riêng, nhập qua Asset Contract. Không triển khai tính năng đánh cược, đổi thưởng tiền thật hoặc quà trả phí ảnh hưởng kết quả chiến đấu/đột phá.

## 3. Vai trò và màn hình

| Đối tượng | Quyền và trải nghiệm |
|---|---|
| Người xem | Gửi lệnh chat, điều khiển nhân vật của chính mình, xem chung livestream |
| Game Master | Chọn phiên, kết nối, cấu hình lịch, quản lý sự kiện/camera/kiểm duyệt, dừng khẩn cấp |
| Backend | Nguồn sự thật duy nhất về trạng thái, thời gian, luật chơi và phần thưởng |
| Renderer | Hiển thị trạng thái, animation và hiệu ứng; không quyết định kết quả |
| Narrator | Thông báo từ template; TTS tùy chọn, không có quyền sửa gameplay |

Chỉ có hai bề mặt chính: Game Master Panel riêng trên desktop và Game Output 1080×1920 dùng chung để capture. Camera ảo không phải màn hình riêng cho mỗi người. Một PiP tối đa trong MVP, có thể tắt để tiết kiệm GPU. Không chiếu panel điều khiển, credential hoặc dữ liệu nội bộ.

## 4. Vòng lặp gameplay

Nhập môn → chọn ngoại hình/nghề → tự tu luyện → tích lũy tu vi → tham gia hoạt động cộng đồng → nhận tài nguyên → đột phá → tiếp tục tu luyện. Không bắt người xem spam chat. Người chơi mới có thể tham gia bất cứ lúc nào, kể cả khi boss đang diễn ra. Tiến trình được lưu qua các buổi live; không cộng tu vi trong thời gian server tắt.

## 5. Nhập môn và nhận diện người chơi

- Dùng ID ổn định do nguồn sự kiện được cấp quyền cung cấp, kết hợp namespace kênh/world; không dùng nickname làm khóa. Một hồ sơ cho mỗi người trong một world. Nickname/avatar có thể thay đổi; không suy luận giới tính từ hồ sơ.
- `!join`: nếu mới, tạo hồ sơ mặc định trong một transaction, spawn nam tu sĩ mặc định và nghề Kiếm Tu; mở cửa sổ chọn 60 giây. Nếu cũ, khôi phục nhân vật mà không reset dữ liệu. `!nam`/`!nu` có thể nhập môn trực tiếp. Không tạo hồ sơ chỉ vì sự kiện join phòng hoặc gift.
- `!kiem`, `!dan`, `!the`: chọn nghề trong 60 giây đầu; sau đó chỉ đổi khi GM mở chế độ đổi nghề ngoài chiến đấu. Ngoại hình có thể đổi ngoài event qua lệnh tương ứng, không làm mất tiến trình.
- Spawn tại sơn môn, tự đi đến vị trí tu luyện còn trống. Nếu hết slot render, vào danh sách chờ hình ảnh nhưng gameplay vẫn hoạt động.
- Mỗi tên hiển thị giới hạn 20 ký tự hiển thị, escape HTML, lọc nội dung không phù hợp; có thể dùng bí danh. Cho phép opt-out `!roi`, lưu hồ sơ, ngừng hoạt động và ẩn khỏi scene; GM có thao tác xóa dữ liệu theo yêu cầu.
- Không yêu cầu mở giao diện chọn nhân vật riêng. Banner nhập môn cố định/luân phiên, thông báo gộp khi có nhiều người mới.

## 6. Lệnh tương tác (MVP)

Lệnh không phân biệt hoa thường, trim khoảng trắng; hỗ trợ alias tiếng Việt có dấu qua bảng ánh xạ tường minh. Không dùng LLM để suy diễn lệnh. Một comment tối đa một lệnh; cooldown theo player và nhóm lệnh. Bình luận thường không mặc định tạo hành động.

| Lệnh | Hành động | Cooldown / điều kiện |
|---|---|---|
| !join | Tạo/khôi phục nhân vật | 5s, idempotent |
| !nam / !nu | Ngoại hình | 10s, ngoài event |
| !kiem / !dan / !the | Nghề | 10s, cửa sổ chọn hoặc GM cho phép |
| !tuluyen | Tự tu luyện | 3s, ngoài event |
| !nghi | Nghỉ, không tăng tu vi | 3s, ngoài event |
| !dotpha | Kiểm tra và yêu cầu đột phá | 10s, đủ điều kiện |
| !dokiep | Alias !dotpha khi bước đột phá cần kiếp | 10s, cùng cooldown |
| !boss | Đăng ký boss | 5s, giai đoạn đăng ký |
| !skill | Kỹ năng nghề | 12s, chỉ trong boss |
| !defend | Phòng thủ | 8s, chỉ trong boss |
| !heal | Dùng 1 đan hồi phục | 20s, có vật phẩm |
| !hothe | Hộ thể | 8s, chỉ trong kiếp |
| !info / !status | Thẻ cá nhân | 60s, hàng chờ overlay |
| !find / !me | Highlight nhân vật | 60s, không ngắt boss |
| !rank | Bảng xếp hạng chung | 60s |
| !help | Hướng dẫn luân phiên | 30s |
| !roi | Rời game, lưu tiến trình | Không được xóa lịch sử thưởng |

Lệnh hợp lệ nhưng không đủ điều kiện trả mã lý do để GM xem và thông báo gọn, không phát TTS cho mọi lỗi. Tất cả lệnh được định tuyến bằng ID người gửi; người xem không được chỉ định ID người khác để điều khiển.

## 7. Tiến trình và kinh tế

### 7.1 Cảnh giới

| Bậc | Cảnh giới | Tu vi mỗi lần tiến tầng | HP gốc / ATK / DEF |
|---|---|---:|---|
| 0 | Phàm Nhân (một tầng) | 100 | 100 / 12 / 4 |
| 1 | Luyện Khí (4 tầng) | 200, 300, 400, 600 | 180 / 20 / 8 |
| 2 | Trúc Cơ (4 tầng) | 800, 1000, 1200, 1600 | 300 / 32 / 14 |
| 3 | Kim Đan (4 tầng) | 2000, 2500, 3200, MAX | 500 / 50 / 22 |

Bốn tầng: Sơ kỳ, Trung kỳ, Hậu kỳ, Viên mãn. Chi phí ở bảng là chi phí để rời tầng hiện tại. Luyện Khí viên mãn → Trúc Cơ sơ kỳ là tiểu thiên kiếp; Trúc Cơ viên mãn → Kim Đan sơ kỳ là tiểu thiên kiếp khó hơn. Kim Đan viên mãn là giới hạn MVP, không tự mở Nguyên Anh. Các bậc tương lai: Nguyên Anh, Hóa Thần, Luyện Hư, Hợp Thể, Đại Thừa, Độ Kiếp, Chân Tiên, Kim Tiên, Tiên Vương, Tiên Đế.

Tu vi là số nguyên, tích lũy 2/giây khi CULTIVATING và hiện diện theo chính sách hoạt động; tick backend 1 giây. Không cộng đồng thời khi đánh boss, di chuyển hoặc độ kiếp. XP dư được giữ khi đột phá; ở MAX vẫn hiển thị max, không tích lũy vô hạn. Giới hạn XP tồn = 2 × chi phí tầng hiện tại; khi MAX dừng tăng. Các lần đột phá thường trừ đúng chi phí và tăng một tầng nguyên tử; không tự động đột phá nếu chưa gửi lệnh. Cooldown đột phá thường 10s.

### 7.2 Nghề

| Nghề | Điều chỉnh chỉ số gốc | Kỹ năng boss (12s) |
|---|---|---|
| Kiếm Tu | ATK ×1.20 | Kiếm khí: 2 × sát thương cơ bản |
| Đan Tu | HP ×1.10 | Hồi 15% HP tối đa cho mình và 2 đồng đội HP thấp nhất còn sống |
| Thể Tu | HP ×1.30, DEF ×1.20 | Hộ thể: giảm 50% sát thương nhận trong 6s |

Mỗi tầng sau Sơ kỳ tăng HP/ATK/DEF gốc 5% cộng dồn tuyến tính, làm tròn xuống sau khi áp dụng nghề. Không có ưu thế từ gift. Linh căn và trang bị đầy đủ nằm ngoài MVP; có thể dành field cấu hình nhưng không giả lập chức năng chưa làm.

### 7.3 Tài nguyên

- Linh thạch: số nguyên không âm, phần thưởng gameplay, không có giá trị tiền thật. MVP lưu và hiển thị, chưa có chợ giao dịch.
- Hồi linh đan: người mới nhận 3, mỗi boss thắng nhận 1; `!heal` hồi 30% HP tối đa, trừ 1 viên trong transaction. Không dùng khi đã chết hoặc đầy HP.
- Không giao dịch P2P, không chuyển quà TikTok thành tài nguyên sức mạnh, không hoàn tiền hay đổi thưởng ngoài game.

## 8. Trạng thái nhân vật

OFFLINE → SELECTING → SPAWNING → IDLE/CULTIVATING → MOVING → BOSS/ TRIBULATION → RECOVERING → CULTIVATING. Có thể chuyển về OFFLINE từ trạng thái thường; đang event thì hoàn tất/forfeit theo quy tắc event, không nhận thưởng hai lần. Trạng thái chọn ngoại hình không chặn spawn. SELECTING có thể là cờ song song trong 60 giây; không yêu cầu chuyển trạng thái gameplay về SELECTING khi đã spawn.

Một player chỉ có một hoạt động gameplay chính. Render culling không làm đổi trạng thái gameplay. Hệ thống quản lý last_seen_at từ sự kiện xác thực được của người xem: sau 5 phút không tương tác, ngừng tích lũy tu vi và đưa vào idle; sau 10 phút ẩn render. Đây là suy đoán hoạt động chứ không khẳng định người xem đã rời live. Khi nhận lệnh hợp lệ tiếp theo, khôi phục hoạt động. Event đang diễn ra có thể kết thúc theo luật đã đăng ký. Nếu connector mất kết nối, tạm ngừng thưởng và đồng hồ gameplay sau grace period 15s.

## 9. World Boss — Bạch Lang Vương

### 9.1 Vòng đời và thời lượng

SCHEDULED → ANNOUNCING (15s) → REGISTRATION (45s) → PREPARING (10s) → ACTIVE (tối đa 120s) → RESOLVING → REWARDING → COMPLETED. CANCELED/FAILED là trạng thái kết thúc riêng. Boss đầu tiên sau 5 phút live, sau đó theo lịch mỗi 10 phút tính từ lần đăng ký trước, không chạy chồng. Nếu hết đăng ký mà không có ai, hủy không thưởng, trở về tu luyện. Tối thiểu một người tham gia; người mới trong trận phải chờ boss tiếp theo. Số slot chiến đấu mặc định 100, vượt giới hạn thì thông báo không có chỗ. Không teleport người chưa đăng ký.

### 9.2 Luật chiến đấu

- N là số người đăng ký hợp lệ tại thời điểm đóng đăng ký. Chụp snapshot chỉ số người chơi; khóa thay đổi nghề trong trận. Boss HP = 500 + 180 × N; DEF = 8. Đây là công thức thử nghiệm cần benchmark theo phân bố cảnh giới.
- Tick chiến đấu 2 giây, xử lý người chơi còn sống theo thứ tự ID ổn định. Sát thương auto = max(1, floor(ATK − boss_DEF)). Kỹ năng Kiếm Tu thêm một đòn bằng 2 lần sát thương auto; Đan Tu/Thể Tu như mục 7. Kỹ năng không tự spam; cooldown dùng đồng hồ simulation.
- Boss phản công mỗi 6 giây: chọn tối đa 3 người còn sống bằng vòng luân phiên ID, sát thương max(1, floor(24 + 2 × min(N,20) − DEF)). Khi defend, giảm 50% trong 4s; nếu trùng hộ thể thì áp dụng mức giảm lớn nhất, không nhân chồng. Damage/heal clamp về [0, maxHP].
- Bắt đầu event với HP đầy; chết thì ngừng tấn công, không hồi sinh trong trận. Khi Boss HP = 0 → thắng; nếu hết thời gian hoặc toàn bộ người chơi chết → thất bại. Nếu cùng tick, xử lý sát thương người chơi trước phản công; boss chết thì không phản công.
- Người đăng ký rời game giữa trận bị forfeit và không nhận thưởng; mất tương tác không tự coi là forfeit. Kết thúc, nhân vật quay về tu luyện, HP hồi đầy sau 10s phục hồi.

### 9.3 Phần thưởng

Thắng: mỗi người tham chiến có đóng góp (gây sát thương, hồi phục hữu ích hoặc phòng thủ giảm được sát thương) và không forfeit nhận 200 tu vi, 100 linh thạch, 1 hồi linh đan. Thua: 30 tu vi, 10 linh thạch cho người đủ điều kiện. Tu vi vượt cap bị giới hạn theo mục 7. Không nhận thưởng cho người chỉ đăng ký rồi rời. Mỗi player/event chỉ được cấp một lần; unique key (event_id, player_id, reward_kind). Ledger và cập nhật số dư cùng transaction. Xếp hạng damage chỉ để vinh danh, không ảnh hưởng phần thưởng MVP; tie-break theo player_id. Hiển thị kết quả 8s, không cản gameplay.

## 10. Đột phá và Tiểu Thiên Kiếp

Các lần tăng tầng thường: kiểm tra đủ XP, khóa player, trừ XP và tăng tầng trong transaction; phát aura 3s và toast. Hai lần vượt đại cảnh giới cần event riêng. Người chơi bình luận !dotpha/!dokiep; kiểm tra điều kiện, tạo yêu cầu idempotent, giữ (reserve) XP cần thiết để không tiêu hai lần. Hàng chờ FIFO theo thời điểm nhận và player_id; chỉ một kiếp active trong MVP, tối đa 20 yêu cầu chờ. Không bắt đầu khi boss sắp mở trong vòng 30s hoặc đang active. Người chơi tiếp tục hoạt động thường khi chờ nhưng XP đã giữ không được dùng cho yêu cầu khác.

Kiếp: chuẩn bị 5s, 5 thiên lôi cách nhau 4s, kết quả 5s. HP ban đầu 100% riêng cho kiếp, không dùng HP trận boss. Thiên lôi Trúc Cơ gây 17% HP tối đa/đợt; Kim Đan 22%/đợt. `!hothe` giảm 50% sát thương đợt kế tiếp, hiệu lực tối đa 8s và tiêu hao khi trúng lôi; cooldown 8s. Tất cả tính theo đơn vị HP nguyên (thang 1000), làm tròn xuống. HP > 0 sau lôi cuối là thành công. Không có RNG hoặc yêu cầu quà trả phí. Trúc Cơ có thể vượt tự động; Kim Đan cần ít nhất một lần hộ thể đúng lúc hoặc chính sách hỗ trợ miễn phí được cấu hình sau playtest.

Thành công: tiêu XP giữ, tăng cảnh giới, thông báo và lưu nguyên tử. Thất bại: tiêu 10% XP giữ (floor), giải phóng phần còn lại, cooldown thử lại 60s, hồi phục 10s. Hủy trước ACTIVE: giải phóng toàn bộ XP; nếu lỗi hệ thống trong ACTIVE: hủy và hoàn lại toàn bộ XP giữ, không phạt. Không chạy lại event đã kết thúc. Lệnh hộ thể nên được thông báo sớm vì độ trễ livestream; trong MVP có thể bật auto-hộ thể miễn phí cho mọi người để tránh bất lợi do mạng (mặc định bật, tắt qua !hotheauto off khi triển khai alias). Manual chỉ là lựa chọn chơi, không phải điều kiện trả phí.

## 11. Lịch sự kiện và xung đột

| Thời điểm từ bắt đầu | Hoạt động |
|---|---|
| 0–5 phút | Nhập môn liên tục, tu luyện, hướng dẫn |
| Phút 5 | Đăng ký và đánh boss đầu tiên |
| Sau boss | Kết quả, tu luyện, xử lý hàng chờ kiếp |
| Phút 15, 25, 35… | Boss tiếp theo nếu không có event active |
| Mỗi 5 phút | Luân phiên bảng hướng dẫn/xếp hạng, không khóa gameplay |
| Dừng live | Ngừng nhận lệnh mới, hoàn tất/hủy có kiểm soát, lưu snapshot |

World event chỉ một active; kiếp cá nhân chỉ một active; ưu tiên boss theo lịch nhưng không cắt kiếp đã bắt đầu. Nếu trùng, lùi boss tới khi kiếp hoàn tất; không chạy bù hàng loạt. Người đang chờ kiếp được tham gia boss, nhưng không được khởi động kiếp khi đã đăng ký/đang chiến đấu. GM có thể mở event sớm khi idle, không bỏ qua điều kiện reward. PAUSE đóng băng simulation clock, không cộng XP; STOP hủy event chưa kết thúc theo quy tắc refund, lưu dữ liệu. Không dùng đồng hồ hệ thống thay cho monotonic clock trong tính toán tick.

## 12. Màn hình livestream và Camera Director

Output chuẩn dọc 1080×1920, safe area điều chỉnh được vì UI TikTok khác theo thiết bị. Bố cục đề xuất: header nhỏ (tên game, số đạo hữu hoạt động, event kế tiếp); viewport thế giới chiếm khoảng 65–75%; footer chứa hướng dẫn lệnh và một overlay context. Không đặt thông tin quan trọng sát mép phải hoặc đáy. Không hiển thị riêng cho từng người chơi.

| Camera | Nội dung | Quy tắc |
|---|---|---|
| CAM01 | Toàn cảnh Thanh Vân Tông | Mặc định |
| CAM02 | Tu luyện / người mới | Luân phiên khi idle |
| CAM03 | Độ kiếp | PiP hoặc camera chính khi không có boss |
| CAM04 | Boss | Camera chính khi ACTIVE |
| CAM05 | Nhân vật nổi bật | Từ hàng chờ !find, khi idle |

Ưu tiên camera: Boss 90 > kiếp 80 > đột phá 50 > yêu cầu cá nhân 30 > người mới 20 > idle 10. Giữ shot tối thiểu 5s, chuyển mượt 0.6s; boss không bị ngắt bởi !find. !info hiển thị tối đa 3s, queue 20, TTL 60s; gộp theo player và từ chối khi đầy. !find highlight 5s, queue 10, TTL 90s; tối đa một yêu cầu/player/60s. Overlay hết hạn bỏ qua, không ảnh hưởng trạng thái game. Tên nhân vật chỉ hiện ở người gần camera, người nổi bật hoặc khi yêu cầu; giảm chồng chữ. Camera không được điều khiển gameplay.

## 13. Game Master Control Panel

Chế độ mặc định Semi-auto: scheduler chạy theo cấu hình, GM có quyền tạm dừng, triệu hồi boss khi hợp lệ, điều chỉnh camera hoặc hủy event. Auto vẫn cần người vận hành giám sát; Manual tắt lịch tự động nhưng giữ game tick và luật an toàn. Panel riêng gồm: trạng thái connector, session clock, số player hoạt động, danh sách chờ, event hiện tại/kế tiếp, camera preview, bảng lệnh lỗi, thống kê hiệu năng, nút pause/resume/stop, chế độ giả lập, kiểm duyệt tên, log audit. Thao tác hủy/reset có xác nhận; không reset tiến trình chỉ vì đổi phiên live. Nút chuyển camera manual tự trả về auto sau 20s hoặc khi GM chọn; không đổi kết quả event. Cấu hình số liệu cân bằng chỉ có hiệu lực ở event mới, không thay giữa trận.

## 14. Quà tặng, like, thông báo và âm thanh

Quà chỉ kích hoạt hiệu ứng cosmetic có cấu hình (hoa sen, kiếm bay, linh quang, rồng trang trí), không cộng XP/ATK, không mua lượt độ kiếp hoặc xác suất thành công. Like có thể tăng cường độ hiệu ứng toàn map với giới hạn tốc độ, không ảnh hưởng sức mạnh. Không khuyến khích spam hoặc gây áp lực tặng quà. Gift streak và event trùng cần chuẩn hóa theo semantics nhà cung cấp; chưa xác minh thì không cấp hiệu ứng trùng. Giới hạn 1 hiệu ứng lớn đồng thời, 3 hiệu ứng nhỏ, queue 20, TTL 15s, gộp hiệu ứng trùng. Template thông báo tiếng Việt; TTS tùy chọn, tối đa 1 thông báo/5s, không đọc nội dung chat chưa kiểm duyệt. Nhạc/âm thanh cần quyền sử dụng livestream. Tắt hoặc giảm VFX nhấp nháy mạnh theo cài đặt.

## 15. Map và mỹ thuật

MAP TT_MAP001 Thanh Vân Tông: phong cách Chibi 3D tiên hiệp, nền núi mây, mái ngói xanh ngọc, đá sáng, vàng nhạt, điểm nhấn linh khí. Bố cục dọc, cổng ở dưới, đại điện ở trên, sân tu luyện trung tâm, đấu trường boss phía phải hoặc khu phụ, độ kiếp đài tách biệt. V1 có thể dùng cùng scene với camera riêng cho đấu trường. Map gameplay phải tách mesh trang trí, collision, walkable areas và anchor; không tạo cả map thành một mesh vô cấu trúc.

| Zone ID | Chức năng |
|---|---|
| spawn_gate | Vị trí xuất hiện |
| cultivation_court | Vị trí ngồi tu luyện, tối thiểu 100 slot logic |
| boss_arena | Boss spawn, vị trí vòng cung người tham chiến |
| tribulation_platform | Anchor một người độ kiếp |
| sect_hall | Đại điện NPC, trang trí MVP |
| paths | Waypoint/navmesh nối khu vực |

Asset tối thiểu: TT_CHAR001 đệ tử nam, TT_CHAR002 đệ tử nữ, TT_BOSS001 Bạch Lang Vương, TT_MAP001, cổng/đại điện/sàn đá/đài tu luyện/đài kiếp/cây/núi/đèn lồng, kiếm và hiệu ứng aura/kiếm khí/thiên lôi/boss hit. Animation: idle, walk, run, meditation, cast, sword_attack, hit, defeat, celebrate; boss idle, attack, hit, defeat. Placeholder hợp lệ cho giai đoạn code; production asset riêng theo prompt TT-AS. GLB/glTF 2.0, Y-up runtime, mét, pivot chân, humanoid rig chuẩn chung khi tương thích, texture 512–1024 ưu tiên đám đông, 2K cho boss nếu cần. LOD nhân vật mục tiêu 5–8k / 2–3k / 0.5–1k triangles. Không khẳng định rig hoặc LOD đạt trước kiểm thử. Asset manifest có hash, version, license, provenance, dependencies và animation names. Asset production không chứa API runtime trong platform.

## 16. Kiến trúc gameplay và tích hợp platform

Dùng Game Plugin Contract hiện có của GD01; không viết lại Event Bus, Asset Registry, Player Manager hoặc runtime chung. Plugin ID cultivation_online. Domain thuần Python, application services quản lý giao dịch, repository SQLite, adapter nhận event TikTok hoặc simulator, Three.js chỉ nhận snapshot/delta. Module riêng: commands, player_progression, cultivation, professions, boss, tribulation, scheduler, rewards, camera_intents, world_config, persistence. Tất cả timer và bảng cân bằng được inject để kiểm thử xác định. Backend phát snapshot ban đầu rồi delta theo revision; frontend bỏ delta cũ, yêu cầu snapshot khi gap. Không phát thông tin bí mật vào overlay.

Envelope event tối thiểu: event_id, source, source_event_id (nếu có), channel_id, live_session_id, player_external_id, event_type, received_at, occurred_at (nếu đáng tin), payload, schema_version. Normalize, validate, dedupe trước parser; không suy diễn sự kiện thiếu. Nếu provider không có ID sự kiện ổn định, adapter phải ghi rõ phương pháp chống trùng và giới hạn; không tự coi hai comment giống nhau là một nếu không có bằng chứng. Chỉ tích hợp nguồn được cấp quyền. API và khả năng nhận chat/gift/like/join thật chưa được xác nhận cho tài khoản người dùng; simulator là bắt buộc, live connector là gate riêng.

## 17. Dữ liệu lưu trữ

Tên bảng logic đề xuất, phải reconcile với schema platform và Alembic; không tạo trùng bảng chung.

| Bảng | Nội dung và khóa |
|---|---|
| tt_profiles | world_id + player_id unique; appearance, profession, created_at, last_seen_at |
| tt_progress | profile_id PK/FK, realm, stage, xp, xp_reserved, stones, version |
| tt_inventory | profile_id + item_id unique, quantity >= 0 |
| tt_worlds | world_id, channel scope, config_version |
| tt_sessions | session_id, world_id, state, started_at, ended_at |
| tt_events | event_id, session_id, type, state, deadline, config snapshot |
| tt_participants | event_id + profile_id unique, HP, damage, healing, status |
| tt_tribulation_queue | request_id, profile_id, reserved_xp, status, created_at |
| tt_reward_ledger | event_id + profile_id + reward_kind unique, amount, created_at |
| tt_processed_events | source namespace + source_event_id unique khi có ID |
| tt_action_audit | action_id, actor, action, outcome, timestamp; redact secrets |

SQLite transaction cho đăng ký, XP, đột phá, reward; optimistic version hoặc serialization theo player. Checkpoint tiến trình mỗi 10s và ngay khi thay cảnh giới, vật phẩm, reward, kết thúc session. Không tạo reward mới từ renderer. Recovery: khi restart, event active chưa hoàn tất chuyển CANCELED_RECOVERY, giải phóng XP giữ, không cấp thưởng mới; ledger đã commit giữ nguyên. Event REWARDING khôi phục idempotent theo ledger và outcome đã lưu. Player về IDLE, chỉ resume tu luyện khi phiên khởi động và người chơi còn đủ điều kiện. Không bù XP offline. Backup local, quyền xóa hồ sơ, log retention cấu hình; không lưu raw chat lâu hơn nhu cầu vận hành.

## 18. Hiệu năng và kiểm thử

Mục tiêu MVP: 100 player logic đồng thời, render 30 FPS ở 1080×1920 khi OBS capture trên cấu hình máy mục tiêu chưa xác định; 60 FPS là mục tiêu nâng cao. Benchmark 1/20/50/100 nhân vật, đo p50/p95 frame time, CPU/GPU/VRAM, draw calls, event queue depth và latency. Giảm LOD/VFX/nametag trước giảm gameplay; reuse geometry/material, pool effect, culling. Skinned mesh cần kỹ thuật batching tương thích, không giả định instancing thường áp dụng được. Backend tick không phụ thuộc frame rate. Test burst 100 lệnh/s trong 30s, đo queue và không mất sự kiện được chấp nhận; đây là tải thử nghiệm, không phải dự đoán traffic.

## 19. Tiêu chí nghiệm thu (acceptance)

| ID | Kịch bản bắt buộc | Kết quả mong đợi |
|---|---|---|
| AC01 | 20 người !join cùng lúc | 20 hồ sơ độc lập, không duplicate |
| AC02 | Rejoin sau restart | Giữ cảnh giới, XP, nghề, inventory |
| AC03 | Tu luyện 10 tick, không chạm cap | +20 XP; pause không cộng |
| AC04 | Đủ/thiếu XP đột phá | Tăng đúng tầng hoặc từ chối, không trừ sai |
| AC05 | 20 người yêu cầu kiếp | FIFO, không giữ XP hai lần, boss không chồng |
| AC06 | Kiếp thất bại/hủy/restart | Penalty/refund đúng, không mất XP ngoài luật |
| AC07 | Boss thắng/thua/hết giờ | Kết thúc xác định, trả đúng reward |
| AC08 | Replay event và restart lúc reward | Không cấp thưởng trùng |
| AC09 | Lệnh sai/spam | Không crash, cooldown đúng, queue hữu hạn |
| AC10 | !info/!find khi boss | Không cắt camera boss, overlay TTL đúng |
| AC11 | Renderer disconnect/reconnect | Snapshot đúng, không reset gameplay |
| AC12 | Mất nguồn sự kiện | Pause theo grace period, resume có kiểm soát |
| AC13 | Game Master pause/stop | Đồng hồ đóng băng, dữ liệu lưu, không orphan process |
| AC14 | GLB thật/placeholder | Load đúng version, lỗi thiếu asset có fallback rõ |
| AC15 | Benchmark 100 player với OBS | Báo số đo thật và cấu hình, không bịa FPS |
| AC16 | Gift gửi lặp | Chỉ cosmetic, không đổi XP/HP/ATK, dedupe |
| AC17 | Output dọc trên thiết bị thật | Text dễ đọc, không che bởi UI TikTok |
| AC18 | TikTok live authorized smoke test | Chat điều khiển đúng nhân vật; quyền và hạn chế ghi rõ |

PASS cho bản live chỉ khi mọi tiêu chí bắt buộc đã chạy và đạt. Nếu chưa có connector hoặc asset production thì PARTIAL/BLOCKED; simulator pass không đồng nghĩa live pass. Báo cáo phân biệt PASS/FAIL/SKIP/NOT RUN.

## 20. Lộ trình giao việc cho Codex và Antigravity

GD01 platform giữ nguyên; cập nhật ROADMAP và PROJECT_SPEC để GAME001 là Tu Tiên Online, không triển khai game production trong GD01. Sau khi platform core và contracts đạt acceptance, triển khai các task riêng theo dependency:

| Task | Đầu ra |
|---|---|
| TT-GD01 | Plugin skeleton, config schema, domain model, simulator onboarding |
| TT-GD02 | Player progression, persistence, cultivation, commands |
| TT-GD03 | Shared scene, map anchors, animation, camera, overlay |
| TT-GD04 | Scheduler, Game Master, queue và lifecycle |
| TT-GD05 | Boss combat, profession skills, reward ledger |
| TT-GD06 | Breakthrough, tribulation, recovery |
| TT-GD07 | Full simulation, import production assets, balancing |
| TT-GD08 | Authorized live connector, OBS, E2E, benchmark |

Codex phụ trách domain/backend/test; Antigravity review độc lập và phụ trách UI/render theo file ownership. Dùng branch/worktree tách biệt, không cùng sửa một file. Mỗi task yêu cầu actual test, commit, delivery report và regression; không tự merge main. Asset task độc lập: TT-AS01 style, TT-AS02/03 nhân vật, TT-AS04 rig/animation, TT-AS05/06 map concept/props, TT-AS07 map, TT-AS08 VFX, TT-AS09 boss. Chỉ nhập asset đã validate.

## 21. Quyết định cần xác nhận trước production

- Phong cách Chibi tiên hiệp, tên Thanh Vân Tông/Bạch Lang Vương, ba nghề và công thức số liệu là đề xuất thiết kế; cần người dùng duyệt.
- Xác minh quyền nhận event TikTok và điều kiện phát game tự động với nguồn chính thức/được cấp quyền; chưa có bằng chứng trong tài liệu này.
- Chốt hardware target và benchmark cùng OBS; 100 player là mục tiêu, không phải năng lực đã chứng minh.
- Playtest độ trễ chat, auto-hộ thể, tốc độ XP, HP boss, thời lượng sự kiện; chỉnh config trước khóa balance.
- Kiểm tra license từng asset, nhạc và animation. Không tuyên bố model 3D hoặc tính năng đã hoàn thành chỉ từ concept.

## 22. Quản lý thay đổi

Lưu tài liệu vào docs/games/cultivation_online/GDD.md. GDD là nguồn luật gameplay; API Contract và Asset Contract của platform là nguồn chuẩn giao tiếp. Nếu có xung đột, ghi ADR/DECISIONS và yêu cầu review trước khi thay đổi. Mọi thông số cân bằng có config version; thay đổi cần changelog và regression test. Không mở rộng scope MVP trong quá trình thực hiện nếu chưa được phê duyệt.
