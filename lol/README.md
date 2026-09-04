# lol/

英雄联盟（LOL）皮肤批量下载子包。

## 快速使用

```bash
# 进入仓库根目录后
python -m lol.lol_skin

# 只下载名字含 "安妮" 的英雄
python -m lol.lol_skin --hero-filter "安妮"

# 指定输出目录、含炫彩
python -m lol.lol_skin -o ./my_skins --include-chromas

# 启用代理
python -m lol.lol_skin --use-proxy --proxy http://127.0.0.1:7890

# 启用 Bright Data（推荐用环境变量，密码不进 shell history）
export BRD_CUSTOMER=hl_xxxxxxxx
export BRD_ZONE=residential
export BRD_PASSWORD=xxxxxxxxxxxx
export BRD_COUNTRY=cn
python -m lol.lol_skin --use-proxy

# 或一次性传 URI
python -m lol.lol_skin --use-proxy --brd-uri "brd://C123:residential:PWD;country=cn"
```

> 兼容老调用：`python lol/lol_skin.py` 仍可直接运行（脚本同时支持两种入口）。

## 数据源

| 用途 | URL |
|---|---|
| 英雄列表 | `https://lol.qq.com/biz/hero/champion.js` |
| 英雄皮肤 | `https://game.gtimg.cn/images/lol/act/img/js/hero/{hero_id}.js` |
| 旧版皮肤图（回退） | `ossweb-img.qq.com/.../skin/big{hero_id}{idx:03d}.jpg` |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-o` / `--output` | `./lol/lol_skins` | 保存目录 |
| `-f` / `--hero-filter` | 无 | 英雄名过滤（中英文） |
| `--include-chromas` | False | 是否下载炫彩 |
| `--use-proxy` | False | 启用代理 |
| `--proxy` | None | 代理地址，多个用逗号分隔 |
| `-t` / `--timeout` | 15 | HTTP 超时（秒） |
| `-r` / `--retries` | 3 | 失败重试次数 |
| `--delay` | 0.3 | 每次下载延迟（秒） |