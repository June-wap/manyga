# ARCHITECTURE DECISION RECORDS (DECISIONS.md)

Tài liệu ghi nhận toàn bộ quyết định kiến trúc quan trọng của **LiveGame Studio** và các điểm đối chiếu (reconciliation) giữa Platform Design (`GD00`) và `GDD_Tu_Tien_Online_v0.1.md`.

---

## ADR-001: Kiến trúc Modular Monolith, Windows Desktop, Local-First
- **Trạng thái:** Accepted (Non-Negotiable)
- **Ngày:** 2026-11-26
- **Quyết định:** Xây dựng Platform theo kiến trúc **Modular Monolith** chạy cục bộ trên Windows Desktop (`127.0.0.1`), không triển khai microservices hay hạ tầng cloud ở giai đoạn nền tảng và MVP.
- **Lý do:** Giảm độ trễ xử lý sự kiện livestream, đơn giản hóa đóng gói Windows (GD20), đảm bảo tính bền vững offline/local-first và phù hợp với tài nguyên 1 máy vận hành livestream.
- **Hệ quả:** Bắt buộc giữ ranh giới module nghiêm ngặt qua Python package boundaries và contract interfaces để tránh biến thành monolith rối rắm khi mở rộng lên 100 mini game.

## ADR-002: Technology Stack cố định
- **Trạng thái:** Accepted (Non-Negotiable)
- **Ngày:** 2026-11-26
- **Quyết định:**
  - Backend: Python 3.11+, FastAPI, Pydantic v2, SQLite (WAL mode), SQLAlchemy 2.x, Alembic, REST + WebSocket.
  - Desktop UI: PySide6.
  - Broadcast Renderer: TypeScript + Vite + Three.js (3D); dự kiến Phaser.js cho game 2D tương lai.
- **Lý do:** Python tối ưu cho backend nhanh, hệ sinh thái kiểm thử tốt và PySide6 tích hợp sâu Windows Desktop; Three.js trên TypeScript/Vite cung cấp chuẩn glTF 2.0/WebGL mạnh cho 3D Broadcast Output 9:16.

## ADR-003: Chiến lược Vertical Slice với GAME001 (Tu Tiên Online)
- **Trạng thái:** Accepted (Non-Negotiable)
- **Ngày:** 2026-11-26
- **Quyết định:** Sử dụng `GAME001` (`cultivation_online`) làm mini game đầu tiên kiểm chứng từng lớp Platform. Không xây Tu Tiên Online thành phần mềm độc lập, đồng thời cấm `core/` và `modules/` phụ thuộc ngược vào `games/cultivation_online/`.
- **Lý do:** Tránh thiết kế trừu tượng quá mức không dùng được thực tế, nhưng vẫn bảo toàn khả năng mở rộng cho `GAME002`–`GAME007+`.

## ADR-004: Loại bỏ hoàn toàn AI Asset Generator và Blender Runtime khỏi Platform
- **Trạng thái:** Accepted (Non-Negotiable)
- **Ngày:** 2026-11-26
- **Quyết định:** Không tích hợp Meshy API, Tripo API, bất kỳ AI Asset Generator nào hoặc Blender runtime vào ứng dụng. Asset được tạo bên ngoài theo chuỗi prompt riêng (`TT-AS`) và chỉ đi vào Platform qua `Asset Importer` + `Asset Validator` theo `docs/platform/ASSET_CONTRACT.md`.
- **Lý do:** Giảm rủi ro bản quyền, loại bỏ chi phí API/lỗi mạng ngoài tầm kiểm soát, tách biệt hoàn toàn pipeline mỹ thuật khỏi độ ổn định phần mềm livestream.

## ADR-005: Đối chiếu Schema CSDL giữa Platform Design và GDD v0.1.0
- **Trạng thái:** Accepted (Reconciliation)
- **Ngày:** 2026-11-26
- **Bối cảnh:** `GDD_Tu_Tien_Online_v0.1.md` (Mục 17) liệt kê 11 bảng `tt_*` (trong đó có `tt_worlds`, `tt_sessions`, `tt_events`, `tt_reward_ledger`, `tt_processed_events`, `tt_action_audit`), nhưng chính GDD yêu cầu *"phải reconcile với schema platform và Alembic; không tạo trùng bảng chung."*
- **Quyết định:**
  - Platform sở hữu duy nhất các bảng lõi dùng chung: `application_settings`, `game_plugins`, `game_sessions`, `players`, `external_identities`, `player_game_profiles`, `assets`, `asset_versions`, `asset_dependencies`, `event_ingestions`, `processed_events`, `scheduled_events`, `reward_ledger`, `audit_logs`.
  - GAME001 (`cultivation_online`) chỉ sở hữu 8 bảng đặc thù tiền tố `g_cultivation_*`: `g_cultivation_characters`, `g_cultivation_progress`, `g_cultivation_realm_history`, `g_cultivation_inventory`, `g_cultivation_boss_events`, `g_cultivation_boss_participants`, `g_cultivation_tribulation_queue`, `g_cultivation_tribulation_results`.
  - Không tạo bảng trùng lặp `tt_sessions`, `tt_reward_ledger`, `tt_processed_events`, `tt_action_audit`; mọi dữ liệu tương ứng liên kết qua khóa ngoại tới bảng Platform.

## ADR-006: Đối chiếu Lộ trình GD00–GD20 với Task Track TT-GD01–TT-GD08
- **Trạng thái:** Accepted (Reconciliation)
- **Ngày:** 2026-11-26
- **Bối cảnh:** Thiết kế Platform chia 21 giai đoạn `GD00`–`GD20`, trong khi GDD v0.1.0 (Mục 20) chia 8 gói việc `TT-GD01`–`TT-GD08` và 9 gói asset `TT-AS01`–`TT-AS09`.
- **Quyết định:** Giữ `GD00`–`GD20` là xương sống phát hành chính thức của Platform, đồng thời ánh xạ tường minh từng `TT-GD01`..`TT-GD08` vào các giai đoạn `GD05`..`GD20` trong `docs/ROADMAP.md`, và giữ `TT-AS01`..`TT-AS09` thành Asset Roadmap độc lập không chặn nền tảng.

## ADR-007: Vị trí file GDD gốc `GDD_Tu_Tien_Online_v0.1.md`
- **Trạng thái:** Proposed (Pending User Approval)
- **Ngày:** 2026-11-26
- **Bối cảnh:** File GDD gốc hiện nằm tại root `D:\Tiktok Mini Game\GDD_Tu_Tien_Online_v0.1.md`, trong khi Mục 22 của GDD ghi *"Lưu tài liệu vào docs/games/cultivation_online/GDD.md"*.
- **Quyết định tạm thời:** Trong GD00, **giữ nguyên 100% file `GDD_Tu_Tien_Online_v0.1.md` tại root** (không di chuyển, không sửa, không ghi đè theo quy tắc an toàn). Sau khi người dùng xác nhận, mới quyết định có sao chép/di chuyển sang `docs/games/cultivation_online/GDD.md` hay giữ ở root.

## ADR-008: Một WebGL Renderer duy nhất và chiến lược Crowd Rendering
- **Trạng thái:** Accepted
- **Ngày:** 2026-11-26
- **Quyết định:** Chỉ sử dụng **1 WebGLRenderer** cho màn hình `1080×1920`. Tối đa 1 PiP được vẽ bằng scissor/viewport trên cùng renderer đó (có thể tắt). Không giả định `InstancedMesh` hoạt động trực tiếp cho `SkinnedMesh` có animation độc lập; sẽ thiết kế cơ chế kết hợp visibility cap gần camera + LOD đơn giản hóa ở xa và bắt buộc benchmark với 1/20/50/100 nhân vật ở GD09 và GD19.

## ADR-009: Chính sách Quà tặng Cosmetic & Tuân thủ (Anti-Gambling / Anti-P2W)
- **Trạng thái:** Accepted (Non-Negotiable)
- **Ngày:** 2026-11-26
- **Quyết định:** Quà tặng trả phí trên TikTok LIVE chỉ được ánh xạ tới hiệu ứng hình ảnh/âm thanh mang tính giải trí (cosmetic) với giới hạn tốc độ và hàng đợi hữu hạn. Tuyệt đối không tác động lên XP, chỉ số nhân vật, kết quả World Boss, xác suất đột phá/độ kiếp hay cơ chế đổi thưởng tiền thật.

## ADR-010: Trusted Built-in Plugins Only ở giai đoạn đầu
- **Trạng thái:** Accepted
- **Ngày:** 2026-11-26
- **Quyết định:** `Game Plugin Manager` chỉ nạp các plugin nằm trong danh sách tin cậy (allowlist) thuộc `games/` của kho mã nguồn. Không hỗ trợ nạp file `.py` / `.zip` tùy ý từ bên ngoài trong giai đoạn GD01–GD20.
- **Lý do:** Ngăn chặn thực thi mã tùy ý (Arbitrary Code Execution) trên máy Windows của người dùng.

## ADR-011: Phân tách Simulation Clock (`monotonic`) và Wall-Clock (`UTC`)
- **Trạng thái:** Accepted
- **Ngày:** 2026-11-26
- **Quyết định:** Mọi tick tu luyện (1s), tick boss (2s), cooldown lệnh, cửa sổ chọn nghề (60s), grace period (15s) và thời lượng event sử dụng **monotonic simulation clock** (injectable cho deterministic testing và đóng băng khi `PAUSE`). Dấu thời gian lưu DB (`created_at`, `ended_at`, `audit_logs`) sử dụng chuẩn `UTC ISO-8601`.
- **Lý do:** Tránh lỗi nhảy giờ hệ thống Windows (NTP sync, đổi múi giờ) làm sai lệch cooldown hoặc tính thưởng.

## ADR-012: Chính sách Xóa dữ liệu người chơi vs Toàn vẹn Sổ cái & Audit
- **Trạng thái:** Accepted
- **Ngày:** 2026-11-26
- **Bối cảnh:** GDD Mục 5 & 6 yêu cầu `!roi` lưu hồ sơ mà không xóa lịch sử thưởng, đồng thời cho phép GM xóa dữ liệu theo yêu cầu người chơi.
- **Quyết định:**
  - Lệnh `!roi` chỉ chuyển trạng thái người chơi sang `OPTED_OUT / OFFLINE`, ẩn khỏi scene, giữ nguyên tiến trình và `reward_ledger`.
  - Thao tác xóa dữ liệu theo yêu cầu (GM Data Erasure) thực hiện **tombstone / pseudonymization**: xóa `display_name`, `avatar_url`, liên kết `external_identities`, đặt cờ `is_anonymized = true` trên `players` và xóa hồ sơ hoạt động game, nhưng giữ bản ghi sổ cái `reward_ledger` và `audit_logs` ở dạng ẩn danh để không vỡ khóa ngoại và bảo toàn tính đối soát.

## ADR-013: Cổng kiểm soát Tích hợp TikTok được cấp quyền (GD17 Gate)
- **Trạng thái:** Accepted
- **Ngày:** 2026-11-26
- **Quyết định:** Không triển khai TikTok Connector thật trước GD17. Mọi kiểm thử từ GD01 đến GD16 chạy trên **Mock Event Provider & Event Simulator**. Khả năng nhận comment, gift, like, join từ TikTok thật được đánh dấu là `UNVERIFIED` cho tới khi xác minh nhà cung cấp chính thức/được cấp quyền cho tài khoản thực tế.

## ADR-014: Tách biệt Quyền truy cập SQLite (Backend-Only Writer)
- **Trạng thái:** Accepted
- **Ngày:** 2026-11-26
- **Quyết định:** Chỉ tiến trình FastAPI Backend được mở kết nối ghi vào file SQLite. PySide6 Desktop UI và Frontend Renderer giao tiếp 100% qua FastAPI REST/WebSocket (`127.0.0.1`).
- **Lý do:** Loại bỏ lỗi `SQLITE_BUSY` / lock contention giữa nhiều tiến trình Windows và đảm bảo mọi thay đổi đều đi qua Validation, Transaction Boundary và Audit Log.
