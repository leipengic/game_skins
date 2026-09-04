"""_common.paths.sanitize_filename 的单元测试。"""
from _common.paths import sanitize_filename


def test_replace_windows_invalid_chars():
    assert sanitize_filename('a/b\\c:d*e?f"g<h>i|j') == "a_b_c_d_e_f_g_h_i_j"


def test_replace_control_chars():
    assert sanitize_filename("foo\x00bar\x01baz") == "foo_bar_baz"


def test_strip_trailing_dots_and_spaces():
    # Windows 不允许以 . 或空格结尾的文件名
    assert sanitize_filename("hello. ") == "hello"
    assert sanitize_filename("...weird...") == "weird"


def test_empty_after_clean_returns_underscore():
    assert sanitize_filename("////") == "_"
    assert sanitize_filename("") == "_"


def test_keep_normal_unicode():
    # 中英文与表情应保留
    assert sanitize_filename("黑暗之女 安妮 🧚") == "黑暗之女 安妮 🧚"