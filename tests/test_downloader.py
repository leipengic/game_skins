"""_common.downloader.parse_proxy_list 的单元测试。"""
from _common.downloader import parse_proxy_list


def test_none_returns_empty():
    assert parse_proxy_list(None) == []


def test_empty_string_returns_empty():
    assert parse_proxy_list("") == []


def test_single_proxy():
    result = parse_proxy_list("http://127.0.0.1:7890")
    assert result == [{"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}]


def test_multiple_proxies_comma_separated():
    raw = "http://127.0.0.1:7890, http://10.0.0.1:8080"
    result = parse_proxy_list(raw)
    assert len(result) == 2
    assert result[1]["https"] == "http://10.0.0.1:8080"


def test_whitespace_tolerated():
    raw = "  http://a:1 ,   ,http://b:2 "
    result = parse_proxy_list(raw)
    assert len(result) == 2