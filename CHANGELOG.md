# Changelog

## [Unreleased] — 2026-09-04 — monorepo 初始化 + Bright Data 集成

合并自：
- `leipengic/KPL_skin` (commit `2b636e7` 2026-09-01)
- `leipengic/LOL_skin` (commit `1d96062` 2026-09-01)

### Added
- 新仓库结构：`game_skins/` monorepo
- `_common/` 共享层：`headers.py` / `paths.py` / `downloader.py` / `cli.py` / `bright_data.py`
- `kpl/` 子包：`wangzhe_skin.py`（从 `KPL_skin.WangzheSkin` 改造）
- `lol/` 子包：`lol_skin.py`（从 `LOL_skin.lol_skin` 改造）
- `overwatch/` 子包占位 + 选型说明 README
- **Bright Data 代理集成**（`_common/bright_data.py` + CLI 接入）：
  - `build_bright_data_proxy()` 直接构造代理字典
  - `parse_bright_data_uri()` 解析 `brd://customer:zone:password[;k=v;...]` URI
  - `normalize_proxy()` 统一处理 BRD URI 与普通 HTTP/SOCKS URL
  - CLI 新增 `--brd-uri / --brd-customer / --brd-zone / --brd-password / --brd-country / --brd-session`
  - 密码走环境变量（`BRD_CUSTOMER` / `BRD_ZONE` / `BRD_PASSWORD` 等），避免进入 history
- GitHub Actions：lint + pytest（Python 3.10/3.11/3.12）
- Dependabot：pip + github-actions 周更
- **29 个单元测试**覆盖 `_common/` 关键路径（`pytest tests/` 全绿）

### Changed
- `random_ua()`：fake_useragent 优先 + Chrome UA 回退（之前 KPL/LOL 各自为政）
- `sanitize_filename()`：覆盖 Windows + *nix + 控制字符 + 首尾 `.`/` ` trim
- `download_image()`：合并 KPL 的"404 提前终止"与 LOL 的"完整下载"两种语义，通过 `stop_on_404` 开关切换
- CLI 参数对齐：`-o/-t/-r/--delay` 统一，KPL 旧 `--sleep-min/--sleep-max` 行为内化为 `delay` 上下浮动
- KPL 启用代理支持（之前仅 LOL 启用）

### Preserved
- KPL 数据源 URL：`pvp.qq.com/web201605/js/herolist.json` + `game.gtimg.cn` 皮肤图床
- LOL 数据源 URL：`lol.qq.com/biz/hero/champion.js` + `game.gtimg.cn/images/lol/act/img/js/hero/{id}.js` + 旧版回退
- MIT License
- 行为兼容：`python kpl/wangzhe_skin.py` 与 `python -m kpl.wangzhe_skin` 两种调用方式均可

### TODO（后续 PR）
- [ ] 守望先锋 `overwatch/ow_wallpaper.py` —— 数据源确认后开工
- [ ] `download_image` 的代理失败自动降级（先直连再代理）
- [ ] 黑名单域名白名单配置
- [ ] pre-commit hooks（black + isort + flake8）
- [ ] mypy 类型检查纳入 lint workflow
- [ ] KPL 老 `--sleep-min/--sleep-max` 作为 deprecated alias 短暂保留
- [ ] Bright Data 粘性会话的批量管理（当前 `--brd-session` 仅控制同一进程内粘性）