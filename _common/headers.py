"""统一的 User-Agent 处理。

优先使用 fake_useragent 获取随机 UA，库不可用时使用硬编码 Chrome UA。
两个老仓一个用 fake_useragent，一个用硬编码 UA，合并后只保留一份逻辑。
"""
from __future__ import annotations

DEFAULT_CHROME_UA: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

_FAKE_UA: bool = True
try:
    from fake_useragent import UserAgent
except ImportError:  # pragma: no cover - 依赖可选
    _FAKE_UA = False
    UserAgent = None  # type: ignore[assignment]


def random_ua() -> str:
    """返回一个随机 User-Agent 字符串。

    优先 fake_useragent.random；库未安装时回退到 DEFAULT_CHROME_UA。
    单个 fake_useragent.UserAgent 实例会被复用（与原 KPL_skin 每次新建实例的写法不同）。
    """
    if _FAKE_UA and UserAgent is not None:
        try:
            return UserAgent().random
        except Exception:
            # 离线首次下载 UA 列表会抛异常，这里吞掉回退硬编码
            pass
    return DEFAULT_CHROME_UA