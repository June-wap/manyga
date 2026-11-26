# PLATFORM MODULE DESIGN — LIVEGAME STUDIO

**Phiên bản:** 1.0.0 (GD00 Baseline)  
**Phạm vi:** Thiết kế đầy đủ 37 module Platform và phân định ranh giới với Game Plugin (`GAME001 – cultivation_online`).  
**Lưu ý:** Không triển khai mã nguồn các module trong GD00; mỗi module được gắn đúng giai đoạn phát triển (`GD01`–`GD20`).

---

## 1. Phân định Ranh giới: Platform Shared Modules vs Game-Specific Logic

| Tầng | Phạm vi sở hữu | Ví dụ cụ thể | Quy tắc phụ thuộc |
|---|---|---|---|
| **Platform Core (`core/`)** | Hạ tầng lõi tối thiểu dùng cho mọi ứng dụng và module | Application Core, Configuration Manager, Logging System, Database Manager, Clock, Base Contracts | Không phụ thuộc bất kỳ tầng nào khác |
| **Platform Modules (`modules/`)** | 33 năng lực nền tảng tái sử dụng cho 100+ mini game | Event Gateway/Bus/Simulator, Command Parser, Plugin Manager, Player Manager, Asset System, 3D Runtime, Camera Director, Overlay, Reward Ledger, Game Master, Live Studio, OBS, Analytics, TikTok Connector | Chỉ phụ thuộc `core/` và module nền tầng thấp hơn; **cấm import `games/*`** |
| **Game Plugin (`games/cultivation_online/`)** | Luật chơi, công thức cân bằng, state machine và bảng CSDL riêng của Tu Tiên Online | Cảnh giới (Phàm Nhân..Kim Đan), 3 nghề (Kiếm/Đan/Thể Tu), công thức Boss Bạch Lang Vương, luật Tiểu Thiên Kiếp, lệnh `!dotpha`/`!dokiep`/`!hothe`, cấu hình map Thanh Vân Tông | Chỉ gọi Platform qua `GAME_PLUGIN_CONTRACT.md` và Application Services |

---

## 2. Đặc tả chi tiết 37 Module Platform

### Nhóm A — Core Infrastructure (GD01–GD02)

#### 1. Application Core (`core/app`)
- **Responsibility:** Composition root của Backend, quản lý vòng đời khởi động/tắt sạch (Acquire → Run → Restore), đăng ký dependency container và health state tổng.
- **Inputs:** CLI args, environment config, OS shutdown signals (`SIGINT`/`SIGTERM`).
- **Outputs:** Running application context, `/api/v1/health` payload, clean exit code.
- **Dependencies:** Configuration Manager, Logging System, Database Manager.
- **Public interfaces:** `ApplicationKernel.start()`, `ApplicationKernel.shutdown()`, `ApplicationKernel.get_health()`.
- **Data ownership:** Trạng thái vòng đời tiến trình trong bộ nhớ (không lưu DB).
- **Failure handling:** Fail-fast khi thiếu cấu hình bắt buộc hoặc DB lỗi không phục hồi được; đảm bảo luôn chạy cleanup hooks khi gặp exception.
- **Security boundaries:** Ép bind mặc định `127.0.0.1`; chặn khởi chạy nếu phát hiện cấu hình unsafe trái chính sách.
- **Testing strategy:** Unit test lifecycle hooks, integration test startup/shutdown không rò rỉ handle hay orphan task.
- **Development phase:** `GD01`.

#### 2. Configuration Manager (`core/config`)
- **Responsibility:** Nạp, hợp lệ hóa (Pydantic v2), phân tầng cấu hình (default → file local → DB `application_settings` → env override hợp lệ) và quản lý versioning cấu hình.
- **Inputs:** Config files (`config.toml`/`.json`), bảng `application_settings`, biến môi trường có tiền tố `LGS_`.
- **Outputs:** Typed immutable settings object, config validation errors.
- **Dependencies:** Pydantic v2 (std/core).
- **Public interfaces:** `ConfigManager.load()`, `ConfigManager.get(key)`, `ConfigManager.update_setting(key, value, actor)`.
- **Data ownership:** Bảng `application_settings`.
- **Failure handling:** Từ chối cấu hình sai kiểu/ngoài biên an toàn; giữ nguyên cấu hình hợp lệ trước đó khi update lỗi.
- **Security boundaries:** Đánh dấu `SecretStr` cho mọi khóa nhạy cảm; cấm trả giá trị secret qua REST API hoặc logs.
- **Testing strategy:** Unit test precedence order, schema validation, redaction khi serialize.
- **Development phase:** `GD01` (cơ bản), `GD02` (DB persistence).

#### 3. Logging System (`core/logging`)
- **Responsibility:** Cung cấp structured logging (JSONL xoay vòng file + console), correlation ID theo session/event và bộ lọc che giấu thông tin nhạy cảm.
- **Inputs:** Log records từ toàn bộ Backend/Modules/Plugins.
- **Outputs:** Rotating log files (`logs/app.jsonl`), stdout/stderr, stream log tóm tắt cho Desktop UI.
- **Dependencies:** Configuration Manager.
- **Public interfaces:** `get_logger(name)`, `bind_context(session_id, event_id)`, `redact_payload(data)`.
- **Data ownership:** File log cục bộ có chính sách retention (mặc định xoay vòng theo dung lượng/ngày).
- **Failure handling:** Nếu lỗi ghi đĩa, fallback ghi stderr mà không làm sập luồng gameplay.
- **Security boundaries:** Redact bắt buộc `token`, `secret`, `cookie`, `password`, `authorization`, `api_key`; không log raw chat dài hạn vượt chính sách retention.
- **Testing strategy:** Unit test redaction filter, rotation policy, UTF-8 Tiếng Việt không vỡ ký tự.
- **Development phase:** `GD01`.

#### 4. Database Manager (`core/database`)
- **Responsibility:** Quản lý SQLAlchemy 2.x engine cho SQLite, áp dụng PRAGMA bắt buộc (`WAL`, `foreign_keys=ON`, `busy_timeout`), vận hành **database-wide centralized write coordinator** (bounded write queue / global write serializer đảm bảo tối đa **1 write transaction hoạt động trên toàn DB tại một thời điểm** — không coi per-player lock là đủ cho SQLite), cung cấp `UnitOfWork` có transaction timeout, hỗ trợ Alembic migration và local backup.
- **Inputs:** Database path từ Configuration Manager, Alembic migration scripts, write/read transaction callables.
- **Outputs:** Serialized transactional sessions, backup snapshots, DB health & write-queue metrics.
- **Dependencies:** Configuration Manager, Logging System.
- **Public interfaces:** `DatabaseManager.read_session()`, `DatabaseManager.write_transaction(timeout_ms)`, `UnitOfWork.commit()`, `UnitOfWork.rollback()`, `DatabaseManager.verify_schema()`, `DatabaseManager.shutdown()`, `DatabaseManager.create_backup()`.
- **Data ownership:** Toàn bộ kết nối vật lý tới tệp SQLite cục bộ.
- **Failure handling:** Tự rollback ngay khi exception hoặc vượt transaction timeout; từ chối có cấu trúc khi bounded write queue đầy; drain sạch hàng đợi ghi và chạy `PRAGMA wal_checkpoint(TRUNCATE)` khi graceful shutdown.
- **Security boundaries:** Chỉ Backend process được ghi (`ADR-014`); ngăn đường dẫn DB thoát khỏi thư mục dữ liệu cấu hình.
- **Testing strategy:** Integration test persistence qua restart, FK enforcement, WAL mode, concurrent multi-player write serialization không gây `SQLITE_BUSY`, transaction timeout rollback và Alembic upgrade/downgrade.
- **Development phase:** `GD01` (SQLite smoke test), `GD02` (Alembic, centralized single-writer coordinator & full UoW).

#### 5. Application Services (`modules/application_services`)
- **Responsibility:** Lớp điều phối use-case giữa API/UI và các domain module (orchestration, transaction boundary, authorization check cho hành động GM, phát audit log).
- **Inputs:** Command/Query DTO từ REST API, WebSocket và Event pipeline.
- **Outputs:** Result DTO chuẩn hóa, domain events, audit entries.
- **Dependencies:** Database Manager, Logging System, các Domain Modules.
- **Public interfaces:** `SessionAppService`, `PlayerAppService`, `AssetAppService`, `GameMasterAppService`, `SettingsAppService`.
- **Data ownership:** Không sở hữu bảng riêng; điều phối transaction qua các repository sở hữu bảng.
- **Failure handling:** Ánh xạ domain exceptions sang mã lỗi API chuẩn (`API_CONTRACT.md`), đảm bảo rollback sạch.
- **Security boundaries:** Kiểm tra nguồn gọi (chỉ chấp nhận GM actions từ kênh admin loopback), ghi `audit_logs` cho mọi thao tác nhạy cảm.
- **Testing strategy:** Integration tests cho từng use-case thực tế dùng SQLite thật (không chỉ mock repository).
- **Development phase:** `GD02`.

---

### Nhóm B — Plugin & Session Management (GD05)

#### 6. Game Plugin Manager (`modules/plugin_manager`)
- **Responsibility:** Nạp, xác thực tương thích phiên bản Platform/Contract, quản lý vòng đời (`load → init → start → pause → resume → stop → unload`) và cô lập lỗi của Game Plugin đang chạy.
- **Inputs:** Plugin ID cần kích hoạt, manifest từ Game Registry, Platform Service Facade.
- **Outputs:** Active `GamePlugin` instance, plugin lifecycle state events.
- **Dependencies:** Game Registry, Configuration Manager, Logging System, Application Services.
- **Public interfaces:** `load_plugin(plugin_id)`, `activate_plugin(plugin_id, session_ctx)`, `deactivate_plugin()`, `get_active_plugin()`.
- **Data ownership:** Trạng thái runtime plugin trong bộ nhớ; cập nhật trạng thái kích hoạt trong `game_plugins`.
- **Failure handling:** Nếu plugin lỗi khi nạp hoặc vượt ngưỡng exception trong runtime, cách ly và chuyển session sang `PAUSED_ERROR`, không crash Backend.
- **Security boundaries:** Chỉ nạp **trusted built-in plugins** khớp chính xác **bảng static allowlist (`TRUSTED_BUILTIN_PLUGINS`)** (`ADR-010`) — không chỉ dựa vào kiểm tra tiền tố đường dẫn module; từ chối tuyệt đối dynamic import ngoài allowlist.
- **Testing strategy:** Contract tests bằng fake/dummy plugin thứ 2 (`dummy_test_game`) cùng song song với `cultivation_online`.
- **Development phase:** `GD05`.

#### 7. Game Registry (`modules/game_registry`)
- **Responsibility:** Khám phá, lưu danh mục metadata (`manifest.json`), kiểm tra hợp lệ schema manifest và cung cấp danh sách mini game cho Game Library UI.
- **Inputs:** Thư mục `games/*/manifest.json`, bảng `game_plugins`.
- **Outputs:** Danh sách `GamePluginMetadata`, capability flags (3D/2D, required assets, commands, config schema).
- **Dependencies:** Database Manager, Logging System.
- **Public interfaces:** `scan_builtin_plugins()`, `list_games()`, `get_game_manifest(plugin_id)`, `validate_manifest(manifest)`.
- **Data ownership:** Bảng `game_plugins`.
- **Failure handling:** Plugin có manifest lỗi bị đánh dấu `INVALID` với lý do rõ ràng, không làm hỏng việc nạp các game hợp lệ khác.
- **Security boundaries:** Kiểm tra schema Pydantic chặt chẽ, chống path traversal trong khai báo asset/entrypoint của manifest.
- **Testing strategy:** Unit test manifest hợp lệ/thiếu trường/sai semver/trùng `plugin_id`.
- **Development phase:** `GD05`.

#### 8. Game Session Manager (`modules/session_manager`)
- **Responsibility:** Quản lý vòng đời phiên livestream (`CREATED → RUNNING → PAUSED → STOPPING → COMPLETED / INTERRUPTED_RECOVERED`), vận hành `SimulationClock`, điều phối periodic tick (1s/2s), checkpoint 10s và Crash Recovery khi khởi động lại.
- **Inputs:** Lệnh Start/Pause/Resume/Stop từ GM, tín hiệu sức khỏe Connector, plugin ticks.
- **Outputs:** Session state transitions, tick invocations tới active plugin, state revisions gửi Renderer.
- **Dependencies:** Database Manager, Game Plugin Manager, Logging System, Audit Logs.
- **Public interfaces:** `create_session(plugin_id, world_scope)`, `start_session(id)`, `pause_session(id, reason)`, `resume_session(id)`, `stop_session(id)`, `recover_interrupted_sessions()`.
- **Data ownership:** Bảng `game_sessions`.
- **Failure handling:** Crash recovery ở tầng Platform chuyển session gián đoạn (`RUNNING`/`PAUSED`/`PAUSED_ERROR`/`STOPPING`) sang `INTERRUPTED_RECOVERED` và **ủy thác cho từng plugin qua `plugin.recover_after_crash(uow, ctx)`** — tuyệt đối không hardcode logic hay tên bảng của Tu Tiên Online trong Platform core (`ADR-018`).
- **Security boundaries:** Chỉ cho phép tối đa 1 phiên `RUNNING` cùng lúc trên một instance Desktop; mọi lệnh dừng/hủy ghi `audit_logs`.
- **Testing strategy:** Integration test state machine, clock freeze khi PAUSE, restart recovery và không mất dữ liệu tiến trình.
- **Development phase:** `GD02` (schema & CRUD), `GD05` (tick loop & plugin binding), `GD12` (recovery tích hợp).

---

### Nhóm C — Event Pipeline & Rules (GD04, GD06, GD12)

#### 9. Event Gateway (`modules/event_gateway`)
- **Responsibility:** Cổng tiếp nhận duy nhất cho mọi sự kiện đầu vào (từ Authorized Provider hoặc Event Simulator), chuẩn hóa về `NormalizedEvent`, kiểm tra schema, gắn `session_id`/`received_at` và chống trùng lặp tầng nhập.
- **Inputs:** Raw provider events (comment, gift, like, join, system) từ Adapter/Simulator.
- **Outputs:** `NormalizedEvent` hợp lệ đẩy vào Event Bus; bản ghi `event_ingestions` và `processed_events`.
- **Dependencies:** Database Manager, Event Bus, Logging System.
- **Public interfaces:** `ingest(raw_event, source_adapter)`, `get_ingestion_stats()`, `is_duplicate(source_ns, source_event_id)`.
- **Data ownership:** Bảng `event_ingestions`, `processed_events`.
- **Failure handling:** Sự kiện sai schema hoặc thiếu trường bắt buộc bị reject và tăng counter lỗi; khi `Event Bus` đạt `100%` thực hiện admission control trả mã tường minh `INGESTION_QUEUE_FULL` (`HTTP 429`) với enqueue timeout hữu hạn (`50ms`, retry `<=2`), ghi `REJECTED_BACKPRESSURE` — **không block vô hạn và không âm thầm drop lệnh gameplay**.
- **Security boundaries:** Kiểm tra chữ ký/nguồn adapter hợp lệ; cắt ngắn payload quá cỡ (DoS protection); không suy diễn ID khi provider không cung cấp ID ổn định.
- **Testing strategy:** Unit + integration test dedupe, malformed payload, replay cùng `source_event_id`.
- **Development phase:** `GD04`.

#### 10. Event Bus (`modules/event_bus`)
- **Responsibility:** Hàng đợi bất đồng bộ có giới hạn dung lượng (bounded priority/FIFO queue) phân phối sự kiện nội bộ giữa Event Gateway, Command Parser, Plugin, Camera/Overlay và Analytics mà không tạo ghép nối chặt.
- **Inputs:** `NormalizedEvent` và internal domain events.
- **Outputs:** Sự kiện phân phối tới subscribers theo đúng thứ tự cam kết và kiểm soát backpressure.
- **Dependencies:** Logging System.
- **Public interfaces:** `publish(topic, event, priority)`, `subscribe(topic, handler)`, `get_queue_depth()`, `drain()`.
- **Data ownership:** Bộ đệm hàng đợi trong bộ nhớ (ephemeral; dữ liệu bền vững đã nằm ở `event_ingestions`).
- **Failure handling:** Áp dụng load shedding theo tầng ưu tiên (`70%` gộp like/cosmetic, `90%` từ chối lệnh hiển thị phụ với `SYSTEM_BUSY`, `100%` từ chối tường minh `INGESTION_QUEUE_FULL` kèm metrics & auditability — không silent drop lệnh gameplay).
- **Security boundaries:** Giới hạn kích thước queue tối đa để chống OOM khi spam burst.
- **Testing strategy:** Stress test `100 events/s` trong 30s, kiểm tra ordering và backpressure metrics.
- **Development phase:** `GD04`.

#### 11. Event Simulator (`modules/event_simulator`)
- **Responsibility:** Giả lập đầy đủ sự kiện người xem (comment, join, gift, like, disconnect, reconnect, burst 100/s) và phát lại kịch bản sự kiện (Event Replay) phục vụ phát triển, demo và kiểm thử tự động mà không cần TikTok thật.
- **Inputs:** Kịch bản JSON/YAML, thao tác từ Desktop Simulator UI, tham số burst/seed.
- **Outputs:** Raw/Normalized simulated events gắn `source = "simulator"` đẩy vào Event Gateway.
- **Dependencies:** Event Gateway, Logging System.
- **Public interfaces:** `emit_comment(player_id, nickname, text)`, `emit_gift(player_id, gift_id, count)`, `run_scenario(path)`, `run_burst(rate, duration_s)`.
- **Data ownership:** Không sở hữu bảng DB riêng; lưu file kịch bản test trong `tests/` hoặc `scripts/`.
- **Failure handling:** Báo lỗi kịch bản không hợp lệ trước khi chạy; luôn có nút Stop hủy kịch bản đang chạy.
- **Security boundaries:** Luôn gắn nhãn `source = "simulator"` rõ ràng trong `event_ingestions` và `audit_logs` để không bao giờ nhầm kết quả simulator với TikTok live thật.
- **Testing strategy:** Determinism test: chạy cùng kịch bản 2 lần với cùng seed/clock phải cho ra trạng thái DB giống hệt nhau.
- **Development phase:** `GD04`.

#### 12. Command Parser (`modules/command_parser`)
- **Responsibility:** Phân tích bình luận thành lệnh có cấu trúc (`ParsedCommand`) bằng quy tắc tường minh (case-insensitive, trim, alias Tiếng Việt có dấu, subcommand/arguments) **nạp động 100% từ tệp `commands.json` của từng plugin — tuyệt đối không hardcode lệnh của `cultivation_online` trong Platform và không dùng LLM**.
- **Inputs:** `NormalizedEvent` loại `comment`, bảng khai báo lệnh & aliases của active plugin.
- **Outputs:** `ParsedCommand(command_key, args, raw_text)` hoặc `None` (bình luận thường bỏ qua).
- **Dependencies:** Game Plugin Manager (lấy command registry).
- **Public interfaces:** `register_commands(plugin_id, command_specs)`, `parse(comment_text)`.
- **Data ownership:** Không sở hữu bảng DB; bảng ánh xạ lệnh nạp từ plugin manifest/spec.
- **Failure handling:** Bình luận không khớp cú pháp trả `None` an toàn; một comment chỉ trích xuất tối đa 1 lệnh hợp lệ đầu tiên.
- **Security boundaries:** Chặn tham số nhắm tới `player_id` người khác (mọi lệnh tự định tuyến bằng `sender_player_id`); giới hạn độ dài chuỗi parse để chống ReDoS.
- **Testing strategy:** Unit test toàn bộ lệnh MVP (bao gồm `!hothe`, `!hotheauto`, `!hotheauto on`, `!hotheauto off` và aliases có dấu/không dấu), ký tự lạ, chuỗi rất dài, HTML injection.
- **Development phase:** `GD06`.

#### 13. Event Scheduler (`modules/event_scheduler`)
- **Responsibility:** Lập lịch tự động và định kỳ các sự kiện phiên live (ví dụ: boss đầu tiên phút 5, lặp mỗi 10 phút; bảng hướng dẫn/xếp hạng mỗi 5 phút) dựa trên `SimulationClock`.
- **Inputs:** Lịch cấu hình theo plugin/session, `SimulationClock` ticks, lệnh tạo/hủy lịch từ GM.
- **Outputs:** Yêu cầu kích hoạt sự kiện (`ScheduledEventDue`) gửi tới Event Director.
- **Dependencies:** Database Manager, Game Session Manager, Event Director.
- **Public interfaces:** `schedule_event(spec)`, `cancel_scheduled(id)`, `list_upcoming(session_id)`, `tick(sim_now_ms)`.
- **Data ownership:** Bảng `scheduled_events`.
- **Failure handling:** Nếu một lịch bị trễ do event khác đang chạy, lùi lịch có kiểm soát — **không chạy bù hàng loạt (no catch-up storm)**.
- **Security boundaries:** Mọi chỉnh sửa lịch từ GM chỉ áp dụng cho sự kiện chưa bắt đầu và được ghi `audit_logs`.
- **Testing strategy:** Deterministic clock test cho lịch 0–5–15–25 phút, pause/resume và conflict deferral.
- **Development phase:** `GD12`.

#### 14. Event Director (`modules/event_director`)
- **Responsibility:** Trọng tài điều phối xung đột sự kiện (mutual exclusion & priority): đảm bảo tại một thời điểm chỉ có tối đa 1 World Event active và 1 Personal Event (như Tiểu Thiên Kiếp) active theo luật ưu tiên, không cắt ngang kiếp đã bắt đầu.
- **Inputs:** Yêu cầu từ Event Scheduler, Event Queue và thao tác kích hoạt sớm/hủy của GM.
- **Outputs:** Quyết định `START_EVENT`, `DEFER_EVENT`, `REJECT_CONFLICT`, `CANCEL_EVENT`.
- **Dependencies:** Event Queue, Game Plugin Manager, Game Session Manager.
- **Public interfaces:** `request_start(event_request)`, `complete_event(event_id)`, `cancel_active(event_id, reason)`, `get_active_events()`.
- **Data ownership:** Trạng thái điều phối runtime; ghi nhận chuyển trạng thái vào `scheduled_events` và bảng event của plugin.
- **Failure handling:** Nếu event timeout hoặc plugin lỗi, tự chuyển sang bước cleanup/refund an toàn.
- **Security boundaries:** Không cho phép GM bỏ qua điều kiện hợp lệ của phần thưởng khi kích hoạt event sớm.
- **Testing strategy:** State transition matrix tests cho mọi cặp xung đột (Boss vs Tribulation, Stop trong Active, GM force cancel).
- **Development phase:** `GD12`.

#### 15. Event Queue (`modules/event_queue`)
- **Responsibility:** Quản lý các hàng chờ hữu hạn có thứ tự xác định (FIFO theo `(received_at_monotonic, player_id)`), chống đăng ký trùng, áp dụng giới hạn kích thước/TTL và **tách biệt rõ 3 loại hàng chờ** (`Gameplay Execution Queue`, `Camera Focus Queue`, `Event Presentation Queue` — `ADR-020`).
- **Inputs:** Yêu cầu xếp hàng từ Plugin/Overlay/Camera (ví dụ hàng chờ Tiểu Thiên Kiếp tối đa 20, hàng chờ `!info` tối đa 20, `!find` tối đa 10).
- **Outputs:** Phần tử kế tiếp hợp lệ, trạng thái vị trí hàng chờ, mã từ chối `QUEUE_FULL` / `ALREADY_QUEUED`.
- **Dependencies:** Logging System.
- **Public interfaces:** `enqueue(queue_name, item, dedupe_key, ttl_ms)`, `dequeue(queue_name)`, `remove(queue_name, key)`, `peek_all(queue_name)`.
- **Data ownership:** Hàng đợi ephemeral (Overlay/Camera) trong RAM; hàng đợi bền vững (như Tribulation) ủy thác lưu trữ qua repository của plugin.
- **Failure handling:** Tự loại bỏ phần tử quá TTL; khi đầy trả lỗi rõ ràng không mở rộng RAM vô hạn.
- **Security boundaries:** Giới hạn tối đa 1 yêu cầu đang chờ mỗi `player_id` trên cùng một hàng chờ.
- **Testing strategy:** Unit test FIFO tie-break theo `player_id`, TTL expiry, cap overflow, idempotent enqueue.
- **Development phase:** `GD12`.

#### 16. Rule Engine (`modules/rule_engine`)
- **Responsibility:** Đánh giá tập luật chung của Platform trước/trong khi thực thi lệnh: cooldown theo player & nhóm lệnh, kiểm tra trạng thái hoạt động, giới hạn rate, kiểm tra chính sách quà tặng cosmetic (chặn mọi rule gắn quà với sức mạnh).
- **Inputs:** `ParsedCommand`, `PlayerContext`, `CooldownConfig`, `GiftMappingConfig`.
- **Outputs:** `RuleDecision(allowed: bool, reason_code: str, retry_after_ms: int)`.
- **Dependencies:** Configuration Manager, Logging System.
- **Public interfaces:** `check_cooldown(player_id, group_key, now_ms)`, `record_execution(...)`, `evaluate_gift_mapping(gift_event)`.
- **Data ownership:** Trạng thái cooldown runtime theo phiên; cấu hình gift mapping đọc từ `application_settings`/plugin config.
- **Failure handling:** Mặc định fail-closed (từ chối an toàn nếu thiếu cấu hình luật) và trả `reason_code` gọn cho GM.
- **Security boundaries:** Cưỡng chế ở tầng mã nguồn chính sách **Anti-P2W / Anti-Gambling** (`ADR-009`): `GiftMapping` chỉ được phát hành `CosmeticEffectIntent`, không có quyền gọi `RewardLedger` hay sửa chỉ số gameplay.
- **Testing strategy:** Unit test cooldown chính xác theo `SimulationClock`, gift mapping không thể tác động XP/ATK/HP.
- **Development phase:** `GD06`.

---

### Nhóm D — Player & Persistence (GD02, GD11)

#### 17. Player Manager (`modules/player_manager`)
- **Responsibility:** Quản lý hồ sơ người chơi toàn cục (`players`), ánh xạ định danh từ nhà cung cấp ngoài (`external_identities`), hồ sơ theo từng game (`player_game_profiles`), lọc/chuẩn hóa tên hiển thị (20 ký tự, escape HTML, profanity filter) và theo dõi `last_seen_at` (idle 5 phút / ẩn render 10 phút).
- **Inputs:** External identity `(provider, channel_id, external_user_id)`, display name, yêu cầu opt-out `!roi` hoặc xóa dữ liệu từ GM.
- **Outputs:** `PlayerProfile`, `PlayerGameProfile`, trạng thái hiện diện (`ACTIVE` / `IDLE` / `HIDDEN` / `OPTED_OUT`).
- **Dependencies:** Player Persistence, Logging System.
- **Public interfaces:** `resolve_or_create_player(...)`, `get_game_profile(player_id, plugin_id)`, `touch_activity(player_id, now_ms)`, `opt_out(player_id)`, `anonymize_player(player_id, actor)`.
- **Data ownership:** Bảng `players`, `external_identities`, `player_game_profiles`.
- **Failure handling:** Xử lý race condition khi 20+ người cùng `!join` đồng thời bằng unique constraint + transaction upsert an toàn.
- **Security boundaries:** Không dùng nickname làm khóa chính; không suy luận giới tính từ hồ sơ TikTok; sanitize/escape 100% display name; hỗ trợ quyền xóa/ẩn danh theo `ADR-012`.
- **Testing strategy:** Concurrency test 20 `!join` song song (AC01), đổi nickname không tạo duplicate, opt-out & anonymize giữ toàn vẹn FK.
- **Development phase:** `GD02` (core CRUD), `GD11` (activity tracking & opt-out).

#### 18. Player Persistence (`modules/player_persistence`)
- **Responsibility:** Cung cấp repository chuẩn hóa, cơ chế optimistic version checking, batch checkpoint mỗi 10s cho dữ liệu biến thiên nhanh (XP/vị trí) và flush nguyên tử khi thay đổi mốc quan trọng.
- **Inputs:** Dirty player state buffers, atomic save requests từ Application Services và Plugins.
- **Outputs:** Committed DB rows, persistence metrics (checkpoint duration, write count).
- **Dependencies:** Database Manager, Logging System.
- **Public interfaces:** `mark_dirty(profile_id)`, `flush_checkpoints()`, `save_atomic(uow, entity)`.
- **Data ownership:** Lớp truy cập lưu trữ cho `players`, `external_identities`, `player_game_profiles` (không sở hữu nghiệp vụ game).
- **Failure handling:** Khi lỗi commit, rollback toàn bộ transaction và giữ dirty flag để báo động/xử lý khôi phục.
- **Security boundaries:** Sử dụng SQLAlchemy parameterized queries 100% (chống SQL injection).
- **Testing strategy:** Persistence-across-restart test (AC02), checkpoint flush on shutdown, optimistic version conflict test.
- **Development phase:** `GD02` (repository), `GD11` (checkpointing).

---

### Nhóm E — 3D Runtime, World, Camera & Overlay (GD08–GD10)

#### 19. Character Engine (`modules/character_engine` + `frontend/src/character`)
- **Responsibility:** Quản lý vòng đời thực thể nhân vật trong thế giới chung (spawn, despawn, đổi ngoại hình/model binding, gắn nameplate, chuyển trạng thái hiển thị theo `Simulation State`).
- **Inputs:** State snapshot/delta nhân vật từ Backend, validated character assets từ Asset Registry.
- **Outputs:** Scene character actors, nameplate anchor positions, render budget status.
- **Dependencies:** Asset Registry, Animation Engine, 3D Runtime.
- **Public interfaces:** `spawnCharacter(dto)`, `updateCharacter(delta)`, `despawnCharacter(id)`, `setVisibilityTier(id, lod)`.
- **Data ownership:** Trạng thái hiển thị nhân vật trong bộ nhớ Frontend (ephemeral).
- **Failure handling:** Nếu GLB nhân vật lỗi hoặc thiếu, tự động fallback sang placeholder capsule/chibi chuẩn có màu phân biệt nghề và báo lỗi về telemetry.
- **Security boundaries:** Mọi nameplate hiển thị text đã escape HTML; không thực thi script từ metadata asset.
- **Testing strategy:** Frontend unit/integration test spawn/despawn 100 nhân vật, cleanup VRAM không rò rỉ sau chu kỳ spawn/despawn.
- **Development phase:** `GD09`.

#### 20. Animation Engine (`modules/animation_engine` + `frontend/src/animation`)
- **Responsibility:** Quản lý `AnimationMixer`, ánh xạ clip chuẩn (`idle`, `walk`, `run`, `meditation`, `cast`, `sword_attack`, `hit`, `defeat`, `celebrate`, boss clips), crossfade mượt và animation throttling theo mức LOD để tối ưu CPU.
- **Inputs:** Trạng thái hành động nhân vật/boss, danh sách animation clips đã validate trong manifest.
- **Outputs:** Cập nhật bone transforms theo frame và mức LOD.
- **Dependencies:** Character Engine, Asset Registry.
- **Public interfaces:** `playClip(entityId, clipName, options)`, `crossfade(entityId, from, to, duration)`, `setUpdateRate(entityId, hz)`.
- **Data ownership:** Ephemeral animation mixers/actions trong bộ nhớ Frontend.
- **Failure handling:** Nếu clip yêu cầu không tồn tại trên model, fallback sang `idle` và ghi cảnh báo 1 lần (không spam console mỗi frame).
- **Security boundaries:** Chỉ truy cập clip name khai báo hợp lệ trong Asset Manifest.
- **Testing strategy:** Test ánh xạ đủ bộ clip bắt buộc, fallback khi thiếu clip, dispose mixer khi despawn.
- **Development phase:** `GD09`.

#### 21. 3D Runtime (`frontend/src/runtime`)
- **Responsibility:** Khởi tạo và quản lý **một WebGLRenderer duy nhất** (`1080×1920`), vòng lặp render, ánh sáng, đổ bóng có kiểm soát, resize, WebSocket state sync (snapshot/delta), hiệu năng telemetry (FPS/frame time/draw calls) và WebGL resource disposal.
- **Inputs:** WebSocket `/ws/renderer`, cấu hình chất lượng hiển thị (LOD, PiP on/off, reduced flash).
- **Outputs:** Khung hình WebGL dọc `1080×1920`, telemetry hiệu năng gửi về Backend.
- **Dependencies:** Three.js, Asset Registry (HTTP asset loader), Map Manager, Character Engine, Camera Director, Overlay Engine.
- **Public interfaces:** `RuntimeEngine.mount(canvas)`, `RuntimeEngine.applySnapshot(snap)`, `RuntimeEngine.applyDelta(delta)`, `RuntimeEngine.dispose()`.
- **Data ownership:** Scene graph và GPU resources trong browser context.
- **Failure handling:** Lắng nghe `webglcontextlost`/`webglcontextrestored`; tự reconnect WebSocket với exponential backoff và gửi `SNAPSHOT_REQUEST` khi nối lại (AC11).
- **Security boundaries:** Chỉ kết nối tới origin Backend loopback cấu hình; không gọi CDN hay tải asset từ internet lúc runtime.
- **Testing strategy:** Vite/TypeScript build check, headless/browser smoke test render 9:16, reconnect snapshot test, dispose memory test.
- **Development phase:** `GD01` (skeleton 9:16), `GD08` (full runtime & sync).

#### 22. Map Manager (`modules/map_manager` + `frontend/src/world`)
- **Responsibility:** Nạp bản đồ 3D đã phân tách cấu trúc (decorative mesh, collision, walkable areas, zone anchors: `spawn_gate`, `cultivation_court`, `boss_arena`, `tribulation_platform`, `sect_hall`, `paths`), cấp phát slot logic (≥100 slot tu luyện) và cung cấp tọa độ anchor cho Navigation/Camera.
- **Inputs:** Map manifest & GLB (`TT_MAP001` hoặc placeholder map), yêu cầu cấp phát/thu hồi slot.
- **Outputs:** Zone anchors, slot assignments, rendered map scene group.
- **Dependencies:** Asset Registry, 3D Runtime.
- **Public interfaces:** `loadMap(mapAssetId)`, `allocateSlot(zoneId, entityId)`, `releaseSlot(entityId)`, `getZoneAnchor(zoneId)`.
- **Data ownership:** Cấp phát slot runtime theo phiên tại Backend; bản đồ 3D cache tại Frontend.
- **Failure handling:** Nếu hết slot hiển thị trực tiếp, trả về trạng thái `RENDER_WAITLIST` (gameplay vẫn tiếp tục bình thường); nếu lỗi tải map GLB, dựng placeholder terrain chuẩn theo metadata zones.
- **Security boundaries:** Validate tọa độ anchor hữu hạn (chặn `NaN`/`Infinity`) và đường dẫn file trong Asset Contract.
- **Testing strategy:** Test cấp phát/thu hồi 100+ slot không trùng vị trí, kiểm tra đủ 6 zone của `TT_MAP001`.
- **Development phase:** `GD10`.

#### 23. Navigation Engine (`modules/navigation_engine` + `frontend/src/navigation`)
- **Responsibility:** Tính toán đường đi nhẹ cho nhân vật di chuyển giữa các zone (`spawn_gate → cultivation_court → boss_arena / tribulation_platform`) theo waypoint graph / navmesh đã khai báo trên map.
- **Inputs:** Vị trí hiện tại, zone/slot đích, waypoint graph của map.
- **Outputs:** Đường đi nội suy (waypoints + tốc độ di chuyển), sự kiện `ARRIVED`.
- **Dependencies:** Map Manager.
- **Public interfaces:** `computePath(fromPos, toZoneOrSlot)`, `stepMovement(entityId, dt)`.
- **Data ownership:** Trạng thái di chuyển runtime (ephemeral).
- **Failure handling:** Nếu không tìm thấy path do cấu hình waypoint thiếu, di chuyển theo đường thẳng có clamp biên an toàn (không để nhân vật rơi khỏi map hoặc bị kẹt vô hạn).
- **Security boundaries:** Giới hạn số node duyệt (bounded A*/BFS) để chống treo CPU.
- **Testing strategy:** Unit test pathfinding qua mọi cặp zone của Thanh Vân Tông, đảm bảo luôn hội tụ `ARRIVED`.
- **Development phase:** `GD10`.

#### 24. Camera Director (`modules/camera_director` + `frontend/src/camera`)
- **Responsibility:** Điều phối nhiều camera ảo (`CAM01`–`CAM05`) và tối đa 1 PiP trên một màn hình phát sóng theo bảng độ ưu tiên (`Boss 90 > Tribulation 80 > Breakthrough 50 > !find 30 > Newcomer 20 > Idle 10`), `min_hold = 5s`, chuyển mượt `0.6s`, hỗ trợ Manual Override của GM (tự trả về auto sau `20s`).
- **Inputs:** `CameraIntent` từ Plugin/Events, lệnh override từ Game Master.
- **Outputs:** Trạng thái camera chính + trạng thái PiP gửi xuống 3D Runtime.
- **Dependencies:** Event Queue, Map Manager, 3D Runtime.
- **Public interfaces:** `submitIntent(intent)`, `setManualOverride(cameraId, targetId, durationMs)`, `togglePip(enabled)`, `tick(nowMs)`.
- **Data ownership:** Trạng thái camera runtime trong bộ nhớ.
- **Failure handling:** Nếu target entity biến mất giữa shot, quay mượt về `CAM01` mặc định; camera không bao giờ tác động ngược vào gameplay.
- **Security boundaries:** Tách biệt quyền ưu tiên: viewer (`!find`) tối đa priority `30`, không thể cướp camera Boss (`90`) hay Tribulation (`80`).
- **Testing strategy:** Unit test priority preemption, min_hold 5s, `!find` không ngắt boss (AC10), GM override auto-return 20s.
- **Development phase:** `GD10`.

#### 25. Overlay Engine (`modules/overlay_engine` + `frontend/src/overlay`)
- **Responsibility:** Quản lý lớp HUD/Overlay trên màn hình dọc `1080×1920`: Header (tên game, số người hoạt động, đếm ngược event), Context Card (`!info` tối đa 3s, queue 20, TTL 60s), Leaderboard/Guide luân phiên, Toast gộp cho người mới/đột phá, Boss HP bar, Tribulation progress và Safe Area guides.
- **Inputs:** `OverlayRequest` từ Plugin/Services, cấu hình Safe Area và giảm nhấp nháy.
- **Outputs:** Rendered DOM/Canvas overlay đồng bộ với 3D viewport.
- **Dependencies:** Event Queue, 3D Runtime.
- **Public interfaces:** `pushOverlay(req)`, `setPinnedBanner(data)`, `setSafeArea(margins)`, `clearExpired(nowMs)`.
- **Data ownership:** Hàng chờ hiển thị ephemeral (hết hạn tự bỏ, không ảnh hưởng gameplay).
- **Failure handling:** Hàng chờ đầy từ chối yêu cầu mới kèm lý do gọn; gộp các yêu cầu trùng theo `player_id`.
- **Security boundaries:** Escape HTML 100% (cấm `innerHTML` với dữ liệu viewer), không bao giờ hiển thị secret/log nội bộ lên broadcast overlay.
- **Testing strategy:** Test TTL expiry, queue cap 20, gộp thông báo khi 20 người `!join`, kiểm tra an toàn XSS và hiển thị safe area 9:16 (AC17).
- **Development phase:** `GD08` (layout 9:16), `GD16` (notifications/leaderboard overlays).

---

### Nhóm F — Universal Asset Management (GD07)

#### 26. Asset Library (`modules/asset_library`)
- **Responsibility:** Cung cấp giao diện truy vấn, lọc theo loại (`character`, `prop`, `map`, `animation`, `material`, `texture`, `effect`, `audio`, `ui`), xem metadata/phiên bản và phân phát tệp tĩnh đã xác thực qua loopback cho Frontend Renderer.
- **Inputs:** Truy vấn từ Desktop UI, Game Plugin và HTTP requests từ Three.js loader.
- **Outputs:** Asset metadata, danh sách phiên bản, luồng file nhị phân GLB/texture/audio an toàn.
- **Dependencies:** Asset Registry, Database Manager.
- **Public interfaces:** `list_assets(filter)`, `get_asset(asset_id, version)`, `resolve_file_path(asset_id, rel_path)`.
- **Data ownership:** Không sở hữu ghi trực tiếp; đọc từ `assets`, `asset_versions`, `asset_dependencies` và thư mục `assets/`.
- **Failure handling:** Khi thiếu asset mục tiêu, tự động trả đường dẫn placeholder hợp lệ cùng mã cảnh báo rõ ràng (AC14).
- **Security boundaries:** Chỉ phục vụ tệp đã đăng ký hợp lệ nằm trong `assets/` (chặn tuyệt đối path traversal và liệt kê thư mục tùy ý).
- **Testing strategy:** Integration test truy vấn theo loại/version, fallback placeholder, test tấn công path traversal (`../`, `..\\`, URL-encoded `%2e%2e`).
- **Development phase:** `GD07`.

#### 27. Asset Importer (`modules/asset_importer`)
- **Responsibility:** Nhập gói asset sản xuất từ bên ngoài (`TT-AS`) vào kho cục bộ `assets/`, tính toán mã băm SHA-256, gọi Asset Validator kiểm định và đăng ký phiên bản bất biến (immutable semantic version) vào Asset Registry.
- **Inputs:** Đường dẫn thư mục/gói asset cục bộ chứa `asset_manifest.json` và file tài nguyên.
- **Outputs:** `ImportResult(status, asset_id, version, validation_report)`.
- **Dependencies:** Asset Validator, Asset Registry, Database Manager.
- **Public interfaces:** `import_package(source_dir, actor)`, `import_placeholder(spec)`.
- **Data ownership:** Quản lý việc sao chép nguyên tử (staging → validate → atomic move) vào `assets/`.
- **Failure handling:** Nếu kiểm định thất bại ở bất kỳ bước nào, xóa sạch thư mục staging và giữ nguyên dữ liệu cũ (không để asset hỏng nửa vời).
- **Security boundaries:** Chặn symlink thoát gốc, chặn tệp thực thi (`.exe`, `.dll`, `.bat`, `.ps1`, `.py`), giới hạn kích thước gói nhập tối đa.
- **Testing strategy:** Integration test import GLB hợp lệ, từ chối manifest lỗi, từ chối trùng version khác hash, rollback staging khi lỗi.
- **Development phase:** `GD07`.

#### 28. Asset Validator (`modules/asset_validator`)
- **Responsibility:** Kiểm định nghiêm ngặt gói asset theo `docs/platform/ASSET_CONTRACT.md`: schema JSON manifest, semver, chuẩn nhị phân glTF 2.0/GLB header, relative paths, SHA-256 hash, license/provenance, metadata đơn vị mét/Y-up, danh sách animation và LOD metadata.
- **Inputs:** Thư mục staging chứa manifest và tệp asset.
- **Outputs:** `ValidationReport(passed: bool, errors[], warnings[], checked_hashes)`.
- **Dependencies:** Logging System.
- **Public interfaces:** `validate_package(staging_dir)`, `verify_checksums(asset_dir, manifest)`, `inspect_glb_header(file_path)`.
- **Data ownership:** Kết quả kiểm định lưu trong `asset_versions.validation_report_json`.
- **Failure handling:** Thu thập toàn bộ lỗi (không dừng ở lỗi đầu tiên) để Technical Artist sửa dứt điểm trong 1 lượt.
- **Security boundaries:** Kiểm tra magic bytes `glTF` thực tế (không tin đuôi file), cấm đường dẫn tuyệt đối/traversal, cấm URI external `http://` bên trong glTF.
- **Testing strategy:** Unit test với bộ fixture: GLB chuẩn, file giả mạo GLB, sai hash, thiếu license, path traversal, external URI.
- **Development phase:** `GD07`.

#### 29. Asset Registry (`modules/asset_registry`)
- **Responsibility:** Lưu trữ metadata, lịch sử phiên bản (semver), đồ thị phụ thuộc (`asset_dependencies`) và kiểm tra tính sẵn sàng tài nguyên của một Game Plugin theo chế độ `DEVELOPMENT` (cho phép placeholder tương thích kèm cảnh báo) vs `PRODUCTION` (bắt buộc tồn tại đủ `required_assets`, `validation_status=VALID`, không tự bỏ qua dependency thiếu — `ADR-016`).
- **Inputs:** Dữ liệu asset đã qua kiểm định từ Asset Importer; danh sách phụ thuộc từ Game Plugin manifest.
- **Outputs:** Danh mục phiên bản active/deprecated, báo cáo thiếu hụt phụ thuộc (`MissingAssetReport`).
- **Dependencies:** Database Manager.
- **Public interfaces:** `register_version(asset_meta)`, `set_active_version(asset_id, version)`, `check_plugin_dependencies(plugin_id)`.
- **Data ownership:** Bảng `assets`, `asset_versions`, `asset_dependencies`.
- **Failure handling:** Không cho phép xóa phiên bản đang được plugin active tham chiếu; đánh dấu `DEPRECATED` thay vì xóa cứng.
- **Security boundaries:** Đảm bảo ràng buộc duy nhất `(asset_id, version)` và tính toàn vẹn khóa ngoại.
- **Testing strategy:** DB integration test FK/unique constraints, dependency resolution và version pinning.
- **Development phase:** `GD07`.

---

### Nhóm G — Economy, Control, Audio & Broadcast (GD03, GD13, GD16–GD18)

#### 30. Reward Ledger (`modules/reward_ledger`)
- **Responsibility:** Sổ cái phần thưởng bất biến và idempotent dùng chung cho mọi mini game, bảo đảm mỗi phần thưởng cho một cặp `(event_id, player_id, reward_kind)` chỉ được hạch toán **duy nhất một lần** trong cùng transaction cập nhật số dư.
- **Inputs:** `GrantRewardRequest(session_id, plugin_id, event_id, player_id, reward_kind, amount, metadata)` bên trong `UnitOfWork`.
- **Outputs:** `LedgerEntry` mới hoặc `ALREADY_GRANTED` (idempotent no-op).
- **Dependencies:** Database Manager, Logging System.
- **Public interfaces:** `grant_idempotent(uow, request)`, `list_player_rewards(player_id, plugin_id)`, `verify_event_payouts(event_id)`.
- **Data ownership:** Bảng `reward_ledger`.
- **Failure handling:** Bắt lỗi vi phạm unique key trả về kết quả idempotent (không cấp trùng khi replay hoặc crash giữa `REWARDING` — AC08).
- **Security boundaries:** Cấm Renderer hoặc Gift Mapping gọi trực tiếp; số lượng thưởng phải nguyên không âm; không hỗ trợ quy đổi tiền thật.
- **Testing strategy:** Replay & mid-reward crash recovery tests xác minh không cấp thưởng trùng.
- **Development phase:** `GD13`.

#### 31. Game Master (`modules/game_master`)
- **Responsibility:** Cung cấp bảng điều khiển nghiệp vụ vận hành cho Host: chọn chế độ `Semi-auto` (mặc định) / `Auto` / `Manual`, Pause/Resume/Stop khẩn cấp, triệu hồi/hủy sự kiện hợp lệ, override camera, kiểm duyệt tên/ẩn người chơi, xử lý xóa dữ liệu và xuất `audit_logs`.
- **Inputs:** Thao tác GM từ Desktop UI (kèm xác nhận cho lệnh hủy/xóa).
- **Outputs:** Thay đổi trạng thái phiên/event/camera, bản ghi `audit_logs`.
- **Dependencies:** Application Services, Game Session Manager, Event Director, Camera Director, Player Manager.
- **Public interfaces:** `set_control_mode(mode)`, `emergency_pause(reason)`, `trigger_event(type)`, `cancel_event(id, confirm)`, `moderate_player(player_id, action)`.
- **Data ownership:** Bảng `audit_logs`.
- **Failure handling:** Từ chối thao tác bất hợp lệ theo trạng thái hiện tại (ví dụ đổi cân bằng giữa trận boss chỉ áp dụng cho event mới).
- **Security boundaries:** Chỉ chấp nhận lệnh từ Desktop loopback; mọi hành động hủy/reset/xóa yêu cầu tham số xác nhận tường minh và ghi `audit_logs` đã redact.
- **Testing strategy:** Integration test Emergency Pause đóng băng đồng hồ (AC13), kiểm tra ghi đủ `audit_logs`.
- **Development phase:** `GD03` (UI shell & controls), `GD12` (full event/session control).

#### 32. Notification Engine (`modules/notification_engine`)
- **Responsibility:** Tạo thông báo tiếng Việt theo template (gộp thông báo khi nhiều người nhập môn/đột phá), xuất ra Overlay Toast/Feed và cung cấp cổng tùy chọn TTS có giới hạn tốc độ (tối đa 1 thông báo/5 giây).
- **Inputs:** Domain events (nhập môn, đột phá, boss spawn/kết thúc, thiên kiếp), cấu hình template/TTS.
- **Outputs:** Notification payloads gửi Overlay Engine và Audio Engine.
- **Dependencies:** Overlay Engine, Audio Engine, Configuration Manager.
- **Public interfaces:** `notify(template_key, params, priority)`, `flush_batched()`, `set_tts_enabled(bool)`.
- **Data ownership:** Cấu hình mẫu thông báo và bộ đệm gộp ngắn hạn trong bộ nhớ.
- **Failure handling:** Nếu TTS engine lỗi hoặc không có trên máy, tắt TTS nhẹ nhàng và vẫn hiển thị overlay chữ bình thường.
- **Security boundaries:** **Không bao giờ đọc nội dung bình luận chat thô chưa kiểm duyệt qua TTS**; chỉ render các biến đã sanitize trong template.
- **Testing strategy:** Test rate-limit 1/5s, batching 20 người `!join`, kiểm tra không đẩy raw chat vào TTS.
- **Development phase:** `GD16`.

#### 33. Audio Engine (`frontend/src/audio` + `modules/audio_config`)
- **Responsibility:** Phát nhạc nền (BGM), hiệu ứng âm thanh (SFX: kiếm khí, thiên lôi, đột phá, cảnh báo boss) và giọng đọc TTS tùy chọn với kiểm soát âm lượng độc lập từng kênh và tắt tiếng nhanh.
- **Inputs:** `AudioTrigger` từ Backend/Notification Engine, audio assets đã kiểm chuẩn license từ Asset Registry.
- **Outputs:** Luồng âm thanh trên Broadcast Output (để OBS capture) với mức âm lượng cân bằng.
- **Dependencies:** Asset Registry, Configuration Manager.
- **Public interfaces:** `playSfx(assetId, volume)`, `setBgm(assetId)`, `setChannelVolume(channel, level)`, `muteAll(bool)`.
- **Data ownership:** Cấu hình âm lượng trong `application_settings`.
- **Failure handling:** Xử lý chính sách browser autoplay một cách rõ ràng; lỗi giải mã file audio bỏ qua gọn không chặn render loop.
- **Security boundaries:** Chỉ phát audio asset đã đăng ký trong Asset Registry có khai báo `license` hợp lệ cho livestream.
- **Testing strategy:** Kiểm tra giới hạn đồng thời SFX (chống rè/clipping khi 20 người dùng skill), test mute/volume persistence.
- **Development phase:** `GD16` (audio hooks), `GD18` (OBS audio routing check).

#### 34. Live Studio (`modules/live_studio`)
- **Responsibility:** Điều phối bảng trạng thái phát sóng trực tiếp (Live Readiness Checklist: active plugin, DB health, asset readiness, connector status, renderer connected, safe area preset, FPS/queue telemetry) trước và trong khi lên sóng.
- **Inputs:** Trạng thái tổng hợp từ Session, Asset Registry, Connector, 3D Runtime, OBS Integration.
- **Outputs:** Live readiness report, broadcast viewport URL/settings, live health warnings.
- **Dependencies:** Game Session Manager, Asset Registry, OBS Integration, Analytics, TikTok Connector.
- **Public interfaces:** `get_readiness_check()`, `get_broadcast_url()`, `get_live_status()`.
- **Data ownership:** Cấu hình preset phát sóng trong `application_settings`.
- **Failure handling:** Cảnh báo đỏ rõ ràng nếu thiếu thành phần bắt buộc (ví dụ chạy Simulator thay vì Live Connector) và **cấm đánh dấu `PRODUCTION_READY`** khi đang bật `DEVELOPMENT` mode hoặc sử dụng placeholder asset chưa được phê duyệt (`ADR-016`).
- **Security boundaries:** URL broadcast chỉ phục vụ trên `127.0.0.1`, tuyệt đối **không chứa `ADMIN_SESSION_TOKEN`** và không chứa nút hay API điều khiển quản trị (`ADR-017`).
- **Testing strategy:** Integration test readiness checklist với từng thành phần online/offline.
- **Development phase:** `GD18`.

#### 35. OBS Integration (`modules/obs_integration`)
- **Responsibility:** Hỗ trợ tích hợp mượt với OBS Studio / TikTok LIVE Studio thông qua cung cấp Broadcast Output `1080×1920` chuẩn (Browser Source loopback hoặc cửa sổ sạch) và tùy chọn kết nối OBS WebSocket cục bộ (nếu người dùng cấu hình) để đồng bộ trạng thái stream/scene.
- **Inputs:** Cấu hình OBS cục bộ (tùy chọn), độ phân giải output `1080×1920`, khung Safe Area.
- **Outputs:** Trạng thái kết nối OBS (tùy chọn), hướng dẫn/preset Browser Source, cảnh báo khung hình.
- **Dependencies:** Configuration Manager, Live Studio.
- **Public interfaces:** `get_browser_source_config()`, `test_obs_connection()`, `get_obs_status()`.
- **Data ownership:** Cấu hình kết nối OBS cục bộ (password mã hóa/ẩn qua `SecretStr`).
- **Failure handling:** OBS WebSocket hoàn toàn tùy chọn — nếu OBS không mở hoặc không bật WebSocket, Broadcast URL vẫn hoạt động bình thường không ảnh hưởng game.
- **Security boundaries:** Chỉ kết nối OBS WebSocket cục bộ (`127.0.0.1`); không lưu mật khẩu OBS dạng plaintext trong logs/exports.
- **Testing strategy:** Test tạo cấu hình 1080×1920, test graceful fallback khi OBS không khả dụng, test benchmark capture thực tế ở GD19.
- **Development phase:** `GD18`.

#### 36. Analytics (`modules/analytics`)
- **Responsibility:** Thu thập, tổng hợp chỉ số vận hành cục bộ theo phiên (tổng người chơi hoạt động, lệnh/phút, phân bố lệnh lỗi, độ trễ xử lý sự kiện p50/p95, độ sâu hàng đợi, FPS/VRAM từ Renderer, số lần thắng/thua boss, tỷ lệ độ kiếp) phục vụ màn hình Analytics và báo cáo benchmark.
- **Inputs:** Metrics từ Event Gateway/Bus, Session Manager, Reward Ledger, 3D Runtime telemetry.
- **Outputs:** Snapshot chỉ số thời gian thực, báo cáo tổng kết phiên (JSON/CSV cục bộ).
- **Dependencies:** Database Manager, Logging System.
- **Public interfaces:** `record_metric(name, value, tags)`, `get_session_summary(session_id)`, `export_benchmark_report(session_id)`.
- **Data ownership:** Tổng hợp đọc từ `game_sessions`, `event_ingestions`, `reward_ledger` và bảng telemetry nhẹ theo phiên.
- **Failure handling:** Lỗi ghi metric không bao giờ làm gián đoạn vòng lặp gameplay; tự áp dụng ring buffer trong bộ nhớ.
- **Security boundaries:** Xuất báo cáo chỉ chứa số liệu tổng hợp/ẩn danh, không rò rỉ dữ liệu cá nhân nhạy cảm hay secret.
- **Testing strategy:** Unit test tính p50/p95 chính xác, kiểm tra xuất báo cáo benchmark 1/20/50/100 nhân vật (AC15).
- **Development phase:** `GD18` (dashboard analytics), `GD19` (benchmark exporter).

#### 37. TikTok Connector (`modules/tiktok_connector`)
- **Responsibility:** Lớp adapter trừu tượng kết nối tới **nhà cung cấp sự kiện TikTok LIVE được cấp quyền (Authorized Provider)**, dịch sự kiện nguồn sang định dạng đầu vào của Event Gateway, giám sát heartbeat, tự động reconnect và kích hoạt grace period `15s` khi mất kết nối.
- **Inputs:** Cấu hình kết nối được cấp quyền, luồng sự kiện từ Authorized Provider.
- **Outputs:** Raw events có gắn `source` và `source_event_id` (nếu có) gửi Event Gateway; trạng thái kết nối (`DISCONNECTED`, `CONNECTING`, `CONNECTED`, `DEGRADED`, `ERROR`).
- **Dependencies:** Event Gateway, Configuration Manager, Game Session Manager, Logging System.
- **Public interfaces:** `ConnectorAdapter.connect()`, `disconnect()`, `get_capabilities()`, `get_status()`.
- **Data ownership:** Không lưu credential vào DB plaintext; trạng thái phiên kết nối trong bộ nhớ.
- **Failure handling:** Mất kết nối → bắt đầu grace period `15s` → quá hạn yêu cầu Session Manager tạm dừng simulation & thưởng cho đến khi reconnect thành công (AC12).
- **Security boundaries:** **Gate bắt buộc GD17.** Tuyệt đối không tích hợp thư viện/phương pháp scraping trái phép hay thu thập cookie/session không được cấp quyền; công bố rõ bảng capabilities thực tế mà provider hỗ trợ (`TIKTOK_INTEGRATION_FEASIBILITY.md`).
- **Testing strategy:** Contract test với Mock Adapter ở GD04; chỉ chạy Authorized Live Smoke Test (AC18) tại GD17 sau khi xác minh quyền truy cập.
- **Development phase:** `GD04` (interface & Mock Provider), `GD17` (Authorized Provider integration gate).
