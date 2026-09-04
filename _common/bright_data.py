"""Bright Data（亮数据 / bright.cn）代理封装。

Bright Data 的代理接入形态：
- 主机：brd.superproxy.io（默认）
- 端口：33335（住宅代理默认）/ 22225（数据中心）等
- 用户名：brd-customer-{CUSTOMER_ID}-zone-{ZONE_NAME}[-country-XX][-session-...]
- 密码：zone 密码

控制面板：https://www.bright.cn/cp/start
文档：https://docs.brightdata.com/

本模块提供：
1. build_bright_data_proxy() —— 直接由 customer/zone/password 构造代理字典
2. parse_bright_data_uri() —— 解析 brd:// URI 为代理字典（CLI 用法）
3. normalize_proxy() —— 统一处理普通 HTTP 代理与 Bright Data URI
"""
from __future__ import annotations

from typing import Dict, Optional
from urllib.parse import quote

BRD_DEFAULT_HOST: str = "brd.superproxy.io"
BRD_DEFAULT_PORT: int = 33335


class BrightDataConfigError(ValueError):
    """Bright Data 配置错误（参数缺失、URI 格式不对等）。"""


def build_bright_data_proxy(
    customer: str,
    zone: str,
    password: str,
    *,
    country: Optional[str] = None,
    host: str = BRD_DEFAULT_HOST,
    port: int = BRD_DEFAULT_PORT,
    session: Optional[str] = None,
) -> Dict[str, str]:
    """构造 Bright Data 代理字典，可直接给 requests 的 proxies 参数。

    Args:
        customer: Bright Data 账户 customer ID（控制面板 → Settings 里可见）
        zone: 代理 zone 名称（控制面板 → Zones 创建）
        password: zone 密码（控制面板 → Zones → Access parameters）
        country: 可选国家代码，如 'cn' / 'us'
        host: 代理主机，默认 brd.superproxy.io
        port: 代理端口，默认 33335
        session: 粘性会话 ID；不传则按请求轮换

    Returns:
        {"http": "...", "https": "..."} 字典

    Raises:
        BrightDataConfigError: 参数缺失
    """
    if not (customer and zone and password):
        raise BrightDataConfigError("customer / zone / password 均不可为空")

    user = f"brd-customer-{customer}-zone-{zone}"
    if country:
        user += f"-country-{country}"
    if session:
        user += f"-session-{session}"

    # 密码含特殊字符时用 quote 编码，避免 URL 解析错乱
    safe_password = quote(password, safe="")
    proxy_url = f"http://{user}:{safe_password}@{host}:{port}"
    return {"http": proxy_url, "https": proxy_url}


def parse_bright_data_uri(uri: str) -> Dict[str, str]:
    """解析 `brd://` URI 为 Bright Data 代理字典。

    URI 格式：
        brd://customer:zone:password[;key=value;key=value;...]

    支持的可选 key：
        - country=cn        国家代码
        - host=brd.superproxy.io   代理主机（一般无需改）
        - port=22225        代理端口（按 zone 类型不同）
        - session=abc123    粘性会话 ID

    示例：
        brd://CUSTOMER123:residential:PASSWORD
        brd://CUSTOMER123:residential:PASSWORD;country=cn
        brd://CUSTOMER123:residential:PASSWORD;country=us;port=22225
        brd://CUSTOMER123:residential:PASSWORD;session=run-001

    Args:
        uri: 形如 `brd://...` 的 URI

    Returns:
        代理字典

    Raises:
        BrightDataConfigError: URI 格式错误
    """
    if not isinstance(uri, str) or not uri.startswith("brd://"):
        raise BrightDataConfigError(f"不是合法的 brd:// URI：{uri!r}")

    body = uri[len("brd://"):]
    if ";" in body:
        cred_part, query_part = body.split(";", 1)
        extras: Dict[str, str] = {}
        for kv in query_part.split(";"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                extras[k] = v
    else:
        cred_part = body
        extras = {}

    # 处理凭证段
    cred_tokens = cred_part.split(":")
    if len(cred_tokens) != 3:
        raise BrightDataConfigError(
            f"brd:// 凭证段必须是 customer:zone:password 三段，得到 {len(cred_tokens)} 段：{uri}"
        )
    customer, zone, password = cred_tokens
    if not (customer and zone and password):
        raise BrightDataConfigError(f"customer/zone/password 不能为空：{uri}")

    # 解析可选参数
    country = extras.get("country")
    host = extras.get("host", BRD_DEFAULT_HOST)
    port_raw = extras.get("port")
    try:
        port = int(port_raw) if port_raw else BRD_DEFAULT_PORT
    except ValueError as exc:
        raise BrightDataConfigError(f"port 必须是整数：{port_raw!r}") from exc
    session = extras.get("session")

    return build_bright_data_proxy(
        customer=customer,
        zone=zone,
        password=password,
        country=country,
        host=host,
        port=port,
        session=session,
    )


def normalize_proxy(spec: str) -> Dict[str, str]:
    """把 CLI 传入的代理 spec 统一为代理字典。

    支持：
    - `brd://customer:zone:password[;k=v;...]` —— Bright Data
    - `http://ip:port`、`http://user:pass@ip:port`、`socks5://...` —— 直 URL

    Args:
        spec: 代理配置字符串

    Returns:
        requests 可用的 proxies 字典

    Raises:
        BrightDataConfigError: brd:// 格式错误
        ValueError: 其他格式错误
    """
    if spec.startswith("brd://"):
        return parse_bright_data_uri(spec)
    # 透传普通 URL，让 requests 自己处理 http/https/socks5 协议
    return {"http": spec, "https": spec}