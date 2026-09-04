"""文件名与路径工具。"""
from __future__ import annotations

import re

# Windows / *nix 通用的非法字符集合，LOL_skin 原本只覆盖 Windows 字符
_INVALID_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
_TRIM_CHARS = " ."
# 占位符 NUL：先替换为 \x00，最后合并连续的占位符为一个
_PLACEHOLDER = "\x00"


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """清理文件名中的非法字符。

    步骤：
    1. 用 \\x00 占位所有非法字符（不直接用 `_`，避免破坏合法 `_`）
    2. 合并连续的占位符为单个 `replacement`
    3. 替换占位符为 `replacement`
    4. 去掉首尾的 `.` 与空格（Windows 不允许结尾的 `.` 和空格）
    5. 若全部字符都被清掉，返回单个 `replacement`

    Args:
        name: 原始文件名（不含路径）
        replacement: 用于替换非法字符的占位符，默认下划线

    Returns:
        清理后的安全文件名
    """
    cleaned = _INVALID_CHARS.sub(_PLACEHOLDER, name)
    cleaned = re.sub(f"{_PLACEHOLDER}+", replacement, cleaned)
    cleaned = cleaned.strip().strip(_TRIM_CHARS)
    return cleaned or replacement