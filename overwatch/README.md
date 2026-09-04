# overwatch

占位目录。

守望先锋（OW / OW2）的壁纸/皮肤批量下载脚本**尚未实现**，等你确认数据源后开工。

## 可走的几条路径

| 路径 | 数据源 | 难度 | 风险 |
|---|---|---|---|
| 官方英雄画廊 HTML | `overwatch.blizzard.com/heroes/` | 中 | OW2 上线后页面结构已变，需先抓包确认选择器；暴雪 CDN 反爬敏感 |
| 官方 CDN 直链字典 | `blzmedia.blizzard.com/.../heroes/screenshots/*.jpg` | 低 | 路径需手维护（暴雪不定期换）；批量抓取可能触发封 IP |
| 社区聚合站 | owcdn / heroesprofile 等 | 低 | 几乎都禁止爬虫（违反 ToS），不建议 |

## 建议起步

**先做 OW2 英雄头像 + 技能图标**（体量小、URL 规整、争议低），跑通后再做高清皮肤/壁纸分两步走。

实现时会复用本仓 `_common/`：
- `request_with_retry` —— HTTP GET + 指数退避
- `download_image` —— 写盘 + 404 终止探测
- `add_common_download_args` + `add_proxy_args` —— CLI 标准化
- `sanitize_filename` —— 文件名清理

数据源确认后，把入口脚本（例如 `ow_wallpaper.py`）放到本目录即可。