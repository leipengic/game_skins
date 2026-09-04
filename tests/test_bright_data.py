"""_common.bright_data 单元测试。"""
from __future__ import annotations

import pytest

from _common.bright_data import (
    BRD_DEFAULT_HOST,
    BRD_DEFAULT_PORT,
    BrightDataConfigError,
    build_bright_data_proxy,
    normalize_proxy,
    parse_bright_data_uri,
)


# ---- build_bright_data_proxy ----

def test_build_minimal_proxy():
    p = build_bright_data_proxy("C123", "residential", "secret")
    assert p["http"] == f"http://brd-customer-C123-zone-residential:secret@{BRD_DEFAULT_HOST}:{BRD_DEFAULT_PORT}"
    assert p["https"] == p["http"]


def test_build_with_country():
    p = build_bright_data_proxy("C123", "residential", "secret", country="cn")
    assert "country-cn" in p["http"]
    assert "brd-customer-C123-zone-residential-country-cn" in p["http"]


def test_build_with_session():
    p = build_bright_data_proxy("C123", "residential", "secret", session="run-001")
    assert "session-run-001" in p["http"]


def test_build_with_custom_host_port():
    p = build_bright_data_proxy(
        "C123", "datacenter", "secret", host="custom.brd.io", port=22225
    )
    assert "custom.brd.io:22225" in p["http"]


def test_build_quotes_special_chars_in_password():
    # 密码含 @ / : 等特殊字符时必须 quote，否则 URL 解析错乱
    p = build_bright_data_proxy("C123", "residential", "p@ss:wo#rd")
    assert "p%40ss%3Awo%23rd" in p["http"]
    assert "@brd.superproxy.io" in p["http"]


def test_build_missing_fields():
    with pytest.raises(BrightDataConfigError):
        build_bright_data_proxy("", "zone", "pwd")
    with pytest.raises(BrightDataConfigError):
        build_bright_data_proxy("cust", "", "pwd")
    with pytest.raises(BrightDataConfigError):
        build_bright_data_proxy("cust", "zone", "")


# ---- parse_bright_data_uri ----

def test_parse_minimal_uri():
    p = parse_bright_data_uri("brd://C123:residential:secret")
    assert "brd-customer-C123-zone-residential:secret@" in p["http"]
    assert p["http"].endswith(f"@{BRD_DEFAULT_HOST}:{BRD_DEFAULT_PORT}")


def test_parse_with_country():
    p = parse_bright_data_uri("brd://C123:residential:secret;country=cn")
    assert "country-cn" in p["http"]


def test_parse_with_country_and_port():
    p = parse_bright_data_uri("brd://C123:residential:secret;country=us;port=22225")
    assert "country-us" in p["http"]
    assert p["http"].endswith(":22225")


def test_parse_with_session():
    p = parse_bright_data_uri("brd://C123:residential:secret;session=batch-42")
    assert "session-batch-42" in p["http"]


def test_parse_invalid_uri_prefix():
    with pytest.raises(BrightDataConfigError):
        parse_bright_data_uri("http://C123:residential:secret")


def test_parse_wrong_credential_segments():
    with pytest.raises(BrightDataConfigError):
        parse_bright_data_uri("brd://only:two")  # 缺 password


def test_parse_invalid_port():
    with pytest.raises(BrightDataConfigError):
        parse_bright_data_uri("brd://C:residential:secret;port=notanumber")


# ---- normalize_proxy ----

def test_normalize_brd_uri():
    p = normalize_proxy("brd://C123:residential:secret;country=cn")
    assert "country-cn" in p["http"]


def test_normalize_http_url():
    p = normalize_proxy("http://127.0.0.1:7890")
    assert p == {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}


def test_normalize_socks5():
    p = normalize_proxy("socks5://127.0.0.1:1080")
    assert p["http"] == "socks5://127.0.0.1:1080"
    assert p["https"] == "socks5://127.0.0.1:1080"