"""统一的 HTTP 请求与图片下载工具。

合并自：
- KPL_skin.WangzheSkin: download_image + fetch_hero_list 风格（无代理）
- LOL_skin.lol_skin: request_with_proxy（带代理、自动重试、指数退避）

统一接口：
- request_with_retry: 仅负责 HTTP GET + 重试 + 可选代理
- download_image: 在 request_with_retry 之上负责写文件
- 两个老仓的 CLI 参数都被收纳到 add_common_download_args
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .headers import random_ua


class ProxyConfigError(RuntimeError):
    """代理配置错误（如用户启用了 --use-proxy 但 proxy_list 为空）。"""


def request_with_retry(
    url: str,
    *,
    timeout: int = 15,
    max_retries: int = 3,
    proxies: Optional[Dict[str, str]] = None,
    backoff: bool = True,
) -> Optional[requests.Response]:
    """GET 请求，统一封装重试与指数退避。

    Args:
        url: 请求 URL
        timeout: 单次请求超时时间（秒）
        max_retries: 最大重试次数（包含首次）
        proxies: 代理字典，None 表示直连
        backoff: 是否使用指数退避（默认开启）

    Returns:
        成功时返回 Response，失败返回 None
    """
    headers = {"User-Agent": random_ua()}

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=timeout,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as exc:
            if attempt >= max_retries:
                print(f"  [失败] 请求已达最大重试次数 {max_retries}：{url} ({exc})")
                return None
            wait = attempt if backoff else 1
            print(
                f"  [重试 {attempt}/{max_retries}] {exc}，{wait}s 后重试: {url}"
            )
            time.sleep(wait)

    return None  # 防御性返回，理论上循环已覆盖


def download_image(
    url: str,
    save_path: Path,
    *,
    timeout: int = 30,
    max_retries: int = 3,
    proxies: Optional[Dict[str, str]] = None,
    stop_on_404: bool = True,
) -> bool:
    """下载单张图片并落盘。

    Args:
        url: 图片 URL
        save_path: 完整保存路径（含文件名）
        timeout: 单次请求超时
        max_retries: 最大重试
        proxies: 代理字典
        stop_on_404: 遇 404 时立即停止（用于按序号递增探测时提前终止）

    Returns:
        是否成功
    """
    headers = {"User-Agent": random_ua()}

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=timeout,
            )
            if resp.status_code == 200 and resp.content:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                save_path.write_bytes(resp.content)
                return True
            if resp.status_code == 404:
                if stop_on_404:
                    return False
                # 非 stop 模式下，404 视作失败但仍走完重试
                print(f"  [404] {url}")
                return False
            print(
                f"  [状态码 {resp.status_code}] {url} "
                f"(第 {attempt}/{max_retries} 次)"
            )
        except requests.exceptions.Timeout:
            print(f"  [超时] {url} (第 {attempt}/{max_retries} 次)")
        except requests.exceptions.RequestException as exc:
            print(f"  [网络错误] {exc} (第 {attempt}/{max_retries} 次)")
        except OSError as exc:
            print(f"  [写入失败] {save_path}：{exc}")
            return False

        if attempt < max_retries:
            time.sleep(1)

    print(f"  [失败] 图片下载失败：{save_path.name}")
    return False


def parse_proxy_list(raw: Any) -> list[Dict[str, str]]:
    """解析 CLI 传入的代理字符串为字典列表。

    支持格式：`http://ip:port`，多个用逗号分隔。
    """
    if not raw:
        return []
    out: list[Dict[str, str]] = []
    for item in str(raw).split(","):
        item = item.strip()
        if not item:
            continue
        out.append({"http": item, "https": item})
    return out