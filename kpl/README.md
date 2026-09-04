# kpl/

王者荣耀（KPL）英雄皮肤批量下载子包。

## 快速使用

```bash
python -m kpl.wangzhe_skin

# 指定输出目录
python -m kpl.wangzhe_skin -o D:/wzry_skins

# 自定义超时与重试
python -m kpl.wangzhe_skin -t 15 -r 5 --delay 1.5

# 启用 Bright Data（KPL 数据源在国内，一般不需要，但支持）
python -m kpl.wangzhe_skin --use-proxy --brd-uri "brd://C123:residential:PWD;country=cn"
```

> 兼容老调用：`python kpl/wangzhe_skin.py` 仍可直接运行。

## 数据源

| 用途 | URL |
|---|---|
| 英雄列表 | `https://pvp.qq.com/web201605/js/herolist.json` |
| 皮肤图片 | `http://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{ename}/{ename}-bigskin-{skin_id}.jpg` |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-o` / `--output` | `./kpl/skins` | 保存目录 |
| `-t` / `--timeout` | 15 | HTTP 超时（秒） |
| `-r` / `--retries` | 3 | 失败重试次数 |
| `--delay` | 0.3 | 每次下载延迟（秒，下限；随机上浮至 `max(delay*3, 1.0)`） |

皮肤序号探测到 404 时自动停止该英雄后续下载，无需关心上限。