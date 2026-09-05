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

## 主要第三方库

两个子包共用 `_common/` 工具层，运行时仅依赖极少第三方库。

### 网络请求

| 库 | 在项目中做的事 | 为什么选它 |
|---|---|---|
| `requests` | `_common/downloader.py` 统一发请求：随机 UA、超时重试、退避、按流式写盘下载图片 | 皮肤下载是 IO 密集型串行任务，`requests` 的重试与代理支持（`proxies` 参数）最省事，也便于接入 Bright Data 代理 |
| `fake-useragent`（可选） | `_common/headers.py` 生成随机 User-Agent | 图床对固定 UA 有限频风险，随机 UA 能降低被拦概率；**库不可用时自动回退内置 Chrome UA**，因此不是硬依赖 |

### 标准库承担的部分

英雄列表解析走的是 `json`（`herolist.json`）+ `re`（LOL 页面内嵌 JSON 提取），没有引入 BeautifulSoup / lxml——数据源本身就是结构化 JSON，正则提取比 DOM 解析更轻。

> 说明：`requirements.txt` 中的 `beautifulsoup4`、`lxml` 为老仓历史遗留声明，当前代码未实际调用，后续版本清理。

### 开发依赖（`requirements-dev.txt`）

| 库 | 用途 |
|---|---|
| `pytest` / `pytest-cov` | 单元测试与覆盖率 |
| `flake8` | 静态检查（CI 中执行） |
| `mypy` | 类型检查（`_common` 等模块均带类型注解） |
| `black` / `isort` | 代码格式化与 import 排序 |

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

## 鸣谢（Acknowledgments）

感谢以下开源项目与工具（图标均取自官方站点 / CDN）：

<table>
  <tr>
    <td align="center" width="140">
      <a href="https://www.jetbrains.com/idea/">
        <img src="https://resources.jetbrains.com/storage/products/intellij-idea/img/meta/intellij-idea_logo_300x300.png" width="64" height="64" alt="IntelliJ IDEA" /><br />
        <sub><b>IntelliJ IDEA</b></sub>
      </a>
      <br />
      <sub>JetBrains 出品</sub>
    </td>
    <td align="center" width="140">
      <a href="https://www.jetbrains.com/pycharm/">
        <img src="https://resources.jetbrains.com/storage/products/pycharm/img/meta/pycharm_logo_300x300.png" width="64" height="64" alt="PyCharm" /><br />
        <sub><b>PyCharm</b></sub>
      </a>
      <br />
      <sub>JetBrains 出品</sub>
    </td>
  </tr>
</table>

| 项目 / 库 / 数据源 | 贡献 | 许可证 / 说明 |
|---|---|---|
| [requests](https://github.com/psf/requests) | 网络请求与图片下载 | Apache-2.0 |
| [fake-useragent](https://github.com/fake-useragent/fake-useragent)（可选） | 随机 User-Agent | 以项目仓库 LICENSE 为准 |
| [pytest](https://pytest.org/) / [pytest-cov](https://pytest-cov.readthedocs.io/) | 测试与覆盖率 | MIT |
| [flake8](https://flake8.pycqa.org/) | 静态检查 | MIT |
| [mypy](https://mypy-lang.org/) | 类型检查 | MIT |
| [black](https://black.readthedocs.io/) / [isort](https://pycqa.github.io/isort/) | 代码格式化与 import 排序 | MIT |
| [JetBrains](https://www.jetbrains.com/) | 提供 IntelliJ IDEA / PyCharm 等开发工具 | 商业授权（开源项目可申请免费许可证） |
| 王者荣耀官方数据（`pvp.qq.com`、`game.gtimg.cn`） | 英雄与皮肤数据来源 | 版权归腾讯所有，仅学习交流 |
| 英雄联盟官方数据（`lol.qq.com`、`game.gtimg.cn`） | 英雄与皮肤数据来源 | 版权归 Riot Games / 腾讯所有，仅学习交流 |

> 本仓库合并自已归档的 [KPL_skin](https://github.com/leipengic/KPL_skin) 与 [LOL_skin](https://github.com/leipengic/LOL_skin)，感谢原仓使用者的反馈。
> 贡献者名单：_（待补充，欢迎在 PR 中署名）_

## 版权

- 王者荣耀图片版权归腾讯所有
- 英雄联盟图片版权归 Riot Games / 腾讯所有
- 守望先锋图片版权归 Blizzard Entertainment 所有
- 工具代码采用 [MIT License](LICENSE)

> ⚠️ 本仓库仅供学习交流，请勿用于商业用途。所有下载的图片版权归原游戏厂商所有。