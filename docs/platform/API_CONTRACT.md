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
- **Mã lỗi HTTP tiêu chuẩn:** `200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized` (thiếu/sai local session token), `403 Forbidden` (sai quyền/Origin/path traversal), `404 Not Found`, `409 Conflict` (trùng bản ghi / sai trạng thái state machine), `422 Unprocessable Entity` (Pydantic validation), `429 Too Many Requests` (rate limit / backpressure), `500 Internal Server Error` (đã ẩn stack trace nhạy cảm), `503 Service Unavailable`.

---

## 1.5 Mô hình Bảo mật API Cục bộ (Local API Security Model — `HIGH-004`)

1. **Loopback Binding & Trusted Host:**
   - Backend mặc định chỉ lắng nghe `127.0.0.1:<port>`. Cấm mở `0.0.0.0` ở cấu hình mặc định.
   - Bắt buộc bật `TrustedHostMiddleware` chỉ chấp nhận `127.0.0.1`, `127.0.0.1:<port>`, `localhost`, `localhost:<port>`.
2. **Restricted Origin Policy (No Wildcard CORS):**
   - **Cấm tuyệt đối wildcard CORS (`Access-Control-Allow-Origin: *`).**
   - Chỉ cho phép danh sách tường minh các local origin hợp lệ (ví dụ `http://127.0.0.1:<vite_port>`, `http://127.0.0.1:<backend_port>`, `http://localhost:<vite_port>`). Mọi cross-origin từ trang web ngoài trình duyệt bị từ chối để chống tấn công CSRF/DNS-rebinding vào localhost.
3. **Phân tách Quyền & Xác thực Phiên cục bộ (Local Session Authentication):**
   - Mỗi lần khởi động Backend, hệ thống sinh hai khóa ngẫu nhiên an toàn mật mã (`secrets.token_urlsafe(32)`, ≥ 256-bit entropy):
     - **`ADMIN_SESSION_TOKEN`:** Cấp riêng cho Desktop Supervisor (`PySide6`) thông qua kênh cục bộ an toàn (process pipe / tệp runtime có Windows ACL chỉ chủ sở hữu hiện tại được đọc). Gửi qua header `Authorization: Bearer <ADMIN_SESSION_TOKEN>` (hoặc header `X-LGS-Admin-Token` cho REST; subprotocol/first-frame auth cho `/ws/admin`).
     - **`RENDERER_STREAM_TOKEN`:** Khóa **chỉ đọc (read-only)** cấp cho màn hình Broadcast Renderer (`Three.js` / OBS Browser Source). **Tuyệt đối không có quyền gọi bất kỳ endpoint ghi/quản trị nào và không thể thay đổi gameplay.**
   - **Tuyệt đối không đặt `ADMIN_SESSION_TOKEN` vào Broadcast URL**, query string của OBS hay mã nguồn frontend.
   - **Tuyệt đối không ghi credentials/tokens vào logs, crash dumps hay `audit_logs`.**
4. **Phân biệt Public Local Health vs Privileged Operations:**
   - **Public Local (Loopback, không yêu cầu token):** Duy nhất `GET /api/v1/health` — chỉ trả về thông tin sống tối thiểu không nhạy cảm (`ok`, `status`, `version`, `db_smoke_ok`, `uptime_s`). Không trả đường dẫn tệp hệ thống, không trả cấu hình hay secret.
   - **Read-Only Renderer Scope (`RENDERER_STREAM_TOKEN`):** Chỉ được phép kết nối `/ws/renderer` và đọc tệp tĩnh đã xác thực qua `GET /api/v1/assets/{asset_id}/files/{rel_path}` (chặn path traversal, không expose đường dẫn đĩa tùy ý).
   - **Privileged Admin Scope (`ADMIN_SESSION_TOKEN` bắt buộc):** Toàn bộ các REST endpoint còn lại (`/metrics`, `/settings`, `/games`, `/sessions`, `/players`, `/assets` metadata/import, `/simulator`, `/gm/*`, `/live-studio`, `/analytics`) và WebSocket `/ws/admin`.
5. **WebSocket Authentication & Origin Validation:**
   - Cả `/ws/admin` và `/ws/renderer` bắt buộc kiểm tra header `Origin` thuộc allowlist local (hoặc non-browser native Qt client có token hợp lệ) và xác thực đúng loại token ngay khi handshake/khung xác thực đầu tiên; đóng ngay với mã `1008 Policy Violation` nếu không hợp lệ.
   - Mọi thông điệp lạ hoặc yêu cầu đột biến gameplay gửi từ `/ws/renderer` bị từ chối cứng và ghi cảnh báo bảo mật.

---

## 2. REST API Endpoints (Đồng bộ Implementation Phase với `ROADMAP.md` & `GD01_SCOPE.md`)

### 2.1 System & Health
| Method | Endpoint | Auth Scope | Phase | Mô tả |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | Public Local | **`GD01`** | Trạng thái sống tối thiểu của Backend & SQLite smoke (không lộ dữ liệu nhạy cảm) |
| `GET` | `/api/v1/metrics` | Admin Token | **`GD02+`** | Chỉ số queue depth, write-queue, latency p50/p95, WS clients, FPS telemetry |
| `GET` | `/api/v1/settings` | Admin Token | **`GD02+`** | Lấy cấu hình hệ thống (các trường `is_secret=1` bị redact thành `"***"`) |
| `PATCH` | `/api/v1/settings/{key}` | Admin Token | **`GD02+`** | Cập nhật 1 cấu hình hợp lệ; ghi `audit_logs` |

### 2.2 Game Registry & Plugins (`GD05+` — Admin Token)
| Method | Endpoint | Auth Scope | Phase | Mô tả |
|---|---|---|---|---|
| `GET` | `/api/v1/games` | Admin Token | `GD05` | Danh sách toàn bộ Game Plugins đã đăng ký trong allowlist `games/` |
| `GET` | `/api/v1/games/{plugin_id}` | Admin Token | `GD05` | Chi tiết manifest, trạng thái tài nguyên, `commands.json` và config schema |
| `POST` | `/api/v1/games/rescan` | Admin Token | `GD05` | Quét lại trusted built-in plugins trong `games/` |

### 2.3 Game Sessions (`GD02` CRUD / `GD05` Lifecycle — Admin Token)
| Method | Endpoint | Auth Scope | Phase | Mô tả |
|---|---|---|---|---|
| `GET` | `/api/v1/sessions` | Admin Token | `GD02` | Danh sách các phiên live (phân trang) |
| `POST` | `/api/v1/sessions` | Admin Token | `GD02` | Tạo phiên mới `{ plugin_id, world_scope, channel_id, source_mode }` |
| `GET` | `/api/v1/sessions/{session_id}` | Admin Token | `GD02` | Trạng thái chi tiết phiên, `sim_elapsed_ms`, `last_revision` |
| `POST` | `/api/v1/sessions/{session_id}/start` | Admin Token | `GD05` | Khởi chạy phiên (từ chối `409` nếu đang có phiên khác `RUNNING`) |
| `POST` | `/api/v1/sessions/{session_id}/pause` | Admin Token | `GD05` | Đóng băng `SimulationClock` và ngừng tích lũy XP |
| `POST` | `/api/v1/sessions/{session_id}/resume` | Admin Token | `GD05` | Tiếp tục `SimulationClock` |
| `POST` | `/api/v1/sessions/{session_id}/stop` | Admin Token | `GD05` | Dừng phiên có kiểm soát, hoàn tài nguyên giữ qua plugin, xả checkpoint |

### 2.4 Players (`GD02` CRUD / `GD11` Moderation — Admin Token)
| Method | Endpoint | Auth Scope | Phase | Mô tả |
|---|---|---|---|---|
| `GET` | `/api/v1/players` | Admin Token | `GD02` | Tìm kiếm / phân trang người chơi theo `plugin_id`, `status`, `query` |
| `GET` | `/api/v1/players/{player_id}` | Admin Token | `GD02` | Hồ sơ toàn cục và trạng thái theo game |
| `PATCH` | `/api/v1/players/{player_id}/moderation` | Admin Token | `GD11` | Kiểm duyệt đổi bí danh / ẩn khỏi scene (ghi `audit_logs`) |
| `POST` | `/api/v1/players/{player_id}/anonymize` | Admin Token | `GD11` | Xóa/ẩn danh dữ liệu theo yêu cầu người chơi (`confirm: true`, `ADR-012`) |

### 2.5 Assets (`GD07+`)
| Method | Endpoint | Auth Scope | Phase | Mô tả |
|---|---|---|---|---|
| `GET` | `/api/v1/assets` | Admin Token | `GD07` | Liệt kê assets theo `asset_type`, `is_placeholder`, `status` |
| `GET` | `/api/v1/assets/{asset_id}` | Admin Token | `GD07` | Chi tiết asset, các phiên bản, `validation_report` và `dependencies` |
| `POST` | `/api/v1/assets/import` | Admin Token | `GD07` | Nhập gói asset cục bộ (chỉ trong thư mục import cho phép), chạy `Asset Validator` |
| `PATCH` | `/api/v1/assets/{asset_id}/active-version` | Admin Token | `GD07` | Chuyển phiên bản active (chỉ chấp nhận phiên bản `VALID`) |
| `GET` | `/api/v1/assets/{asset_id}/files/{rel_path:path}` | Renderer / Admin Token | `GD07` | Stream tệp tĩnh đã xác thực cho Three.js (chặn path traversal — trả `400`/`403`, không lộ host path) |

### 2.6 Event Simulator (`GD04+` — Admin Token)
| Method | Endpoint | Auth Scope | Phase | Mô tả |
|---|---|---|---|---|
| `POST` | `/api/v1/simulator/events` | Admin Token | `GD04` | Bắn 1 sự kiện giả lập (`comment`, `gift`, `like`, `join`) vào Event Gateway |
| `POST` | `/api/v1/simulator/burst` | Admin Token | `GD04` | Chạy bài test tải burst `{ rate_per_sec, duration_sec, seed }` |
| `POST` | `/api/v1/simulator/replay` | Admin Token | `GD04` | Phát lại tệp kịch bản sự kiện phục vụ kiểm thử xác định |
| `POST` | `/api/v1/simulator/disconnect` | Admin Token | `GD04` | Giả lập mất kết nối provider (test grace period 15s) |
| `POST` | `/api/v1/simulator/reconnect` | Admin Token | `GD04` | Giả lập khôi phục kết nối provider |

### 2.7 Game Master, Events, Live Studio & Analytics (`GD12+`, `GD18+` — Admin Token)
| Method | Endpoint | Auth Scope | Phase | Mô tả |
|---|---|---|---|---|
| `POST` | `/api/v1/gm/control-mode` | Admin Token | `GD12` | Đặt chế độ `semi_auto` / `auto` / `manual` |
| `POST` | `/api/v1/gm/camera/override` | Admin Token | `GD10` / `GD12` | Chuyển camera thủ công `{ camera_id, target_entity_id, duration_ms }` |
| `POST` | `/api/v1/gm/events/trigger` | Admin Token | `GD12` | Kích hoạt sự kiện hợp lệ sớm (ví dụ World Boss khi idle) |
| `POST` | `/api/v1/gm/events/{event_id}/cancel` | Admin Token | `GD12` | Hủy sự kiện (`confirm: true`, ghi `audit_logs`) |
| `GET` | `/api/v1/gm/audit-logs` | Admin Token | `GD03` / `GD12` | Xem lịch sử thao tác GM (đã redact) |
| `GET` | `/api/v1/live-studio/readiness` | Admin Token | `GD18` | Bảng kiểm tra sẵn sàng phát sóng (`DEVELOPMENT`/`PRODUCTION` asset mode) + Broadcast URL (không chứa admin token) |
| `GET` | `/api/v1/analytics/sessions/{session_id}` | Admin Token | `GD18` / `GD19` | Báo cáo chỉ số vận hành và benchmark phiên |

---

## 3. WebSocket Contracts (`HIGH-006`)

### 3.1 Broadcast Renderer Stream: `ws://127.0.0.1:<port>/ws/renderer` (`GD08+`)
- **Auth & Origin:** Bắt buộc xác thực `RENDERER_STREAM_TOKEN` (chỉ đọc) + `Origin` thuộc allowlist local. **Renderer tuyệt đối không được gửi lệnh làm thay đổi trạng thái gameplay.**

**Server → Renderer:**
- `STATE_SNAPSHOT`: Gửi ngay khi kết nối, khi Backend đổi `stream_epoch` hoặc phản hồi `SNAPSHOT_REQUEST`.
  ```json
  {
    "type": "STATE_SNAPSHOT",
    "schema_version": "1.0.0",
    "stream_epoch": "ep_01J9X7Z0...",
    "session_id": "sess_01",
    "plugin_id": "cultivation_online",
    "snapshot_seq": 3,
    "revision": 42,
    "request_id": "sreq_01J9X8...",
    "sim_elapsed_ms": 125000,
    "session_state": "RUNNING",
    "world": { "map_asset_id": "TT_MAP001", "map_version": "0.1.0", "asset_mode": "DEVELOPMENT" },
    "entities": [],
    "active_event": null,
    "camera": { "active_camera_id": "CAM01", "pip_camera_id": null, "priority": 10 },
    "overlays": { "pinned": {}, "queue": [] }
  }
  ```
- `STATE_DELTA`: Phát thay đổi tăng dần theo `(stream_epoch, session_id, revision)`.
  ```json
  {
    "type": "STATE_DELTA",
    "schema_version": "1.0.0",
    "stream_epoch": "ep_01J9X7Z0...",
    "session_id": "sess_01",
    "from_revision": 42,
    "to_revision": 43,
    "ops": [
      { "op": "entity_upsert", "entity": { "id": "p_01", "display_name": "Đạo Hữu A", "state": "CULTIVATING" } },
      { "op": "vfx_trigger", "effect_id": "aura_breakthrough", "entity_id": "p_01", "ttl_ms": 3000 }
    ]
  }
  ```
- `HEARTBEAT`: Gửi định kỳ mỗi `5s` kèm `stream_epoch`, `session_id`, `latest_revision`.

**Renderer → Server (Chỉ đọc / Đồng bộ & Telemetry):**
- `SNAPSHOT_REQUEST`:
  ```json
  {
    "type": "SNAPSHOT_REQUEST",
    "request_id": "sreq_01J9X8...",
    "stream_epoch": "ep_01J9X7Z0...",
    "session_id": "sess_01",
    "last_revision": 42,
    "reason": "initial | reconnect | gap_detected | overlap_detected | epoch_or_session_mismatch"
  }
  ```
- `RENDERER_TELEMETRY`: `{ "type": "RENDERER_TELEMETRY", "fps": 58.4, "frame_time_p95_ms": 17.2, "draw_calls": 94, "visible_entities": 60 }`

**Quy tắc xử lý Đồng bộ Bắt buộc phía Renderer:**
| Tình huống | Điều kiện phát hiện | Hành động bắt buộc của Renderer |
|---|---|---|
| **Delta hợp lệ** | `delta.stream_epoch == current_epoch` AND `delta.session_id == current_session_id` AND `delta.from_revision == last_applied_revision` AND `to_revision > from_revision` | Apply `ops` nguyên tử, cập nhật `last_applied_revision = to_revision` |
| **Stale Snapshot** | Cùng `stream_epoch` và (`snapshot_seq < last_applied_snapshot_seq` OR `revision < last_applied_revision`) | **Bỏ qua (drop)** để không kéo lùi trạng thái hiển thị |
| **Duplicate Delta** | Cùng `stream_epoch` + `session_id` và `to_revision <= last_applied_revision` | **Bỏ qua (idempotent no-op)** |
| **Overlapping Revision** | Cùng `stream_epoch` + `session_id` và `from_revision < last_applied_revision < to_revision` | Không apply; chuyển `RESYNCING` và gửi `SNAPSHOT_REQUEST(reason="overlap_detected")` |
| **Revision Gap** | Cùng `stream_epoch` + `session_id` và `from_revision > last_applied_revision` | Không apply; chuyển `RESYNCING` và gửi `SNAPSHOT_REQUEST(reason="gap_detected")` |
| **Backend Restart / Đổi Phiên** | `stream_epoch != current_epoch` OR `session_id != current_session_id` | Xóa scene cache cục bộ, chuyển `RESYNCING` và yêu cầu `STATE_SNAPSHOT` mới |
| **Renderer Reconnect** | WS đóng và kết nối lại | Chuyển `AWAITING_SNAPSHOT`, bỏ qua delta cho tới khi áp dụng `STATE_SNAPSHOT` mới |

### 3.2 Desktop Admin Stream: `ws://127.0.0.1:<port>/ws/admin` (`GD03+`)
- **Auth & Origin:** Bắt buộc `ADMIN_SESSION_TOKEN` + `Origin` validation; đóng kết nối mã `1008` nếu xác thực thất bại.
- Đẩy cập nhật thời gian thực cho PySide6 Desktop UI: trạng thái phiên, danh sách lệnh bị từ chối kèm `reason_code`, bảng người chơi, hàng chờ sự kiện, trạng thái Connector, FPS/Queue telemetry và cảnh báo lỗi.
- Tuyệt đối tách riêng khỏi `/ws/renderer` để không bao giờ rò rỉ thông tin quản trị sang màn hình phát sóng.
