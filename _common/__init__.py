"""game_skins 共享工具层"""

from .headers import random_ua, DEFAULT_CHROME_UA
from .paths import sanitize_filename
from .downloader import (
    request_with_retry,
    download_image,
    parse_proxy_list,
    ProxyConfigError,
)
from .cli import add_common_download_args, add_proxy_args, resolve_proxies
from .bright_data import (
    build_bright_data_proxy,
    parse_bright_data_uri,
    normalize_proxy,
    BrightDataConfigError,
    BRD_DEFAULT_HOST,
    BRD_DEFAULT_PORT,
)

__all__ = [
    "random_ua",
    "DEFAULT_CHROME_UA",
    "sanitize_filename",
    "request_with_retry",
    "download_image",
    "parse_proxy_list",
    "ProxyConfigError",
    "add_common_download_args",
    "add_proxy_args",
    "resolve_proxies",
    "build_bright_data_proxy",
    "parse_bright_data_uri",
    "normalize_proxy",
    "BrightDataConfigError",
    "BRD_DEFAULT_HOST",
    "BRD_DEFAULT_PORT",
]