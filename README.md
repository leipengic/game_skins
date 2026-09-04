# game_skins

> 英雄皮肤 / 壁纸批量下载工具集（monorepo）。王者荣耀 · 英雄联盟 · 守望先锋（规划中）。

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://img.shields.io/badge/CI-flake8%20%2B%20pytest-yellow)

## 仓库说明

本仓库合并自：

| 老仓库 | 状态 |
|---|---|
| [`leipengic/KPL_skin`](https://github.com/leipengic/KPL_skin) | 王者荣耀皮肤 · 已归档 |
| [`leipengic/LOL_skin`](https://github.com/leipengic/LOL_skin) | 英雄联盟皮肤 · 已归档 |

原仓库已停止维护，新功能与 bug fix 仅在 `game_skins` 处理。

## 子包

| 子包 | 状态 | 数据源 |
|---|---|---|
| `kpl/wangzhe_skin.py` | ✅ 可用 | `pvp.qq.com` + `game.gtimg.cn` 皮肤图床 |
| `lol/lol_skin.py` | ✅ 可用 | `lol.qq.com` + `game.gtimg.cn` + 旧版回退 |
| `overwatch/ow_wallpaper.py` | 🚧 规划 | 见 [`overwatch/README.md`](overwatch/README.md) |

## 安装

```bash
git clone https://github.com/leipengic/game_skins.git
cd game_skins
pip install -r requirements.txt
pip install -r requirements-dev.txt   # 可选：含 pytest/flake8
```

## 使用

每个子包既可作为模块运行，也可作为脚本运行（保持与老仓的兼容性）。

```bash
# 王者荣耀
python -m kpl.wangzhe_skin
python kpl/wangzhe_skin.py -o D:/wzry_skins -t 15 -r 5

# 英雄联盟
python -m lol.lol_skin
python lol/lol_skin.py --hero-filter "安妮" --include-chromas

# 代理（可选，三种用法见下节）
python lol/lol_skin.py --use-proxy --proxy http://127.0.0.1:7890
python lol/lol_skin.py --use-proxy --brd-uri "brd://C123:residential:PWD;country=cn"
BRD_PASSWORD=xxx python lol/lol_skin.py --use-proxy --brd-customer C123 --brd-zone residential
```

## 代理接入（Bright Data）

支持三种代理用法，详见 [`_common/bright_data.py`](_common/bright_data.py)：

1. **普通 HTTP 代理**：`--proxy http://ip:port`
2. **BRD URI 简写**：`--brd-uri "brd://customer:zone:password;country=cn;session=xxx"`
3. **BRD 字段（密码走环境变量）**：配合 `BRD_PASSWORD` 环境变量

控制面板：<https://www.bright.cn/cp/start>

## 目录结构

```
game_skins/
├── _common/             # 共享工具层（HTTP 下载、UA、文件名清理、CLI 参数、代理封装）
│   ├── headers.py       # random_ua() — fake_useragent 不可用时回退 Chrome UA
│   ├── paths.py         # sanitize_filename() — 跨平台文件名清理
│   ├── downloader.py    # request_with_retry() / download_image() / parse_proxy_list()
│   ├── cli.py           # add_common_download_args() / add_proxy_args() / add_brd_args()
│   └── bright_data.py   # Bright Data 代理封装：build / parse / normalize
├── kpl/                 # 王者荣耀子包
│   └── wangzhe_skin.py
├── lol/                 # 英雄联盟子包
│   └── lol_skin.py
├── overwatch/           # 守望先锋（规划）
│   └── README.md        # 数据源选型说明
├── tests/               # pytest 单元测试
├── .github/workflows/    # CI
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## 从老仓迁移

老仓的脚本调用方式保持兼容：

| 老仓 | 命令 | 新仓命令 |
|---|---|---|
| `KPL_skin` | `python WangzheSkin.py` | `python kpl/wangzhe_skin.py` 或 `python -m kpl.wangzhe_skin` |
| `LOL_skin` | `python lol_skin.py` | `python lol/lol_skin.py` 或 `python -m lol.lol_skin` |

CLI 参数：

| 老仓参数 | 新仓参数 |
|---|---|
| KPL `-o / -t / -r / --sleep-min / --sleep-max` | `-o / -t / -r / --delay` |
| LOL `-o / --delay / --hero-filter / --include-chromas` | `-o / --delay / --hero-filter / --include-chromas` |
| LOL `--use-proxy --proxy ...` | `--use-proxy --proxy ...` / `--brd-*` |

完整迁移对照见 [`CHANGELOG.md`](CHANGELOG.md)。

## 开发

```bash
# 运行测试
pytest tests/ -v

# 代码风格
flake8 _common kpl lol tests
```

## 版权

- 王者荣耀图片版权归腾讯所有
- 英雄联盟图片版权归 Riot Games / 腾讯所有
- 守望先锋图片版权归 Blizzard Entertainment 所有
- 工具代码采用 [MIT License](LICENSE)

> ⚠️ 本仓库仅供学习交流，请勿用于商业用途。所有下载的图片版权归原游戏厂商所有。