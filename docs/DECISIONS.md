# ARCHITECTURE DECISION RECORDS (DECISIONS.md)

Tài liệu ghi nhận toàn bộ quyết định kiến trúc quan trọng của **LiveGame Studio** và các điểm đối chiếu (reconciliation) giữa Platform Design (`GD00`) và `docs/games/cultivation_online/GDD.md`.

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
- **Bối cảnh:** `docs/games/cultivation_online/GDD.md` (Mục 17) liệt kê 11 bảng `tt_*` (trong đó có `tt_worlds`, `tt_sessions`, `tt_events`, `tt_reward_ledger`, `tt_processed_events`, `tt_action_audit`), nhưng chính GDD yêu cầu *"phải reconcile với schema platform và Alembic; không tạo trùng bảng chung."*
- **Quyết định:**
  - Platform sở hữu duy nhất các bảng lõi dùng chung: `application_settings`, `game_plugins`, `game_sessions`, `players`, `external_identities`, `player_game_profiles`, `assets`, `asset_versions`, `asset_dependencies`, `event_ingestions`, `processed_events`, `scheduled_events`, `reward_ledger`, `audit_logs`.
  - GAME001 (`cultivation_online`) chỉ sở hữu 8 bảng đặc thù tiền tố `g_cultivation_*`: `g_cultivation_characters`, `g_cultivation_progress`, `g_cultivation_realm_history`, `g_cultivation_inventory`, `g_cultivation_boss_events`, `g_cultivation_boss_participants`, `g_cultivation_tribulation_queue`, `g_cultivation_tribulation_results`.
  - Không tạo bảng trùng lặp `tt_sessions`, `tt_reward_ledger`, `tt_processed_events`, `tt_action_audit`; mọi dữ liệu tương ứng liên kết qua khóa ngoại tới bảng Platform.

## ADR-006: Đối chiếu Lộ trình GD00–GD20 với Task Track TT-GD01–TT-GD08
- **Trạng thái:** Accepted (Reconciliation)
- **Ngày:** 2026-11-26
- **Bối cảnh:** Thiết kế Platform chia 21 giai đoạn `GD00`–`GD20`, trong khi GDD v0.1.0 (Mục 20) chia 8 gói việc `TT-GD01`–`TT-GD08` và 9 gói asset `TT-AS01`–`TT-AS09`.
- **Quyết định:** Giữ `GD00`–`GD20` là xương sống phát hành chính thức của Platform, đồng thời ánh xạ tường minh từng `TT-GD01`..`TT-GD08` vào các giai đoạn `GD05`..`GD20` trong `docs/ROADMAP.md`, và giữ `TT-AS01`..`TT-AS09` thành Asset Roadmap độc lập không chặn nền tảng.

## ADR-007: Vị trí chính thức duy nhất của GDD GAME001 (`docs/games/cultivation_online/GDD.md`)
- **Trạng thái:** Accepted & Resolved (`GD00-FIX01`, 2026-11-26)
- **Ngày:** 2026-11-26
- **Bối cảnh:** File GDD gốc ban đầu nằm tại root `GDD_Tu_Tien_Online_v0.1.md`, trong khi Mục 22 của GDD chỉ định *"Lưu tài liệu vào docs/games/cultivation_online/GDD.md"*.
- **Quyết định:** Di chuyển tệp bằng `git mv` từ `GDD_Tu_Tien_Online_v0.1.md` sang `docs/games/cultivation_online/GDD.md`, xác minh toàn vẹn SHA-256 trước/sau hoàn toàn trùng khớp (`0A4F9D8B3D2005D0947A7C48E85F87D6B143ECC851DEB0E6345D27B2FF4AE534`, `31,380 bytes`), cập nhật toàn bộ đường dẫn tham chiếu trong repository và không duy trì bản sao GDD thứ hai. `docs/games/cultivation_online/GDD.md` là **Single Source of Truth** duy nhất cho luật gameplay GAME001.

## ADR-008: Một WebGL Renderer duy nhất và chiến lược Crowd Rendering
- **Trạng thái:** Accepted
- **Ngày:** 2026-11-26
- **Quyết định:** Chỉ sử dụng **1 WebGLRenderer** cho màn hình `1080×1920`. Tối đa 1 PiP được vẽ bằng scissor/viewport trên cùng renderer đó (có thể tắt). Không giả định `InstancedMesh` hoạt động trực tiếp cho `SkinnedMesh` có animation độc lập; sẽ thiết kế cơ chế kết hợp visibility cap gần camera + LOD đơn giản hóa ở xa và bắt buộc benchmark với 1/20/50/100 nhân vật ở GD09 và GD19.

## ADR-009: Chính sách Quà tặng Cosmetic & Tuân thủ (Anti-Gambling / Anti-P2W)
- **Trạng thái:** Accepted (Non-Negotiable)
- **Ngày:** 2026-11-26
- **Quyết định:** Quà tặng trả phí trên TikTok LIVE chỉ được ánh xạ tới hiệu ứng hình ảnh/âm thanh mang tính giải trí (cosmetic) với giới hạn tốc độ và hàng đợi hữu hạn. Tuyệt đối không tác động lên XP, chỉ số nhân vật, kết quả World Boss, xác suất đột phá/độ kiếp hay cơ chế đổi thưởng tiền thật.

## ADR-010: Trusted Built-in Plugins Only bằng Static Allowlist
- **Trạng thái:** Accepted & Hardened (`GD00-FIX02`, 2026-11-26)
- **Ngày:** 2026-11-26
- **Quyết định:** `Game Plugin Manager` chỉ nạp các plugin có cặp `(plugin_id, entrypoint)` khớp chính xác trong **bảng allowlist tĩnh (`TRUSTED_BUILTIN_PLUGINS`)** khai báo trong Platform — **không chỉ dựa vào kiểm tra tiền tố đường dẫn `games.<plugin_id>.`**. Không hỗ trợ nạp file `.py` / `.zip` tùy ý từ bên ngoài trong giai đoạn GD01–GD20.
- **Lý do:** Ngăn chặn thực thi mã tùy ý (Arbitrary Code Execution) ngay cả khi có file lạ rơi vào thư mục `games/`.

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

## ADR-014: SQLite Single-Process Writer & Database-Wide Write Serialization (`HIGH-003`)
- **Trạng thái:** Accepted & Hardened (`GD00-FIX02`, 2026-11-26)
- **Ngày:** 2026-11-26
- **Quyết định:**
  1. Chỉ tiến trình FastAPI Backend được mở kết nối ghi vào tệp SQLite (PySide6 và Renderer giao tiếp 100% qua FastAPI).
  2. Mọi write transaction trong Backend bắt buộc đi qua **Centralized Write Coordinator** (global write serializer / bounded write queue đảm bảo tối đa **1 write transaction toàn DB tại một thời điểm**) kèm `WAL`, `foreign_keys=ON`, `busy_timeout=5000ms`, `transaction_timeout=5000ms`, rollback tự động và drain + `wal_checkpoint(TRUNCATE)` khi shutdown.
  3. Khóa theo từng `player_id` **không được coi là đủ** để xử lý tranh chấp ghi của SQLite (chỉ dùng cho thứ tự logic domain). Triển khai tại `GD02`.

## ADR-015: Chuẩn hóa Lệnh Hộ Thể Tự Động (`!hothe`, `!hotheauto`, `!hotheauto on/off`) — Giải quyết `CONF-04` / `OPEN-05`
- **Trạng thái:** Accepted & Resolved (`GD00-FIX01`, 2026-11-26)
- **Ngày:** 2026-11-26
- **Bối cảnh:** GDD v0.1.0 Mục 10 nhắc đến `!hotheauto off` nhưng chưa kê khai trong bảng lệnh Mục 6. Ngoài ra độ trễ livestream (broadcast delay 3–15s) khiến việc ép người xem canh chuẩn khung hình animation để bấm `!hothe` là không công bằng.
- **Quyết định:**
  1. Bổ sung chính thức vào bảng lệnh MVP (`docs/games/cultivation_online/GDD.md` Amendment `v0.1.1`): `!hothe`, `!hotheauto`, `!hotheauto on`, `!hotheauto off`.
  2. **Hộ thể tự động mặc định bật** (`g_cultivation_characters.auto_guard_enabled = 1`); người chơi có thể bật/tắt bằng bình luận; Game Master có thể cấu hình chính sách mặc định cho phiên/lượt kiếp mới.
  3. Toàn bộ tính toán hộ thể và thiên lôi dựa trên **server-side event timing (`SimulationClock`)**, hỗ trợ độ trễ livestream và không yêu cầu phản ứng khớp khung hình animation.
  4. Không thay đổi bất kỳ thông số cân bằng gốc nào của v0.1.0 và tuyệt đối không dùng quà tặng trả phí để tăng xác suất độ kiếp.

## ADR-016: Chính sách Asset theo Chế độ `DEVELOPMENT` vs `PRODUCTION` (`HIGH-002`)
- **Trạng thái:** Accepted (`GD00-FIX02`, 2026-11-26)
- **Ngày:** 2026-11-26
- **Quyết định:** Tách 2 chế độ tài nguyên: `DEVELOPMENT` (cho phép placeholder tương thích kèm cảnh báo nổi bật, không chặn phát triển) và `PRODUCTION` (bắt buộc tồn tại đủ `required_assets` đúng semver, `validation_status=VALID`, cấm tự bỏ qua dependency thiếu và cấm gắn `production-ready` khi dùng placeholder chưa được phê duyệt).

## ADR-017: Mô hình Bảo mật API Cục bộ (`HIGH-004`)
- **Trạng thái:** Accepted (`GD00-FIX02`, 2026-11-26)
- **Ngày:** 2026-11-26
- **Quyết định:** Kết hợp loopback `127.0.0.1`, `TrustedHostMiddleware`, restricted Origin (**cấm wildcard CORS `*`**), khóa phiên ngẫu nhiên mật mã tách quyền `ADMIN_SESSION_TOKEN` (privileged REST + `/ws/admin`) vs `RENDERER_STREAM_TOKEN` (read-only `/ws/renderer` + asset stream), chỉ giữ `GET /api/v1/health` công khai cục bộ tối thiểu, không đặt admin credential vào Broadcast URL, không log credentials và không expose arbitrary file paths.

## ADR-018: Plugin-Delegated Crash Recovery & Immutable Outcome Snapshot (`HIGH-005`)
- **Trạng thái:** Accepted (`GD00-FIX02`, 2026-11-26)
- **Ngày:** 2026-11-26
- **Quyết định:** Platform Recovery Core không hardcode logic hay tên bảng của bất kỳ game nào; mọi sự kiện có thưởng bắt buộc commit `outcome_snapshot_json` bất biến (`outcome_committed=1`) trong 1 transaction trước `REWARDING`. Khi crash, trạng thái chưa commit outcome chuyển `CANCELED_RECOVERY` kèm hoàn tài nguyên giữ qua plugin handler; trạng thái đã commit outcome tiếp tục trả thưởng idempotent qua `RewardLedger`.

## ADR-019: Giao thức Snapshot/Delta có `stream_epoch` & Chống Stale/Overlap (`HIGH-006`)
- **Trạng thái:** Accepted (`GD00-FIX02`, 2026-11-26)
- **Ngày:** 2026-11-26
- **Quyết định:** Mọi gói `/ws/renderer` bắt buộc gắn `stream_epoch`, `session_id`, `revision`, `snapshot_seq` và `request_id`. Renderer chỉ apply delta khi khớp đồng thời `stream_epoch`, `session_id` và `from_revision == last_applied_revision`; mọi mismatch, gap hoặc overlap đều buộc chuyển `RESYNCING` và yêu cầu snapshot mới.

## ADR-020: Tách 3 Hàng chờ Sự kiện & Chính sách Backpressure `100%` (`MEDIUM-002`, `MEDIUM-004`)
- **Trạng thái:** Accepted (`GD00-FIX02`, 2026-11-26)
- **Ngày:** 2026-11-26
- **Quyết định:** Tách biệt Gameplay Execution Queue, Camera Focus Queue và Event Presentation Queue (không ép mọi sự kiện cá nhân lên camera chính). Khi `Event Bus` đạt `100%`, áp dụng Admission Control + Explicit Rejection (`INGESTION_QUEUE_FULL` / `HTTP 429`) có bounded enqueue timeout, metrics và auditability — không silent drop gameplay commands và không block vô hạn Event Gateway.
