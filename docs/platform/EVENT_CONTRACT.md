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

### 3.3 Rate Limiting & Backpressure
- **Per-player Cooldown (Rule Engine):** Áp dụng cooldown độc lập theo từng player và nhóm lệnh dựa trên **server-side `SimulationClock`** (không phụ thuộc thời gian animation ở client, hỗ trợ độ trễ livestream). Ví dụ GAME001 (20 lệnh/dạng lệnh MVP): `!join` 5s, `!nam`/`!nu`/`!kiem`/`!dan`/`!the` 10s, `!tuluyen`/`!nghi` 3s, `!dotpha`/`!dokiep` 10s, `!boss` 5s, `!skill` 12s, `!defend`/`!hothe` 8s, `!hotheauto` / `!hotheauto on` / `!hotheauto off` 5s, `!heal` 20s, `!info`/`!find`/`!rank` 60s, `!help` 30s.
- **Bounded Queue & Load Shedding:**
  - `Event Bus` đặt giới hạn mặc định `max_queue_size = 2000`.
  - Khi độ sâu hàng đợi vượt `70%`: kích hoạt chế độ gộp/bỏ bớt sự kiện ưu tiên thấp (`like`, `room_join`, `cosmetic burst`).
  - Khi vượt `90%`: từ chối nhẹ lệnh hiển thị (`!info`, `!find`, `!rank`) với lý do `SYSTEM_BUSY`, ưu tiên tối đa lệnh gameplay (`!boss`, `!skill`, `!defend`, `!heal`, `!hothe`, `!dotpha`, `!join`).
  - Mục tiêu kiểm thử burst: xử lý ổn định `100 lệnh/giây` trong 30 giây mà không mất lệnh gameplay hợp lệ và không crash (AC09 / GD04 / GD19).

---

## 4. Mất kết nối, Idempotent Rewards, Recovery & Replay

- **Reconnect & Grace Period:** Khi nhận `connector_status = DISCONNECTED`, hệ thống bắt đầu đếm `grace_period_ms = 15000` trên monotonic clock. Nếu reconnect trong 15s → tiếp tục mượt. Quá 15s → tạm dừng `SimulationClock`, ngừng cộng XP và ngừng phát thưởng mới, giữ nguyên tiến trình đã lưu (AC12).
- **Idempotent Rewards:** Mọi thưởng phát sinh từ sự kiện đều ghi qua `reward_ledger` với khóa duy nhất `(event_id, player_id, reward_kind)` trong cùng SQLite transaction cập nhật số dư (AC08).
- **Crash Recovery:** Khởi động lại sau crash đọc lại trạng thái session/event, chuyển event đang dở sang `CANCELED_RECOVERY` kèm hoàn `xp_reserved`, và hoàn tất idempotent các event đang ở `REWARDING`.
- **Event Replay & Mock Event Provider:**
  - Mọi kịch bản kiểm thử được lưu dạng JSONL gồm danh sách `NormalizedEvent` + khoảng nhảy `delta_sim_ms`.
  - `Event Simulator` chạy chế độ `Mock Event Provider` độc lập hoàn toàn với internet, hỗ trợ phát từng lệnh, chạy kịch bản hoàn chỉnh (nhập môn → tu luyện → boss → độ kiếp → restart) và chạy lại cùng tập sự kiện để kiểm chứng tính idempotent.
