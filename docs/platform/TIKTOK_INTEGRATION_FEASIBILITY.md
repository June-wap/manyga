# TIKTOK LIVE INTEGRATION FEASIBILITY STUDY — LIVEGAME STUDIO

**Phiên bản:** 1.0.0 (GD00 Baseline)  
**Trạng thái tích hợp hiện tại:** `NOT IMPLEMENTED (GATED AT GD17)`  
**Nguyên tắc trung thực:** Không tuyên bố khả năng nhận bình luận, quà tặng, lượt thích hay sự kiện vào phòng từ TikTok LIVE thật nếu chưa xác minh chính thức trên tài khoản và nguồn được cấp quyền của chủ dự án.

---

## 1. Bối cảnh & Ràng buộc pháp lý / bảo mật

LiveGame Studio cần tiếp nhận sự kiện tương tác từ khán giả (ưu tiên bình luận `!join`, `!boss`, `!dotpha`, ... và tùy chọn quà tặng cho hiệu ứng cosmetic). Tuy nhiên, việc truy cập luồng sự kiện TikTok LIVE chịu sự kiểm soát nghiêm ngặt của **TikTok Developer Terms of Service**, chính sách quyền truy cập API theo khu vực/đối tác và giới hạn bảo vệ chống tự động hóa trái phép.

**Quyết định bất di bất dịch (`ADR-013`):**
- Không triển khai TikTok Connector thật trong `GD00`–`GD16`.
- Tuyệt đối không sử dụng phương pháp scraping trái phép, giả mạo chữ ký ứng dụng, đánh cắp cookie phiên đăng nhập hay thu thập credential không được cấp quyền.
- Toàn bộ kiến trúc Platform được tách rời khỏi nhà cung cấp sự kiện thông qua lớp `ConnectorAdapter` → `Event Gateway` → `NormalizedEvent`.

---

## 2. Phân loại rạch ròi khả năng tiếp nhận sự kiện

### 2.1 Official Documented Capabilities (Khả năng chính thức có tài liệu — Cần kiểm tra phạm vi tài khoản)
- **TikTok for Developers (Login Kit, Display API, Content Posting API, Research API, Commercial/Partner APIs):**
  - Cung cấp OAuth2 chuẩn và quản lý dữ liệu tài khoản/video theo phạm vi được cấp phép.
  - **Lưu ý thực tế:** Tại thời điểm thiết kế `GD00`, bộ API công khai đại trà của TikTok for Developers **không tự động cấp một WebSocket công khai mở sẵn cho mọi cá nhân đọc luồng comment/gift thời gian thực của TikTok LIVE**; quyền truy cập luồng LIVE tương tác thường thuộc nhóm chương trình **TikTok LIVE Interactive / Partner / Agency / TikTok LIVE Studio integration** yêu cầu đăng ký và phê duyệt riêng.
  - **Trạng thái đối với tài khoản dự án:** `UNVERIFIED` — cần chủ dự án kiểm tra tư cách tài khoản/đối tác và cung cấp tài liệu cấp quyền tại cổng `GD17`.

### 2.2 Authorized Third-Party Providers / Middleware (Nhà cung cấp trung gian được cấp quyền)
- Một số nền tảng dịch vụ livestream / streaming middleware thương mại (được TikTok cấp quyền đối tác hoặc cung cấp webhook/WebSocket hợp lệ theo điều khoản dịch vụ) có thể chuyển tiếp sự kiện livestream (ví dụ comment, gift, follow/like) về ứng dụng local qua API/WebSocket có khóa xác thực.
- **Điều kiện chấp nhận để tích hợp ở `GD17`:**
  1. Có tài liệu API chính thức, điều khoản sử dụng rõ ràng và xác nhận không vi phạm ToS của TikTok.
  2. Hỗ trợ xác thực bằng API key/OAuth hợp lệ do chủ tài khoản tự cấp (không yêu cầu mật khẩu hay cookie phiên TikTok).
  3. Khai báo rõ danh sách sự kiện hỗ trợ thực tế, giới hạn tốc độ (rate limit), độ trễ (latency) và có hay không `source_event_id` ổn định + semantics cho `gift streak`.
- **Trạng thái hiện tại:** `UNVERIFIED` — chưa chọn nhà cung cấp cụ thể trong `GD00`.

### 2.3 Unverified Capabilities (Chưa được xác minh cho dự án này)
Toàn bộ các mục sau được đánh dấu tường minh là **`UNVERIFIED`** cho đến khi hoàn thành bước kiểm chứng thực tế tại `GD17`:
- Khả năng nhận **Comment** thời gian thực với độ trễ ổn định và `player_external_id` bất biến xuyên suốt nhiều phiên live.
- Khả năng nhận **Gift** kèm `streak_id`, `repeat_count`, cờ kết thúc chuỗi (`is_streak_end`) và đảm bảo không phát trùng sự kiện.
- Khả năng nhận **Like** tổng hợp theo batch và giới hạn tần suất.
- Khả năng nhận **Room Join** (lưu ý: dù có, GAME001 cũng **không** tạo hồ sơ nhân vật từ sự kiện join).
- Chính sách kiểm duyệt nội dung và điều kiện chạy game tự động (interactive game policy) của TikTok LIVE trên kênh thực tế của chủ dự án.

### 2.4 Unsupported & Prohibited Capabilities (Không hỗ trợ / Cấm triển khai)
Các phương pháp sau bị **cấm tuyệt đối** trong LiveGame Studio:
- Scraping trang web TikTok LIVE trái phép, chạy trình duyệt ẩn danh (headless browser) để trích xuất DOM/WebSocket nội bộ chưa được cấp quyền.
- Dùng thư viện bên thứ ba dựa trên reverse-engineering giao thức nội bộ không chính thức / ký request giả mạo (`signature server` lậu) hoặc yêu cầu `sessionid` cookie của người dùng.
- Đọc/điều khiển trực tiếp bộ nhớ hoặc hook tiến trình TikTok LIVE Studio.
- Dùng quà tặng trả phí làm điều kiện đặt cược, quay thưởng ngẫu nhiên (RNG gacha trả tiền), mua chỉ số sức mạnh hay quy đổi tiền thật.

### 2.5 Mock Simulation (Phương án bắt buộc cho GD01–GD16)
- **Event Simulator (`modules/event_simulator`)** là nguồn sự kiện mặc định, đầy đủ và xác định trong toàn bộ giai đoạn phát triển Platform và GAME001 (`GD04`–`GD16`).
- Hỗ trợ giả lập:
  - Bình luận đơn lẻ, nhiều người chơi (`!join` đồng thời 20–100 người), chuỗi lệnh gameplay hoàn chỉnh.
  - Burst load `100 sự kiện/giây` trong 30 giây.
  - Quà tặng cosmetic (gồm cả kịch bản lặp/trùng ID để kiểm tra dedupe và chứng minh không thay đổi chỉ số sức mạnh).
  - Mất kết nối & khôi phục kết nối (test grace period `15s`).
  - Event Replay từ tệp kịch bản JSONL để kiểm thử hồi quy xác định.

---

## 3. Hợp đồng Capability Discovery của `ConnectorAdapter` (Chuẩn bị cho GD17)

Để ứng dụng không bao giờ giả định tính năng không tồn tại, mọi adapter kết nối tới `Event Gateway` đều phải khai báo `ConnectorCapabilities`:

```json
{
  "provider_name": "mock_simulator",
  "is_authorized_live": false,
  "supports_comments": true,
  "supports_gifts": true,
  "supports_likes": true,
  "supports_room_join": true,
  "provides_stable_player_id": true,
  "provides_stable_event_id": true,
  "gift_streak_semantics": "explicit_delta",
  "limitations": ["Chỉ dùng cho môi trường phát triển và kiểm thử cục bộ."]
}
```

- Khi một live provider thật chỉ hỗ trợ `comments` mà không hỗ trợ `gifts` hoặc không có `source_event_id`, giao diện **Live Studio** và **Game Master** sẽ tự động hiển thị chính xác năng lực và giới hạn đó cho Host.

---

## 4. Điều kiện mở cổng GD17 (GD17 Entry & Exit Gate)

Trước khi bắt đầu triển khai mã nguồn `TikTok Connector` thật tại `GD17`, bắt buộc có:
1. Quyết định phê duyệt từ chủ dự án về phương án nhà cung cấp được cấp quyền (Official Partner API hoặc Authorized Third-Party Provider).
2. Tài liệu kỹ thuật xác minh định dạng sự kiện, giới hạn rate, định danh người dùng ổn định và chính sách sử dụng.
3. Kịch bản kiểm thử **AC18 (Authorized Live Smoke Test)** trên kênh thử nghiệm thật với báo cáo ghi rõ quyền hạn, độ trễ đo thực tế và mọi giới hạn còn tồn tại.
