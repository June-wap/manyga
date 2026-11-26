# GAME PLUGIN CONTRACT — LIVEGAME STUDIO

**Contract Version:** `1.0.0`  
**Áp dụng cho:** `GAME001` (`cultivation_online`) và toàn bộ mini game mở rộng (`GAME002`–`GAME100+`).  
**Ràng buộc bảo mật:** Giai đoạn đầu chỉ hỗ trợ **trusted built-in plugins** nằm trong allowlist `games/<plugin_id>/` (`ADR-010`).

---

## 1. Mục tiêu của Contract

1. Cho phép Platform đăng ký, nạp, chạy, tạm dừng và dừng bất kỳ mini game nào mà **không chứa code nghiệp vụ riêng của GAME001 trong `core/` hoặc `modules/`**.
2. Cho phép thêm `GAME002` (Bar Online), `GAME003` (Chùa Online), `GAME004` (Đua Vịt), `GAME005` (Đại Chiến Kéo Co), `GAME006` (Nhà Tù Online), `GAME007` (Lớp Học Online)... mà **không phải sửa bất kỳ dòng code nào của `games/cultivation_online/`**.
3. Chuẩn hóa giao tiếp giữa Plugin và Platform Services (Database UoW, Event Bus, Command Parser, Player Manager, Asset Registry, Reward Ledger, Camera Director, Overlay Engine, Event Scheduler).

---

## 2. Plugin Manifest (`games/<plugin_id>/manifest.json`)

Mỗi mini game bắt buộc có tệp `manifest.json` hợp lệ theo Pydantic schema:

```json
{
  "schema_version": "1.0.0",
  "game_code": "GAME001",
  "plugin_id": "cultivation_online",
  "name": "Tu Tiên Online",
  "version": "0.1.0",
  "engine_type": "threejs",
  "platform_compatibility": ">=1.0.0,<2.0.0",
  "contract_version": "1.0.0",
  "entrypoint": "games.cultivation_online.plugin:CultivationOnlinePlugin",
  "trusted_builtin": true,
  "broadcast_aspect_ratio": "9:16",
  "target_resolution": { "width": 1080, "height": 1920 },
  "capabilities": {
    "supports_persistence": true,
    "supports_world_events": true,
    "supports_personal_events": true,
    "supports_pip_camera": true,
    "supports_cosmetic_gifts": true
  },
  "config_schema_version": "0.1.0",
  "db_table_prefix": "g_cultivation_",
  "required_assets": [
    { "asset_id": "TT_MAP001", "version_constraint": ">=0.1.0", "required": true },
    { "asset_id": "TT_CHAR001", "version_constraint": ">=0.1.0", "required": true },
    { "asset_id": "TT_CHAR002", "version_constraint": ">=0.1.0", "required": true },
    { "asset_id": "TT_BOSS001", "version_constraint": ">=0.1.0", "required": true }
  ],
  "commands_spec_file": "commands.json",
  "default_config_file": "default_config.json"
}
```

### Quy tắc kiểm tra tương thích (Plugin Compatibility)
- `Game Registry` kiểm tra `contract_version` khớp major version hiện tại (`1.x`) và `platform_compatibility` thỏa mãn version của LiveGame Studio.
- Kiểm tra `plugin_id` (`^[a-z][a-z0-9_]{2,40}$`), `game_code` duy nhất (`^GAME[0-9]{3,}$`), `db_table_prefix` không trùng với plugin khác và không xâm phạm bảng Platform.
- `entrypoint` phải bắt đầu bằng `games.<plugin_id>.` (chặn nạp module tùy ý bên ngoài `games/`).

---

## 3. Giao diện Python bắt buộc (`core/contracts/game_plugin.py`)

```python
class GamePlugin(Protocol):
    @property
    def plugin_id(self) -> str: ...
    @property
    def manifest(self) -> PluginManifest: ...

    # 1. Lifecycle
    def on_load(self, services: PlatformServices) -> None: ...
    def on_session_start(self, ctx: SessionContext) -> PluginInitResult: ...
    def on_tick(self, ctx: TickContext) -> PluginTickOutput: ...
    def on_pause(self, ctx: SessionContext, reason: str) -> None: ...
    def on_resume(self, ctx: SessionContext) -> None: ...
    def on_session_stop(self, ctx: SessionContext, reason: str) -> None: ...
    def on_unload(self) -> None: ...

    # 2. Event & Command Handling
    def get_command_specs(self) -> list[CommandSpec]: ...
    def handle_command(self, ctx: CommandContext) -> CommandOutcome: ...
    def handle_cosmetic_gift(self, ctx: GiftContext) -> list[CosmeticEffectIntent]: ...
    def handle_scheduled_event(self, ctx: ScheduledEventContext) -> EventTransitionResult: ...
    def handle_gm_action(self, ctx: GameMasterActionContext) -> GameMasterActionResult: ...

    # 3. State, Snapshot & Persistence
    def build_render_snapshot(self, ctx: SessionContext) -> RenderSnapshotPayload: ...
    def get_player_public_state(self, profile_id: str) -> dict[str, Any]: ...
    def save_checkpoint(self, uow: UnitOfWork, ctx: SessionContext) -> CheckpointStats: ...
    def recover_after_crash(self, uow: UnitOfWork, session_id: str) -> RecoveryReport: ...

    # 4. Configuration & Assets
    def validate_config(self, raw_config: dict[str, Any]) -> ValidatedConfig: ...
    def get_asset_dependencies(self) -> list[AssetDependencySpec]: ...
```

---

## 4. Đặc tả từng miền trách nhiệm trong Contract

### 4.1 Vòng đời (Lifecycle)
```text
DISCOVERED → REGISTERED → LOADED → SESSION_STARTING → RUNNING ⇄ PAUSED → STOPPING → STOPPED → UNLOADED
                                                            ↘ PAUSED_ERROR (khi vượt ngưỡng lỗi)
```
- `on_load`: Đăng ký command specs, config schema, không mở DB transaction hay tạo background thread tự phát.
- `on_session_start`: Kiểm tra `recover_after_crash` nếu phiên trước bị gián đoạn, nạp config snapshot bất biến cho phiên, dựng state runtime và trả về `RenderSnapshotPayload` ban đầu.
- `on_tick(ctx)`: Chỉ dùng `ctx.sim_now_ms` và `ctx.delta_sim_ms` từ `SimulationClock` (cấm tự gọi `time.time()` hoặc `datetime.now()` cho logic game).
- `on_pause`: Đóng băng toàn bộ bộ đếm logic game; không tăng XP hay hạ HP.
- `on_session_stop`: Hủy an toàn các event chưa hoàn tất theo chính sách refund, trả toàn bộ `xp_reserved`, xả checkpoint cuối cùng.

### 4.2 Game State & Player State
- Plugin phải tách rõ:
  - **Persistent Domain State:** Lưu qua SQLite repositories mang tiền tố `g_<plugin_id>_*` và `PlatformServices.player_manager` / `reward_ledger`.
  - **Ephemeral Simulation State:** Hàng chờ tạm, animation hints, hiệu ứng đang chạy, delta queue chờ phát sang Renderer.
- Mọi thay đổi tài nguyên/thưởng bắt buộc gọi `PlatformServices.reward_ledger.grant_idempotent(uow, ...)` trong cùng `UnitOfWork`.

### 4.3 Event Handling & Game Configuration
- `handle_command(ctx)` nhận `ParsedCommand` đã được Platform chuẩn hóa, dedupe và kiểm tra cooldown cơ bản (hỗ trợ cả lệnh đơn và subcommand/argument tường minh như `!hotheauto`, `!hotheauto on`, `!hotheauto off`). Mọi lệnh được gắn `ctx.player_id` của chính người gửi (không thể điều khiển người khác) và đánh giá hoàn toàn theo **server-side event timing (`SimulationClock`)**, không yêu cầu người xem phản ứng khớp thời gian animation trên livestream.
- `handle_cosmetic_gift(ctx)` **chỉ được trả về `list[CosmeticEffectIntent]`** (hiệu ứng thị giác/âm thanh); không được cấp `UnitOfWork` ghi tiến trình để thực thi cứng chính sách chống pay-to-win (`ADR-009`).
- Cấu hình cân bằng có `config_schema_version`; thay đổi cấu hình trong lúc đang chạy chỉ có hiệu lực ở **event mới hoặc phiên mới**, không sửa nóng giữa trận đang `ACTIVE`.

### 4.4 Scheduled Events, Camera Requests & Overlay Requests
Plugin không gọi trực tiếp Three.js hay tự tạo thread timer; thay vào đó trả về các **Intent Objects** chuẩn hóa trong `PluginTickOutput` / `CommandOutcome`:
- **`ScheduledEventRequest`**: Yêu cầu `Event Scheduler` / `Event Director` lên lịch hoặc đăng ký xung đột (ví dụ Boss 5 phút đầu / mỗi 10 phút).
- **`CameraIntent`**: `{ "camera_id": "CAM04", "target_entity_id": "boss_01", "priority": 90, "min_hold_ms": 5000, "duration_ms": 120000, "pip_camera_id": "CAM03" | null }`.
- **`OverlayIntent`**: `{ "kind": "player_card" | "toast" | "boss_hud" | "tribulation_hud" | "leaderboard", "dedupe_key": "...", "ttl_ms": 60000, "display_ms": 3000, "payload": { ... } }`.
- **`VfxAudioIntent`**: `{ "effect_asset_id": "...", "audio_asset_id": "...", "anchor_id": "...", "tier": "major" | "minor", "ttl_ms": 15000 }`.

### 4.5 Save, Restore & Error Handling
- **Save/Restore:** Platform gọi `save_checkpoint(uow, ctx)` định kỳ mỗi `10s` và ngay trước `on_pause` / `on_session_stop`. Khi khởi động lại sau crash, Platform gọi `recover_after_crash(uow, session_id)` trước khi cho phép mở phiên mới.
- **Error Handling:**
  - Lỗi nghiệp vụ hợp lệ (thiếu XP, hết slot boss, chưa đến giờ đăng ký) trả về `CommandOutcome(accepted=False, reason_code="INSUFFICIENT_XP", message_vi="...")` — **không ném unhandled exception**.
  - Unhandled exception từ plugin bị `Game Plugin Manager` bắt lại, ghi structured log + correlation ID, tăng bộ đếm lỗi; nếu xảy ra liên tiếp (mặc định ≥ 5 lỗi trong 10 giây) → kích hoạt circuit breaker chuyển phiên sang `PAUSED_ERROR` và thông báo trên Game Master Panel.
