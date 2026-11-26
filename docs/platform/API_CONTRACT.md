# API CONTRACT — LIVEGAME STUDIO

**Contract Version:** `1.0.0`  
**Transport:** REST (HTTP/1.1 JSON) + WebSocket (JSON)  
**Default Bind Address:** `127.0.0.1:8765` (loopback-only mặc định; không bind `0.0.0.0`).

---

## 1. Quy ước chung (Global Conventions)

- **Base URL:** `http://127.0.0.1:<port>/api/v1`
- **Content-Type:** `application/json; charset=utf-8` (trừ endpoint stream file nhị phân asset).
- **Timestamps:** UTC ISO-8601 (`2026-11-26T07:30:00.000Z`).
- **Response Envelope chuẩn:**
  ```json
  {
    "ok": true,
    "data": {},
    "meta": { "request_id": "req_01...", "timestamp": "2026-11-26T07:30:00.000Z" }
  }
  ```
- **Error Envelope chuẩn:**
  ```json
  {
    "ok": false,
    "error": {
      "code": "RESOURCE_NOT_FOUND",
      "message": "Không tìm thấy phiên live yêu cầu.",
      "details": {}
    },
    "meta": { "request_id": "req_01...", "timestamp": "2026-11-26T07:30:00.000Z" }
  }
  ```
- **Mã lỗi HTTP tiêu chuẩn:** `200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `409 Conflict` (trùng bản ghi / sai trạng thái state machine), `422 Unprocessable Entity` (Pydantic validation), `429 Too Many Requests`, `500 Internal Server Error` (đã ẩn stack trace nhạy cảm), `503 Service Unavailable`.

---

## 2. REST API Endpoints

### 2.1 System & Health (`GD01+`)
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/v1/health` | Trạng thái sống của Backend, kết nối DB, active plugin, uptime |
| `GET` | `/api/v1/metrics` | Chỉ số queue depth, latency p50/p95, WS clients, FPS telemetry |
| `GET` | `/api/v1/settings` | Lấy cấu hình hệ thống (các trường `is_secret=1` bị redact thành `"***"`) |
| `PATCH` | `/api/v1/settings/{key}` | Cập nhật 1 cấu hình hợp lệ; ghi `audit_logs` |

### 2.2 Game Registry & Plugins (`GD05+`)
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/v1/games` | Danh sách toàn bộ Game Plugins đã đăng ký trong `games/` |
| `GET` | `/api/v1/games/{plugin_id}` | Chi tiết manifest, trạng thái tài nguyên, command specs và config schema |
| `POST` | `/api/v1/games/rescan` | Quét lại trusted built-in plugins trong `games/` |

### 2.3 Game Sessions (`GD02+`, `GD05+`)
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/v1/sessions` | Danh sách các phiên live (phân trang) |
| `POST` | `/api/v1/sessions` | Tạo phiên mới `{ plugin_id, world_scope, channel_id, source_mode }` |
| `GET` | `/api/v1/sessions/{session_id}` | Trạng thái chi tiết phiên, `sim_elapsed_ms`, `last_revision` |
| `POST` | `/api/v1/sessions/{session_id}/start` | Khởi chạy phiên (từ chối `409` nếu đang có phiên khác `RUNNING`) |
| `POST` | `/api/v1/sessions/{session_id}/pause` | Đóng băng `SimulationClock` và ngừng tích lũy XP |
| `POST` | `/api/v1/sessions/{session_id}/resume` | Tiếp tục `SimulationClock` |
| `POST` | `/api/v1/sessions/{session_id}/stop` | Dừng phiên có kiểm soát, hoàn XP giữ, xả checkpoint |

### 2.4 Players (`GD02+`, `GD11+`)
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/v1/players` | Tìm kiếm / phân trang người chơi theo `plugin_id`, `status`, `query` |
| `GET` | `/api/v1/players/{player_id}` | Hồ sơ toàn cục và trạng thái theo game |
| `PATCH` | `/api/v1/players/{player_id}/moderation` | Kiểm duyệt đổi bí danh / ẩn khỏi scene (ghi `audit_logs`) |
| `POST` | `/api/v1/players/{player_id}/anonymize` | Xóa/ẩn danh dữ liệu theo yêu cầu người chơi (`confirm: true`, `ADR-012`) |

### 2.5 Assets (`GD07+`)
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/v1/assets` | Liệt kê assets theo `asset_type`, `is_placeholder`, `status` |
| `GET` | `/api/v1/assets/{asset_id}` | Chi tiết asset, các phiên bản, `validation_report` và `dependencies` |
| `POST` | `/api/v1/assets/import` | Nhập gói asset cục bộ `{ source_dir }`, chạy `Asset Validator` |
| `PATCH` | `/api/v1/assets/{asset_id}/active-version` | Chuyển phiên bản active (chỉ chấp nhận phiên bản `VALID`) |
| `GET` | `/api/v1/assets/{asset_id}/files/{rel_path:path}` | Stream tệp tĩnh đã xác thực cho Three.js (chặn tuyệt đối path traversal — trả `400`/`403`) |

### 2.6 Event Simulator (`GD04+`)
| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/api/v1/simulator/events` | Bắn 1 sự kiện giả lập (`comment`, `gift`, `like`, `join`) vào Event Gateway |
| `POST` | `/api/v1/simulator/burst` | Chạy bài test tải burst `{ rate_per_sec, duration_sec, seed }` |
| `POST` | `/api/v1/simulator/replay` | Phát lại tệp kịch bản sự kiện phục vụ kiểm thử xác định |
| `POST` | `/api/v1/simulator/disconnect` | Giả lập mất kết nối provider (test grace period 15s) |
| `POST` | `/api/v1/simulator/reconnect` | Giả lập khôi phục kết nối provider |

### 2.7 Game Master, Events, Live Studio & Analytics (`GD12+`, `GD18+`)
| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/api/v1/gm/control-mode` | Đặt chế độ `semi_auto` / `auto` / `manual` |
| `POST` | `/api/v1/gm/camera/override` | Chuyển camera thủ công `{ camera_id, target_entity_id, duration_ms }` |
| `POST` | `/api/v1/gm/events/trigger` | Kích hoạt sự kiện hợp lệ sớm (ví dụ World Boss khi idle) |
| `POST` | `/api/v1/gm/events/{event_id}/cancel` | Hủy sự kiện (`confirm: true`, ghi `audit_logs`) |
| `GET` | `/api/v1/gm/audit-logs` | Xem lịch sử thao tác GM (đã redact) |
| `GET` | `/api/v1/live-studio/readiness` | Bảng kiểm tra sẵn sàng phát sóng + URL `1080×1920` |
| `GET` | `/api/v1/analytics/sessions/{session_id}` | Báo cáo chỉ số vận hành và benchmark phiên |

---

## 3. WebSocket Contracts

### 3.1 Broadcast Renderer Stream: `ws://127.0.0.1:<port>/ws/renderer`
Luồng một chiều chính từ Backend → Three.js Renderer, kèm thông điệp điều khiển ngược tối thiểu từ Renderer:

**Server → Renderer:**
- `STATE_SNAPSHOT`: Gửi ngay khi kết nối hoặc phản hồi `SNAPSHOT_REQUEST`.
  ```json
  {
    "type": "STATE_SNAPSHOT",
    "schema_version": "1.0.0",
    "session_id": "sess_01",
    "plugin_id": "cultivation_online",
    "revision": 42,
    "sim_elapsed_ms": 125000,
    "session_state": "RUNNING",
    "world": { "map_asset_id": "TT_MAP001", "map_version": "0.1.0" },
    "entities": [],
    "active_event": null,
    "camera": { "active_camera_id": "CAM01", "pip_camera_id": null, "priority": 10 },
    "overlays": { "pinned": {}, "queue": [] }
  }
  ```
- `STATE_DELTA`: Phát thay đổi tăng dần theo `revision`.
  ```json
  {
    "type": "STATE_DELTA",
    "schema_version": "1.0.0",
    "session_id": "sess_01",
    "from_revision": 42,
    "to_revision": 43,
    "ops": [
      { "op": "entity_upsert", "entity": { "id": "p_01", "display_name": "Đạo Hữu A", "state": "CULTIVATING" } },
      { "op": "vfx_trigger", "effect_id": "aura_breakthrough", "entity_id": "p_01", "ttl_ms": 3000 }
    ]
  }
  ```
- `HEARTBEAT`: Gửi định kỳ mỗi `5s`.

**Renderer → Server:**
- `SNAPSHOT_REQUEST`: `{ "type": "SNAPSHOT_REQUEST", "last_revision": 42, "reason": "gap_detected" }`
- `RENDERER_TELEMETRY`: `{ "type": "RENDERER_TELEMETRY", "fps": 58.4, "frame_time_p95_ms": 17.2, "draw_calls": 94, "visible_entities": 60 }`

### 3.2 Desktop Admin Stream: `ws://127.0.0.1:<port>/ws/admin`
- Đẩy cập nhật thời gian thực cho PySide6 Desktop UI: trạng thái phiên, danh sách lệnh bị từ chối kèm `reason_code`, bảng người chơi, hàng chờ Tiểu Thiên Kiếp, trạng thái Boss, trạng thái Connector, FPS/Queue telemetry và cảnh báo lỗi.
- Tuyệt đối tách riêng khỏi `/ws/renderer` để không bao giờ rò rỉ thông tin quản trị sang màn hình phát sóng.
