"""英雄联盟（LOL）全英雄皮肤批量下载工具（monorepo 版本）。

数据源：
- 英雄列表: https://lol.qq.com/biz/hero/champion.js (JS 脚本，含 LOLherojs.champion.keys)
- 英雄皮肤: https://game.gtimg.cn/images/lol/act/img/js/hero/{hero_id}.js
- 旧版 URL 回退: ossweb-img.qq.com/images/lol/web201310/skin/big{hero_id}{idx:03d}.jpg

仅供学习交流，请勿用于商业用途。图片版权归腾讯所有。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 允许直接 `python lol/lol_skin.py` 运行（兼容老调用方式）
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import (
    add_common_download_args,
    add_proxy_args,
    download_image,
    request_with_retry,
    resolve_proxies,
    sanitize_filename,
)


CHAMPION_JS_URL: str = "https://lol.qq.com/biz/hero/champion.js"
HERO_JS_URL_TEMPLATE: str = (
    "https://game.gtimg.cn/images/lol/act/img/js/hero/{hero_id}.js"
)
OLD_SKIN_URL_TEMPLATE: str = (
    "https://ossweb-img.qq.com/images/lol/web201310/skin/big{hero_id}{skin_idx:03d}.jpg"
)
SKIN_HTML_URL: str = "https://lol.qq.com/web201311/info-heros.shtml"


def _parse_champion_js(raw_text: str) -> Dict[str, str]:
    """解析 champion.js，提取 {英雄ID: 英文名} 映射。"""
    match = re.search(r'"keys"\s*:\s*(\{.*?\})\s*,\s*"data"', raw_text)
    if not match:
        print("  错误: 无法从 champion.js 中提取 keys 字段")
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        print(f"  解析 champion.js 失败: {exc}")
        return {}


def get_hero_list(
    *,
    timeout: int,
    retries: int,
    hero_filter: Optional[str] = None,
    proxies: Optional[Dict[str, str]] = None,
) -> List[Tuple[str, str]]:
    """获取英雄列表（(英雄ID, 英文名) 列表）。"""
    print("正在获取英雄列表...")
    resp = request_with_retry(
        CHAMPION_JS_URL,
        timeout=timeout,
        max_retries=retries,
        proxies=proxies,
    )
    if resp is None:
        print("  错误: 无法获取英雄列表数据")
        return []

    hero_map = _parse_champion_js(resp.text)
    if not hero_map:
        return []

    hero_list: List[Tuple[str, str]] = sorted(
        hero_map.items(), key=lambda x: int(x[0])
    )

    if hero_filter:
        fl = hero_filter.lower()
        filtered = [(i, n) for i, n in hero_list if fl in n.lower()]
        if filtered:
            print(f"  应用过滤 '{hero_filter}'，匹配到 {len(filtered)} 个英雄")
            return filtered
        print(f"  警告: 无匹配 '{hero_filter}' 的英雄，返回全部")

    print(f"  成功获取 {len(hero_list)} 个英雄")
    return hero_list


def _parse_hero_skins_js(
    raw_text: str,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """解析 hero/{id}.js，返回 (英雄信息dict, 皮肤列表)。"""
    try:
        data = json.loads(raw_text)
        return data.get("hero", {}), data.get("skins", [])
    except json.JSONDecodeError as exc:
        print(f"  解析英雄皮肤 JSON 失败: {exc}")
        return {}, []


def get_hero_skins(
    hero_id: str,
    *,
    timeout: int,
    retries: int,
    proxies: Optional[Dict[str, str]] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    url = HERO_JS_URL_TEMPLATE.format(hero_id=hero_id)
    resp = request_with_retry(url, timeout=timeout, max_retries=retries, proxies=proxies)
    if resp is None:
        return {}, []
    return _parse_hero_skins_js(resp.text)


def _resolve_skin_image_url(
    skin: Dict[str, Any], hero_id: str, skin_index: int
) -> Optional[str]:
    """根据优先级挑选图片 URL。"""
    chromas = skin.get("chromas", "0")
    if chromas == "1":
        url = skin.get("chromaImg") or ""
    else:
        url = skin.get("mainImg") or skin.get("loadingImg") or ""

    if url:
        return url if url.startswith("http") else f"https:{url}"

    fallback = OLD_SKIN_URL_TEMPLATE.format(
        hero_id=hero_id.zfill(3), skin_idx=skin_index
    )
    print(f"  警告: 皮肤 {skin.get('skinId')} 无图片URL，回退: {fallback}")
    return fallback


def download_skin(
    skin: Dict[str, Any],
    *,
    hero_id: str,
    hero_dir: Path,
    skin_index: int,
    include_chromas: bool,
    timeout: int,
    retries: int,
    proxies: Optional[Dict[str, str]],
) -> bool:
    """下载单张皮肤到 {hero_dir}。"""
    chromas = skin.get("chromas", "0")
    if chromas == "1" and not include_chromas:
        return False

    skin_id = skin.get("skinId", f"unknown_{skin_index}")
    skin_name = skin.get("name") or f"skin_{skin_index}"

    img_url = _resolve_skin_image_url(skin, hero_id, skin_index)
    if not img_url:
        return False

    ext = ".jpg"
    if "." in img_url.split("?")[0].rsplit("/", 1)[-1]:
        ext = "." + img_url.split("?")[0].rsplit("/", 1)[-1].rsplit(".", 1)[-1]

    filename = f"{skin_index:02d}_{skin_id}_{sanitize_filename(skin_name)}{ext}"
    save_path = hero_dir / filename

    ok = download_image(
        img_url,
        save_path,
        timeout=timeout,
        max_retries=retries,
        proxies=proxies,
        stop_on_404=False,
    )
    if ok:
        print(f"  [成功] {filename}")
    return ok


def _run_js_mode(args: argparse.Namespace, proxies: Optional[Dict[str, str]]) -> Tuple[int, int, int, int]:
    """JS 数据接口模式：完整下载流程。"""
    hero_list = get_hero_list(
        timeout=args.timeout,
        retries=args.retries,
        hero_filter=args.hero_filter,
        proxies=proxies,
    )
    if not hero_list:
        print("错误: 英雄列表为空，程序退出。")
        return 0, 0, 0, 0

    total = len(hero_list)
    processed = 0
    total_skins = 0
    downloaded_skins = 0
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, (hero_id, hero_alias) in enumerate(hero_list, start=1):
        print(f"\n[{idx}/{total}] 处理英雄 ID={hero_id}, alias={hero_alias}")
        hero_info, skins = get_hero_skins(
            hero_id,
            timeout=args.timeout,
            retries=args.retries,
            proxies=proxies,
        )
        if not skins:
            print("  跳过: 未获取到皮肤数据")
            continue

        hero_cn_name = hero_info.get("name") or hero_alias
        hero_dir = output_dir / sanitize_filename(hero_cn_name)

        skins_to_dl = (
            skins if args.include_chromas
            else [s for s in skins if s.get("chromas", "0") != "1"]
        )
        print(f"  英雄名: {hero_cn_name}，皮肤数: {len(skins_to_dl)}")

        for s_idx, skin in enumerate(skins_to_dl):
            total_skins += 1
            if download_skin(
                skin,
                hero_id=hero_id,
                hero_dir=hero_dir,
                skin_index=s_idx,
                include_chromas=args.include_chromas,
                timeout=args.timeout,
                retries=args.retries,
                proxies=proxies,
            ):
                downloaded_skins += 1
            if args.delay > 0:
                time.sleep(args.delay)

        processed += 1

    return total, processed, total_skins, downloaded_skins


def main() -> int:
    parser = argparse.ArgumentParser(
        description="英雄联盟（LOL）皮肤批量下载工具（monorepo 版本）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_common_download_args(parser)
    add_proxy_args(parser)
    parser.add_argument(
        "-f", "--hero-filter",
        default=None,
        help="英雄名过滤关键字（中英文部分匹配）",
    )
    parser.add_argument(
        "--include-chromas",
        action="store_true",
        default=False,
        help="是否下载炫彩皮肤",
    )
    parser.set_defaults(
        output=str(Path.cwd() / "lol" / "lol_skins"),
    )
    args = parser.parse_args()

    proxies = resolve_proxies(args) if args.use_proxy else None
    if args.use_proxy and proxies is None:
        print("错误: --use-proxy 已启用但未提供代理地址")
        print("  提示: 传 --proxy / --brd-uri / --brd-customer + --brd-zone + --brd-password 之一")
        return 2

    print("=" * 60)
    print("  英雄联盟 LOL 皮肤下载工具（monorepo）")
    print("=" * 60)
    print(f"  输出目录      : {args.output}")
    print(f"  英雄过滤      : {args.hero_filter or '(无)'}")
    print(f"  包含炫彩      : {args.include_chromas}")
    print(f"  启用代理      : {bool(proxies)}")
    print(f"  下载延迟      : {args.delay}s")
    print("=" * 60)

    total, processed, total_skins, downloaded = _run_js_mode(args, proxies)

    print("\n" + "=" * 60)
    print("下载完成！统计信息:")
    print(f"  英雄总数      : {total}")
    print(f"  成功处理英雄  : {processed}")
    print(f"  皮肤总数      : {total_skins}")
    print(f"  成功下载皮肤  : {downloaded}")
    print(f"  保存目录      : {args.output}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())