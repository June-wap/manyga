# LiveGame Studio

**LiveGame Studio** là nền tảng **Windows Desktop (Local-first)** vận hành nhiều mini game tương tác trực tiếp trên **TikTok LIVE** thông qua kiến trúc **Modular Monolith** kết hợp **Game Plugin Architecture**.

> **Trạng thái hiện tại:** `GD00 – Project Design & Initialization` (branch `design/gd00`). Chưa triển khai source code runtime (bắt đầu từ `GD01`).

---

## 1. Mục tiêu & Danh mục Mini Game

Platform cung cấp lõi vận hành chung (Event Pipeline, Player Persistence, Game Session, Asset Library, Camera Director, Overlay Engine, 3D/2D Runtime, Game Master Panel, OBS Broadcast Output 9:16) để phát triển và mở rộng nhiều mini game độc lập:

| Game ID | Plugin ID | Tên mini game | Engine | Trạng thái |
|---|---|---|---|---|
| **GAME001** | `cultivation_online` | **Tu Tiên Online** (Vertical Slice kiểm chứng Platform) | Three.js (3D) | GDD v0.1.0 đã kiểm tra; thiết kế hoàn tất |
| GAME002 | `bar_online` | Bar Online | Three.js / Phaser.js | Planned |
| GAME003 | `temple_online` | Chùa Online | Three.js | Planned |
| GAME004 | `duck_race` | Đua Vịt | Three.js / Phaser.js | Planned |
| GAME005 | `tug_of_war` | Đại Chiến Kéo Co | Three.js / Phaser.js | Planned |
| GAME006 | `prison_online` | Nhà Tù Online | Three.js | Planned |
| GAME007 | `classroom_online` | Lớp Học Online | Three.js | Planned |

---

## 2. Công nghệ cốt lõi (Locked Tech Stack)

- **Kiến trúc:** Modular Monolith, Windows Desktop, Local-first (loopback `127.0.0.1` mặc định).
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLite (WAL mode), SQLAlchemy 2.x, Alembic, REST API + WebSocket.
- **Desktop UI:** PySide6 (Dark theme, Purple accent, Game Master Panel tách biệt hoàn toàn với Broadcast Output).
- **Frontend Renderer:** TypeScript + Vite + Three.js (3D, 9:16 `1080×1920`), Phaser.js (dự phòng 2D).
- **Asset Pipeline:** Sản xuất bên ngoài theo Asset Contract (GLB/glTF 2.0). Không tích hợp Meshy, Tripo, AI Asset Generator hay Blender runtime.

---

## 3. Cấu trúc thư mục dự án

```text
D:\Tiktok Mini Game\
├── apps/                       # Entry points ứng dụng (backend server, PySide6 desktop shell) — từ GD01
├── core/                       # Application Core, Config, Logging, DB engine, Base contracts — từ GD01
├── modules/                    # Các module dùng chung của Platform (Event, Player, Asset, Camera, ...) — từ GD02+
├── games/                      # Built-in Game Plugins (games/cultivation_online/ cho GAME001) — từ GD05+
├── frontend/                   # TypeScript + Vite + Three.js Broadcast Renderer (1080x1920) — từ GD01/GD08
├── assets/                     # Asset registry local & placeholder assets đã kiểm chuẩn — từ GD07
├── asset_production/           # Prompts, specs, validation checklists sản xuất asset ngoài (TT-AS)
├── docs/                       # Toàn bộ tài liệu đặc tả, kiến trúc, hợp đồng và báo cáo
│   ├── platform/               # TDD, Module Design, DB Design, Contracts, UI, Testing, TikTok Feasibility
│   └── games/cultivation_online/ # GDD requirements mapping và tài liệu riêng GAME001
├── scripts/                    # Công cụ dev/bootstrap/migration/benchmark cục bộ
├── tests/                      # Unit, integration, contract, UI, replay & benchmark tests
├── AGENTS.md                   # Quy tắc phối hợp giữa Codex và Antigravity
├── GDD_Tu_Tien_Online_v0.1.md  # GDD gốc v0.1.0 của Tu Tiên Online (không tự ý ghi đè)
└── README.md                   # Tài liệu này
```

---

## 4. Chỉ mục tài liệu (Documentation Index)

### Quản trị & Tổng quan
- [AGENTS.md](AGENTS.md) — Quy tắc làm việc giữa Codex và Antigravity.
- [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) — Đặc tả sản phẩm Platform & phạm vi Vertical Slice GAME001.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Kiến trúc tổng thể, ranh giới module, luồng sự kiện và Shared World.
- [docs/ROADMAP.md](docs/ROADMAP.md) — Lộ trình 21 giai đoạn (`GD00`–`GD20`), mapping `TT-GD01..08` và Asset Roadmap `TT-AS`.
- [docs/DECISIONS.md](docs/DECISIONS.md) — Nhật ký quyết định kiến trúc (ADRs).
- [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) — Trạng thái dự án, rủi ro và điểm chờ duyệt.
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — Lịch sử thay đổi.

### Thiết kế Platform (`docs/platform/`)
- [docs/platform/TDD.md](docs/platform/TDD.md) — Technical Design Document (Runtime, Shared World, Concurrency, Recovery).
- [docs/platform/MODULE_DESIGN.md](docs/platform/MODULE_DESIGN.md) — Thiết kế chi tiết 37 module Platform.
- [docs/platform/DATABASE_DESIGN.md](docs/platform/DATABASE_DESIGN.md) — Thiết kế CSDL Platform + GAME001, ERD, Migration & Isolation.
- [docs/platform/GAME_PLUGIN_CONTRACT.md](docs/platform/GAME_PLUGIN_CONTRACT.md) — Hợp đồng Game Plugin (Manifest, Lifecycle, State, Intents).
- [docs/platform/ASSET_CONTRACT.md](docs/platform/ASSET_CONTRACT.md) — Hợp đồng Universal Asset (GLB/glTF 2.0, Manifest, Hash, Validation).
- [docs/platform/API_CONTRACT.md](docs/platform/API_CONTRACT.md) — Đặc tả REST API và WebSocket Snapshot/Delta Protocol.
- [docs/platform/EVENT_CONTRACT.md](docs/platform/EVENT_CONTRACT.md) — Hợp đồng sự kiện Livestream, Deduplication, Backpressure & Replay.
- [docs/platform/UI_GUIDELINES.md](docs/platform/UI_GUIDELINES.md) — Hướng dẫn UI/UX Desktop (Dark/Purple), GAME001 Panel & Output 9:16.
- [docs/platform/TESTING_POLICY.md](docs/platform/TESTING_POLICY.md) — Chính sách kiểm thử, phân loại trạng thái và tiêu chuẩn nghiệm thu.
- [docs/platform/TIKTOK_INTEGRATION_FEASIBILITY.md](docs/platform/TIKTOK_INTEGRATION_FEASIBILITY.md) — Nghiên cứu khả thi tích hợp TikTok được cấp quyền.

### GAME001 & Báo cáo GD00
- [GDD_Tu_Tien_Online_v0.1.md](GDD_Tu_Tien_Online_v0.1.md) — Game Design Document gốc (v0.1.0).
- [docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md](docs/games/cultivation_online/GDD_REQUIREMENTS_MAPPING.md) — Đối chiếu yêu cầu GDD vào Platform & các điểm xung đột/chưa xác minh.
- [docs/GD00_ENVIRONMENT_REPORT.md](docs/GD00_ENVIRONMENT_REPORT.md) — Báo cáo kiểm tra môi trường thực tế trên máy Windows.
- [docs/GD00_DELIVERY_REPORT.md](docs/GD00_DELIVERY_REPORT.md) — Báo cáo bàn giao GD00 và đánh giá Acceptance Criteria.
