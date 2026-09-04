"""共享的 argparse 参数组。

两个老仓的参数命名有差异：
- KPL: --timeout / --retries / --sleep-min / --sleep-max
- LOL: --delay

合并时合并为 `--timeout / --retries / --delay`，老参数作为 alias 保留兼容。
"""
from __future__ import annotations

import argparse
import os
from typing import Optional


def add_common_download_args(parser: argparse.ArgumentParser) -> None:
    """为子命令注册共用的下载参数。

    Args:
        parser: 子命令解析器
    """
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="皮肤图片输出目录（子命令会提供各自的默认值）",
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=15,
        help="单次 HTTP 请求超时时间（秒），默认 15",
    )
    parser.add_argument(
        "-r", "--retries",
        type=int,
        default=3,
        help="失败重试次数，默认 3",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="每次下载之间的延迟秒数，默认 0.3（防风控）",
    )


def add_proxy_args(parser: argparse.ArgumentParser) -> None:
    """为支持代理的子命令注册代理参数（KPL 不调用即可）。

    支持两种风格：
    - 普通代理：--proxy http://user:pass@ip:port
    - Bright Data：--proxy brd://customer:zone:password[;country=cn;session=xxx]
                  或专用开关：--brd-uri / --brd-customer / --brd-zone / --brd-password
    """
    proxy_group = parser.add_argument_group("代理设置")
    proxy_group.add_argument(
        "--use-proxy",
        action="store_true",
        default=False,
        help="启用 HTTP 代理（需配合 --proxy 或 --brd-* 给出实际地址）",
    )
    proxy_group.add_argument(
        "--proxy",
        default=None,
        help=(
            "代理地址。格式：http://ip:port 或 socks5://ip:port；"
            "Bright Data 简写：brd://customer:zone:password[;country=cn;port=22225]"
        ),
    )

    # Bright Data 专用参数（更安全：可只走环境变量，避免进 shell history）
    brd_group = parser.add_argument_group("Bright Data 专用设置")
    brd_group.add_argument(
        "--brd-uri",
        default=os.environ.get("GAME_SKINS_BRD_URI"),
        help=(
            "Bright Data 完整 URI，例如 brd://CUSTOMER:residential:PASSWORD"
            "（也可设环境变量 GAME_SKINS_BRD_URI）"
        ),
    )
    brd_group.add_argument(
        "--brd-customer",
        default=os.environ.get("BRD_CUSTOMER"),
        help="Bright Data customer ID（也可设环境变量 BRD_CUSTOMER）",
    )
    brd_group.add_argument(
        "--brd-zone",
        default=os.environ.get("BRD_ZONE"),
        help="Bright Data zone 名称（也可设环境变量 BRD_ZONE）",
    )
    brd_group.add_argument(
        "--brd-password",
        default=os.environ.get("BRD_PASSWORD"),
        help=(
            "Bright Data zone 密码（建议通过环境变量 BRD_PASSWORD 设置，"
            "避免进入 shell history）"
        ),
    )
    brd_group.add_argument(
        "--brd-country",
        default=os.environ.get("BRD_COUNTRY"),
        help="Bright Data 国家代码，如 cn / us（也可设环境变量 BRD_COUNTRY）",
    )
    brd_group.add_argument(
        "--brd-session",
        default=os.environ.get("BRD_SESSION"),
        help=(
            "Bright Data 粘性会话 ID；不传则每请求轮换 IP"
            "（也可设环境变量 BRD_SESSION）"
        ),
    )


def resolve_proxies(args: argparse.Namespace) -> Optional[dict]:
    """从 argparse Namespace 解析最终代理配置。

    优先级：--brd-uri > (--brd-customer/--brd-zone/--brd-password) > --proxy > None
    """
    # 1. Bright Data URI
    if getattr(args, "brd_uri", None):
        from .bright_data import parse_bright_data_uri
        return parse_bright_data_uri(args.brd_uri)

    # 2. Bright Data 分字段
    customer = getattr(args, "brd_customer", None)
    zone = getattr(args, "brd_zone", None)
    password = getattr(args, "brd_password", None)
    if customer and zone and password:
        from .bright_data import build_bright_data_proxy
        return build_bright_data_proxy(
            customer=customer,
            zone=zone,
            password=password,
            country=getattr(args, "brd_country", None),
            session=getattr(args, "brd_session", None),
        )

    # 3. 普通代理
    proxy_str = getattr(args, "proxy", None)
    if proxy_str:
        from .bright_data import normalize_proxy
        return normalize_proxy(proxy_str)

    return None