# UNIVERSAL ASSET CONTRACT — LIVEGAME STUDIO

**Contract Version:** `1.0.0`  
**Ràng buộc cốt lõi:** Asset được sản xuất bên ngoài bằng các prompt/quy trình riêng (`TT-AS`). Platform **chỉ nhập, kiểm định, quản lý phiên bản và sử dụng** — tuyệt đối không tích hợp Meshy, Tripo, AI Asset Generator hay Blender runtime (`ADR-004`).

---

## 1. Các loại Asset được hỗ trợ (9 Asset Types)

| `asset_type` | Định dạng chuẩn | Mục đích | Ví dụ GAME001 |
|---|---|---|---|
| `character` | `.glb` (glTF 2.0 binary) | Nhân vật có skeleton / LOD | `TT_CHAR001` (Nam), `TT_CHAR002` (Nữ), `TT_BOSS001` (Bạch Lang Vương) |
| `prop` | `.glb` | Vật thể môi trường, vũ khí | Cổng sơn môn, đại điện, đèn lồng, kiếm, bồ đoàn |
| `map` | `.glb` + `zones.json` | Bản đồ tách lớp (decor, collision, walkable, anchors) | `TT_MAP001` (Thanh Vân Tông) |
| `animation` | `.glb` (embedded hoặc clip-only) | Bộ chuyển động nhân vật/boss | `idle`, `walk`, `run`, `meditation`, `cast`, `sword_attack`, `hit`, `defeat`, `celebrate` |
| `material` | `.json` / embedded PBR | Định nghĩa vật liệu dùng chung | Đá sáng, mái ngói xanh ngọc, linh khí |
| `texture` | `.png` / `.webp` / `.ktx2` | Bản đồ bề mặt (512–1024 đám đông, 2K boss) | Albedo/ORM textures |
| `effect` | `.json` + `.glb`/`.png` | Hiệu ứng VFX (pooled) | Aura đột phá, kiếm khí, thiên lôi, hoa sen cosmetic |
| `audio` | `.ogg` / `.mp3` / `.wav` | BGM và SFX đã có quyền livestream | SFX kiếm khí, sấm sét, nhạc nền tiên hiệp |
| `ui` | `.svg` / `.png` / `.webp` | Biểu tượng, khung badge, icon nghề | Icon Kiếm Tu / Đan Tu / Thể Tu |

---

## 2. Quy chuẩn kỹ thuật 3D bắt buộc

1. **Định dạng:** **GLB / glTF 2.0** (tự đóng gói, cấm URI ngoài `http://`, `https://`, `file://` hoặc `../`).
2. **Đơn vị đo:** **Mét (Meter units, `1 unit = 1m`)**, chuẩn hóa tỷ lệ thực tế cho nhân vật Chibi và kiến trúc map.
3. **Hệ trục tọa độ Runtime:** **Y-up, Right-handed (`+Z` hướng mặt trước khi chuẩn hóa Three.js)**; mọi transform gốc phải được apply (`scale = [1,1,1]`).
4. **Pivot chuẩn:** Nhân vật và Prop đặt trên mặt đất có pivot tại **chân đế (`y = 0`)** ở tâm hình chiếu đáy.
5. **Tách cấu trúc Map (`map`):** Cấm xuất toàn bộ bản đồ thành một mesh gộp vô cấu trúc. Phải tách node/layer tối thiểu: `decor_*`, `collision_*`, `walkable_*` và danh sách anchor tọa độ trong `zones.json` (`spawn_gate`, `cultivation_court`, `boss_arena`, `tribulation_platform`, `sect_hall`, `paths`).
6. **Skeleton & Animation Compatibility:**
   - Nhân vật dùng chung humanoid rig phải khai báo `skeleton_profile` (ví dụ `humanoid_chibi_v1`) và danh sách xương chuẩn tối thiểu để tái sử dụng animation giữa `TT_CHAR001` và `TT_CHAR002`.
   - Mọi tên clip animation phải khớp chính xác bảng `animations` trong manifest.
   - Không khẳng định rig hoặc animation tương thích trước khi chạy kiểm định thực tế tại `GD07`/`GD09`.
7. **Ngân sách LOD mục tiêu (Subject to Benchmark):**
   - Nhân vật đám đông: `LOD0: 5,000–8,000 tris`, `LOD1: 2,000–3,000 tris`, `LOD2: 500–1,000 tris`.
   - Texture nhân vật đám đông: `512×512` đến `1024×1024`; Boss có thể tới `2048×2048` nếu benchmark VRAM cho phép.

---

## 3. Schema Asset Manifest (`asset_manifest.json`)

Mọi gói asset (kể cả Placeholder) bắt buộc có `asset_manifest.json` nằm ở thư mục gốc của gói:

```json
{
  "schema_version": "1.0.0",
  "asset_id": "TT_CHAR001",
  "version": "0.1.0",
  "asset_type": "character",
  "display_name": "Đệ Tử Nam — Thanh Vân Tông",
  "is_placeholder": true,
  "units": "meters",
  "up_axis": "Y",
  "pivot": "bottom_center",
  "entry_file": "model/tt_char001_lod0.glb",
  "skeleton_profile": "humanoid_chibi_v1",
  "animations": [
    "idle", "walk", "run", "meditation", "cast",
    "sword_attack", "hit", "defeat", "celebrate"
  ],
  "lods": [
    { "level": 0, "file": "model/tt_char001_lod0.glb", "max_distance_m": 12.0, "triangles": 6400 },
    { "level": 1, "file": "model/tt_char001_lod1.glb", "max_distance_m": 28.0, "triangles": 2400 },
    { "level": 2, "file": "model/tt_char001_lod2.glb", "max_distance_m": 80.0, "triangles": 820 }
  ],
  "dependencies": [
    { "asset_id": "TT_ANIM_CORE", "version_constraint": ">=0.1.0", "required": true }
  ],
  "files": [
    { "path": "model/tt_char001_lod0.glb", "sha256": "<64-hex>", "size_bytes": 123456 },
    { "path": "model/tt_char001_lod1.glb", "sha256": "<64-hex>", "size_bytes": 65432 },
    { "path": "model/tt_char001_lod2.glb", "sha256": "<64-hex>", "size_bytes": 23456 }
  ],
  "license": {
    "name": "CC0-1.0",
    "commercial_livestream_allowed": true,
    "attribution_required": false,
    "license_url_or_ref": "internal/licenses/cc0.txt"
  },
  "provenance": {
    "created_by": "external_artist_or_pipeline",
    "source_task_id": "TT-AS02",
    "created_at": "2026-11-26T00:00:00Z",
    "notes": "Placeholder or validated production export"
  }
}
```

### Quy ước Định danh & Phiên bản
- **Stable Asset ID:** `^[A-Z][A-Z0-9_]{3,48}$` (ví dụ `PL_PLACEHOLDER_CHAR`, `TT_CHAR001`, `TT_MAP001`, `TT_BOSS001`). Một khi đã phát hành, không đổi nghĩa `asset_id`.
- **Semantic Version:** `MAJOR.MINOR.PATCH` (`0.1.0` cho placeholder/pre-release, `1.0.0` cho production asset đã kiểm định). Mỗi cặp `(asset_id, version)` là **bất biến (immutable)**.

---

## 4. Quy tắc Bảo mật Đường dẫn & Kiểm định (Asset Validator)

### 4.1 Path Safety (Chống Path Traversal)
Mọi đường dẫn tệp trong `entry_file`, `lods[].file`, `files[].path`:
- Bắt buộc là **relative POSIX path** (`/` phân tách).
- **Cấm tuyệt đối:** bắt đầu bằng `/`, `\`, ổ đĩa Windows (`C:`, `D:`), UNC (`\\server\`), chứa `..`, ký tự null `\x00`, hoặc symlink/junction trỏ ra ngoài thư mục gốc của gói.
- Khi giải đường dẫn cuối cùng: `resolved.resolve().is_relative_to(asset_root.resolve())` bắt buộc `True`.

### 4.2 Quy trình Validation & Schema Validation Report
`Asset Validator` chạy tuần tự các kiểm tra và xuất `ValidationReport` lưu vào `asset_versions.validation_report_json`:
1. **Schema Check:** Hợp lệ Pydantic schema của `asset_manifest.json`.
2. **File Safety Check:** Không có path traversal, không có tệp bị cấm (`.exe`, `.dll`, `.py`, `.ps1`, `.bat`, `.js`, `.html`).
3. **Integrity Check:** Tính lại `SHA-256` từng file trong `files[]` khớp 100% và mọi file trong gói đều được kê khai.
4. **Binary Header Check (GLB):** Kiểm tra magic bytes `0x46546C67` (`glTF`), version `== 2`, cấu trúc JSON chunk hợp lệ, không chứa external URI `http(s)://`.
5. **Metadata & License Check:** Xác nhận `units == "meters"`, `up_axis == "Y"`, `license.name` không rỗng, `license.commercial_livestream_allowed == true` (với production asset; placeholder nội bộ gắn `is_placeholder = true`).
6. **Rig / Animation / Zone Check:** Đối chiếu danh sách clip animation trong GLB khớp khai báo manifest (nếu có); đối chiếu `zones.json` với `map`.

```json
{
  "validator_version": "1.0.0",
  "checked_at": "2026-11-26T00:00:00Z",
  "passed": true,
  "errors": [],
  "warnings": [
    { "code": "PLACEHOLDER_ASSET", "message": "Asset đang ở chế độ placeholder, chưa phải bản production." }
  ],
  "stats": { "file_count": 3, "total_bytes": 212344, "glb_version": 2 }
}
```

---

## 5. Chính sách Tài nguyên theo Môi trường (`DEVELOPMENT` vs `PRODUCTION` — `HIGH-002`)

Platform áp dụng hai chế độ vận hành tài nguyên tách biệt, được cấu hình rõ trong `Configuration Manager` (`asset_policy_mode`) và kiểm tra tại `Asset Registry` + `Live Studio` readiness check:

| Quy tắc | Chế độ `DEVELOPMENT` | Chế độ `PRODUCTION` |
|---|---|---|
| **Placeholder Assets (`is_placeholder=true`)** | **Cho phép** các placeholder tương thích chuẩn manifest (`asset_manifest.json`) | **Không cho phép** tự động thay thế cho required assets; không được đánh dấu `production-ready` khi đang dùng placeholder chưa được phê duyệt tường minh |
| **Required Assets của Plugin** | Không yêu cầu production asset; cho phép kiểm thử plugin bằng asset thay thế tương thích | **Bắt buộc tồn tại 100%** mọi `required_assets` có `required: true` trong plugin manifest |
| **Kiểm định phiên bản & trạng thái** | Cho phép semver pre-release (`0.x.y`) có `validation_status = VALID` | Bắt buộc thỏa mãn `version_constraint`, `validation_status = VALID`, khớp SHA-256 và `license.commercial_livestream_allowed = true` |
| **Khi thiếu dependency** | Tự fallback sang placeholder tương ứng và hiển thị **cảnh báo nổi bật** (`PLACEHOLDER_ACTIVE`) trên Desktop UI & logs | **Cấm tự động bỏ qua dependency bị thiếu**; chặn chuyển trạng thái `PRODUCTION_READY` và trả `MissingAssetReport` chi tiết cho Host |
| **Giai đoạn áp dụng chính** | `GD01`–`GD18` (phát triển & kiểm thử, không để production asset chặn tiến độ code) | `GD18`–`GD20` & vận hành livestream thực tế |

### Quy tắc áp dụng Placeholder trong `DEVELOPMENT`
- Giai đoạn nền tảng (`GD01`–`GD16`) **không phụ thuộc production asset** (`TT-AS01`..`TT-AS09`).
- Bộ **Placeholder Assets** (tối giản nhưng tuân thủ đầy đủ `asset_manifest.json`, đơn vị mét, Y-up, đủ zone anchors) luôn mang `is_placeholder: true`.
- Khi nâng cấp lên production asset đã kiểm định (`version: 1.0.0`, `is_placeholder: false`), Game Plugin và 3D Runtime **không phải sửa code** — chỉ chuyển active version trong `Asset Registry`.
- Trong cả hai chế độ, `Live Studio` readiness checklist bắt buộc hiển thị rõ trạng thái `ASSET_MODE: DEVELOPMENT (PLACEHOLDER)` hoặc `ASSET_MODE: PRODUCTION (VERIFIED)` để Host không bao giờ nhầm lẫn (AC14).
