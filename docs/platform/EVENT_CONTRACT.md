# EVENT CONTRACT — LIVEGAME STUDIO

**Contract Version:** `1.0.0`  
**Luồng chuẩn:**  
`Authorized Event Provider → Event Gateway → Normalized Event → Event Bus → Command Parser → Game Plugin → Gameplay Services → Database Transaction → State Update → Three.js Runtime → Broadcast Output`

---

## 1. Normalized Event Envelope (Schema bắt buộc)

Mọi sự kiện đi qua `Event Gateway` (dù từ Authorized TikTok Provider hay Mock Event Simulator) phải được chuẩn hóa về cùng một Envelope khớp với `docs/games/cultivation_online/GDD.md` (v0.1.1) Mục 16:

```json
{
  "schema_version": "1.0.0",
  "event_id": "01J9X7K2M8N4P6Q8R0S2T4V6W8",
  "source": "simulator",
  "source_event_id": "sim_evt_000102",
  "channel_id": "channel_local_01",
  "live_session_id": "sess_01",
  "player_external_id": "ext_user_9001",
  "event_type": "comment",
  "received_at": "2026-11-26T07:35:00.120Z",
  "occurred_at": "2026-11-26T07:35:00.095Z",
  "payload": {
    "nickname": "Đạo Hữu A",
    "text": "!dotpha"
  }
}
```

### Quy tắc từng trường
| Trường | Kiểu | Bắt buộc | Mô tả & Ràng buộc |
|---|---|---|---|
| `schema_version` | `string` | Có | Semver của Event Contract (`1.0.0`) |
| `event_id` | `string` | Có | ULID/UUID do `Event Gateway` sinh ra (duy nhất nội bộ) |
| `source` | `enum` | Có | `"simulator"` \| `"authorized_provider:<name>"` \| `"system"` |
| `source_event_id` | `string \| null` | Tùy provider | ID ổn định từ nhà cung cấp nếu có; **không tự bịa** nếu provider không trả về |
| `channel_id` | `string` | Có | Phạm vi kênh phát sóng để cô lập định danh người chơi |
| `live_session_id` | `string` | Có | Phiên đang chạy gắn vào sự kiện |
| `player_external_id` | `string \| null` | Có với sự kiện viewer | ID người xem ổn định từ provider; **không dùng `nickname` thay thế** |
| `event_type` | `enum` | Có | `"comment"` \| `"gift"` \| `"like"` \| `"room_join"` \| `"connector_status"` \| `"system_tick"` |
| `received_at` | `ISO-8601 UTC` | Có | Mốc thời gian `Event Gateway` nhận sự kiện |
| `occurred_at` | `ISO-8601 UTC \| null` | Không | Mốc thời gian nguồn nếu đáng tin; không dùng thay `SimulationClock` |
| `payload` | `object` | Có | Dữ liệu chuẩn hóa theo từng `event_type` (giới hạn dung lượng ≤ 8 KB) |

---

## 2. Phân loại `event_type` và Chính sách xử lý

| `event_type` | Payload chuẩn | Quy tắc Platform & GAME001 |
|---|---|---|
| `comment` | `{ nickname, avatar_url?, text }` | Chuyển qua `Command Parser` xác định (không dùng LLM). Bình luận thường không tạo hành động. Chỉ `!join` / `!nam` / `!nu` được tạo hồ sơ mới. |
| `gift` | `{ nickname, gift_id, gift_name, repeat_count, streak_id?, is_streak_end? }` | **Không tạo hồ sơ người chơi mới.** Chỉ chuyển vào `GiftMapping` tạo **hiệu ứng cosmetic**; cấm tuyệt đối tác động XP/ATK/HP/Boss/Độ kiếp (`ADR-009`). |
| `like` | `{ nickname, like_count }` | Chỉ dùng cho hiệu ứng môi trường nhẹ có rate-limit; không ảnh hưởng sức mạnh. |
| `room_join` | `{ nickname }` | Chỉ dùng thống kê/hiện diện nhẹ nếu provider hỗ trợ. **Không tự động tạo hồ sơ nhân vật.** |
| `connector_status` | `{ state, reason }` | Điều khiển grace period `15s` khi mất kết nối và thông báo trên Game Master Panel. |

> **Cảnh báo quan trọng (Non-Assumption Rule):** Thiết kế này **không giả định** TikTok cung cấp mọi loại sự kiện (`comment`, `gift`, `like`, `room_join`) hay `source_event_id` ổn định cho mọi tài khoản. Mọi khả năng sự kiện thật phải được xác minh trong `GD17` (`docs/platform/TIKTOK_INTEGRATION_FEASIBILITY.md`).

---

## 3. Chống trùng lặp, Thứ tự, Rate Limiting & Backpressure

### 3.1 Chống xử lý trùng lặp (Deduplication)
- **Khi provider cung cấp `source_event_id`:** Lưu khóa duy nhất `(source_namespace, source_event_id)` vào bảng `processed_events`. Sự kiện trùng bị đánh dấu `DUPLICATE` tại `event_ingestions` và bỏ qua an toàn.
- **Khi provider KHÔNG cung cấp `source_event_id`:** Adapter bắt buộc khai báo rõ chiến lược và giới hạn trong tài liệu/config. **Không tự coi hai bình luận giống nhau liên tiếp của cùng người chơi là trùng lặp** nếu không có bằng chứng (tránh nuốt lệnh hợp lệ sau hết cooldown); bảo vệ nghiệp vụ dựa vào cooldown và idempotency ở tầng domain/reward.
- **Gift Streak:** Chuẩn hóa theo semantics của từng provider đã xác minh; chưa xác minh thì không kích hoạt hiệu ứng lặp chồng.

### 3.2 Thứ tự sự kiện (Event Ordering)
- Mỗi sự kiện được cấp `received_seq` tăng đơn điệu khi vào `Event Gateway`.
- `Event Bus` bảo toàn thứ tự FIFO theo `player_external_id` để các lệnh liên tiếp của cùng một người chơi không bao giờ chạy đảo ngược.
- Các hàng chờ cộng đồng (ví dụ hàng chờ Tiểu Thiên Kiếp) sắp xếp xác định bằng cặp `(received_at_monotonic, player_id)`.

### 3.3 Rate Limiting & Chính sách Backpressure 100% (`MEDIUM-004`)
- **Per-player Cooldown (Rule Engine):** Áp dụng cooldown độc lập theo từng player và nhóm lệnh dựa trên **server-side `SimulationClock`** (không phụ thuộc thời gian animation ở client, hỗ trợ độ trễ livestream). Toàn bộ bảng lệnh và cooldown được nạp động từ tệp `commands.json` của từng plugin (`MEDIUM-003`).
- **Phân biệt rõ Target Throughput vs Guaranteed Delivery:**
  - *Target Throughput:* Mục tiêu kiểm thử chịu tải burst **`100 lệnh/giây` trong 30 giây** trên máy cục bộ.
  - *Guaranteed Delivery:* Không cam kết bộ đệm vô hạn; trong môi trường Desktop local-first, hàng đợi bị chặn biên (bounded) và áp dụng **Admission Control** tường minh để bảo vệ ổn định RAM và độ trễ.
- **Chính sách theo ngưỡng hàng đợi `Event Bus` (`max_queue_size = 2000`):**
  - **Ngưỡng `70%`:** Kích hoạt gộp/giảm tần suất sự kiện ưu tiên thấp (`like`, `room_join`, `cosmetic burst`).
  - **Ngưỡng `90%`:** Từ chối có mã lỗi `SYSTEM_BUSY` cho lệnh hiển thị phụ (`!info`, `!find`, `!rank`), giữ nguyên băng thông cho lệnh gameplay lõi.
  - **Ngưỡng `100%` (Queue Full Policy):**
    1. **Admission Control & Explicit Rejection:** Khi hàng đợi đạt `100%`, `Event Gateway` **từ chối tường minh** với mã `INGESTION_QUEUE_FULL` (`HTTP 429` cho Simulator/API, structured rejection cho adapter) — **tuyệt đối không âm thầm drop (no silent drop) lệnh gameplay**.
    2. **Non-Blocking Gateway & Bounded Retries:** `Event Gateway` **tuyệt đối không block vô hạn** khi enqueue; sử dụng enqueue timeout hữu hạn (`50ms`) và tối đa `<= 2` lần retry ngắn khi gặp áp lực tức thời trước khi trả `INGESTION_QUEUE_FULL`.
    3. **Priority Policy:** Giữ slot ưu tiên (reserved headroom) cho sự kiện hệ thống (`connector_status`, GM emergency stop) và lệnh gameplay lõi (`!boss`, `!skill`, `!defend`, `!heal`, `!hothe`, `!dotpha`, `!join`, `!roi`) trước lệnh trình chiếu/cosmetic.
    4. **Metrics & Auditability:** Mọi từ chối do backpressure bắt buộc ghi nhận vào `event_ingestions` với `ingestion_status = 'REJECTED_BACKPRESSURE'` (hoặc tổng hợp có audit trong trường hợp bão sự kiện), đồng thời cập nhật metrics `events_rejected_backpressure_total`, `queue_depth`, `rejection_by_priority` cho Desktop UI & Analytics.

---

## 3.5 Hợp đồng Lệnh Plugin (`commands.json` — `MEDIUM-003`)

**Nguyên tắc tách biệt:** Platform `Command Parser` (`modules/command_parser`) **tuyệt đối không hardcode bất kỳ lệnh nào của `cultivation_online`**. Mọi lệnh của từng game được khai báo trong tệp `games/<plugin_id>/commands.json` và nạp vào parser tại `on_load()`.

### Bảng đối chiếu đầy đủ Lệnh MVP `GAME001` (`GDD.md` v0.1.1 ↔ `commands.json`)
| Canonical Command | Aliases (ví dụ Tiếng Việt có dấu) | Arguments | Cooldown Group | Cooldown | Preconditions | Ownership | Error Codes chính |
|---|---|---|---|---:|---|---|---|
| `!join` | `!thamgia`, `!nhập_môn` | Không | `onboarding` | 5s | Phiên `RUNNING` (idempotent) | `sender_only` | `SESSION_NOT_RUNNING`, `COOLDOWN_ACTIVE` |
| `!nam` / `!nu` | `!nữ` | Không | `appearance` | 10s | Ngoài event; có thể nhập môn trực tiếp | `sender_only` | `IN_ACTIVE_EVENT`, `COOLDOWN_ACTIVE` |
| `!kiem` / `!dan` / `!the` | `!kiếm`, `!đan`, `!thể` | Không | `profession` | 10s | Trong cửa sổ 60s hoặc GM cho phép, ngoài chiến đấu | `sender_only` | `SELECTION_WINDOW_CLOSED`, `IN_ACTIVE_EVENT` |
| `!tuluyen` | `!tuluyện` | Không | `cultivation_mode` | 3s | Đã nhập môn, ngoài event | `sender_only` | `PLAYER_NOT_JOINED`, `IN_ACTIVE_EVENT` |
| `!nghi` | `!nghỉ` | Không | `cultivation_mode` | 3s | Đã nhập môn, ngoài event | `sender_only` | `PLAYER_NOT_JOINED`, `IN_ACTIVE_EVENT` |
| `!dotpha` | `!độtphá`, `!dokiep`, `!độkiếp` | Không | `breakthrough` | 10s | Đủ XP khả dụng, chưa có yêu cầu kiếp chờ/chạy | `sender_only` | `INSUFFICIENT_XP`, `ALREADY_QUEUED`, `QUEUE_FULL`, `MAX_REALM_REACHED` |
| `!boss` | — | Không | `boss_register` | 5s | Boss đang ở pha `REGISTRATION`, còn slot `<100` | `sender_only` | `BOSS_NOT_OPEN`, `BOSS_FULL`, `ALREADY_REGISTERED` |
| `!skill` | `!kỹnăng` | Không | `boss_skill` | 12s | Đang sống trong Boss `ACTIVE` | `sender_only` | `NOT_IN_BOSS`, `PLAYER_DEAD`, `COOLDOWN_ACTIVE` |
| `!defend` | `!phòngthủ` | Không | `boss_defend` | 8s | Đang sống trong Boss `ACTIVE` | `sender_only` | `NOT_IN_BOSS`, `PLAYER_DEAD`, `COOLDOWN_ACTIVE` |
| `!heal` | `!hồimáu` | Không | `consume_heal` | 20s | Có Hồi linh đan `>= 1`, còn sống, chưa đầy HP | `sender_only` | `NO_HEALING_PILL`, `PLAYER_DEAD`, `HP_ALREADY_FULL` |
| `!hothe` | `!hộthể` | Không | `tribulation_guard` | 8s | Đang trong Tiểu Thiên Kiếp `ACTIVE` | `sender_only` | `NOT_IN_TRIBULATION`, `COOLDOWN_ACTIVE` |
| `!hotheauto` | `!hộthểtựđộng` | `[on \| off]` *(optional)* | `auto_guard_pref` | 5s | Đã nhập môn (`!hotheauto` xem trạng thái; `on`/`off` bật/tắt; mặc định bật) | `sender_only` | `PLAYER_NOT_JOINED`, `INVALID_ARGS`, `COOLDOWN_ACTIVE` |
| `!info` | `!status`, `!thôngtin` | Không | `overlay_info` | 60s | Đã nhập môn, hàng chờ overlay chưa đầy | `sender_only` | `PLAYER_NOT_JOINED`, `QUEUE_FULL`, `SYSTEM_BUSY` |
| `!find` | `!me`, `!tìm` | Không | `camera_find` | 60s | Đã nhập môn, không ngắt camera Boss | `sender_only` | `PLAYER_NOT_JOINED`, `QUEUE_FULL`, `SYSTEM_BUSY` |
| `!rank` | `!bxh` | Không | `overlay_rank` | 60s | Phiên `RUNNING` | `sender_only` | `COOLDOWN_ACTIVE`, `SYSTEM_BUSY` |
| `!help` | `!hướngdẫn` | Không | `overlay_help` | 30s | Phiên `RUNNING` | `sender_only` | `COOLDOWN_ACTIVE` |
| `!roi` | `!rời` | Không | `opt_out` | 5s | Đã nhập môn (**Opt-out:** lưu tiến trình, ẩn khỏi scene, **không xóa `reward_ledger`**; nếu đang event xử lý forfeit theo luật) | `sender_only` | `PLAYER_NOT_JOINED`, `COOLDOWN_ACTIVE` |

- **Quy tắc Validation & Ownership chung:** Trim khoảng trắng, không phân biệt hoa/thường, 1 comment tối đa 1 lệnh đầu tiên hợp lệ, từ chối tham số dư/sai enum với `INVALID_ARGS`, mọi lệnh luôn khóa `ownership = sender_only` (người xem không thể truyền ID người khác để điều khiển).

---

## 4. Mất kết nối, Idempotent Rewards, Recovery & Replay

- **Reconnect & Grace Period:** Khi nhận `connector_status = DISCONNECTED`, hệ thống bắt đầu đếm `grace_period_ms = 15000` trên monotonic clock. Nếu reconnect trong 15s → tiếp tục mượt. Quá 15s → tạm dừng `SimulationClock`, ngừng cộng XP và ngừng phát thưởng mới, giữ nguyên tiến trình đã lưu (AC12).
- **Idempotent Rewards:** Mọi thưởng phát sinh từ sự kiện đều ghi qua `reward_ledger` với khóa duy nhất `(event_id, player_id, reward_kind)` trong cùng SQLite transaction cập nhật số dư (AC08).
- **Crash Recovery:** Khởi động lại sau crash đọc lại trạng thái session/event, chuyển event đang dở sang `CANCELED_RECOVERY` kèm hoàn `xp_reserved`, và hoàn tất idempotent các event đang ở `REWARDING`.
- **Event Replay & Mock Event Provider:**
  - Mọi kịch bản kiểm thử được lưu dạng JSONL gồm danh sách `NormalizedEvent` + khoảng nhảy `delta_sim_ms`.
  - `Event Simulator` chạy chế độ `Mock Event Provider` độc lập hoàn toàn với internet, hỗ trợ phát từng lệnh, chạy kịch bản hoàn chỉnh (nhập môn → tu luyện → boss → độ kiếp → restart) và chạy lại cùng tập sự kiện để kiểm chứng tính idempotent.
