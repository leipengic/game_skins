"""_common.headers.random_ua 的单元测试。"""
from _common.headers import DEFAULT_CHROME_UA, random_ua


def test_default_chrome_ua_not_empty():
    assert isinstance(DEFAULT_CHROME_UA, str)
    assert DEFAULT_CHROME_UA.startswith("Mozilla/")


def test_random_ua_returns_non_empty_string():
    ua = random_ua()
    assert isinstance(ua, str)
    assert len(ua) > 10


def test_random_ua_multiple_calls():
    # fake_useragent 不可用时应至少稳定返回 DEFAULT_CHROME_UA
    uas = {random_ua() for _ in range(3)}
    assert all(isinstance(u, str) and u for u in uas)