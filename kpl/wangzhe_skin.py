"""王者荣耀英雄皮肤图片批量下载工具（monorepo 版本）。

数据源：王者荣耀官网公开 JS 接口 herolist.json + game.gtimg.cn CDN
- 英雄列表: https://pvp.qq.com/web201605/js/herolist.json
- 皮肤图片: http://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{ename}/{ename}-bigskin-{skin_id}.jpg

仅供学习交流，请勿用于商业用途。图片版权归腾讯所有。
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 允许直接 `python kpl/wangzhe_skin.py` 运行（兼容老调用方式）
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import (
    add_common_download_args,
    add_proxy_args,
    download_image,
    resolve_proxies,
)


HERO_LIST_URL: str = "https://pvp.qq.com/web201605/js/herolist.json"
SKIN_BASE_URL: str = (
    "http://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/"
    "{ename}/{ename}-bigskin-{skin_id}.jpg"
)
MAX_SKIN_COUNT: int = 10  # 单英雄最大皮肤序号探测上限


def fetch_hero_list(timeout: int, retries: int, proxies: Optional[Dict] = None) -> List[Dict]:
    """拉取官方英雄列表 JSON。

    使用 _common.downloader.request_with_retry 替代原 self-implemented 重试循环。
    """
    from _common.downloader import request_with_retry

    resp = request_with_retry(
        HERO_LIST_URL, timeout=timeout, max_retries=retries, proxies=proxies
    )
    if resp is None:
        raise RuntimeError("多次重试后仍无法获取英雄列表，请检查网络连接")
    try:
        return resp.json()
    except ValueError as exc:
        raise RuntimeError(f"英雄列表 JSON 解析失败：{exc}") from exc


def download_hero_skins(
    hero: Dict,
    output_dir: Path,
    *,
    timeout: int,
    retries: int,
    delay: float,
    proxies: Optional[Dict] = None,
) -> int:
    """下载单个英雄的全部皮肤。

    Returns:
        该英雄成功下载的张数
    """
    from _common import sanitize_filename  # 本子包未用到，留作未来扩展

    hero_name = hero.get("cname", "未知英雄")
    ename = hero.get("ename")
    if not ename:
        print(f"[跳过] 英雄数据缺少编号：{hero_name}")
        return 0

    safe_name = sanitize_filename(hero_name) or "未知英雄"
    hero_dir = output_dir / safe_name
    print(f"[开始] 下载英雄：{hero_name}")
    success = 0

    for skin_id in range(MAX_SKIN_COUNT):
        skin_url = SKIN_BASE_URL.format(ename=ename, skin_id=skin_id)
        save_path = hero_dir / f"{skin_id}.jpg"
        ok = download_image(
            skin_url,
            save_path,
            timeout=timeout,
            max_retries=retries,
            proxies=proxies,
            stop_on_404=True,
        )
        if ok:
            success += 1
        else:
            print(f"  - 皮肤 {skin_id} 不存在或下载失败，停止该英雄")
            break

        if delay > 0:
            time_sleep = random.uniform(delay, max(delay * 3, 1.0))
            import time as _t
            _t.sleep(time_sleep)

    print(f"[完成] {hero_name}：成功 {success} 张\n")
    return success


def main() -> int:
    parser = argparse.ArgumentParser(
        description="王者荣耀英雄皮肤图片批量下载工具（monorepo 版本）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_common_download_args(parser)
    add_proxy_args(parser)  # KPL 默认不启用，需要显式 --use-proxy
    parser.set_defaults(
        output=str(Path.cwd() / "kpl" / "skins"),
    )
    args = parser.parse_args()

    proxies = resolve_proxies(args) if args.use_proxy else None
    if args.use_proxy and proxies is None:
        print("错误: --use-proxy 已启用但未提供代理地址")
        print("  提示: 传 --proxy / --brd-uri / --brd-customer + --brd-zone + --brd-password 之一")
        return 2

    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"输出目录：{output_dir}")
    print(f"超时：{args.timeout}s  重试：{args.retries}次  延迟：{args.delay}s\n")

    try:
        hero_list = fetch_hero_list(args.timeout, args.retries, proxies)
    except RuntimeError as exc:
        print(f"[致命错误] {exc}")
        return 1

    print(f"共获取到 {len(hero_list)} 个英雄\n")

    total_ok = 0
    for hero in hero_list:
        try:
            total_ok += download_hero_skins(
                hero,
                output_dir,
                timeout=args.timeout,
                retries=args.retries,
                delay=args.delay,
                proxies=proxies,
            )
        except KeyboardInterrupt:
            print("\n[中断] 用户取消")
            return 130
        except Exception as exc:  # 单英雄失败不阻塞其他英雄
            print(f"[错误] {hero.get('cname', '未知英雄')}：{exc}")

    print(f"全部任务执行完毕，累计下载 {total_ok} 张皮肤")
    return 0


if __name__ == "__main__":
    sys.exit(main())