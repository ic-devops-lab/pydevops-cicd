from typing import Collection

import pytest
from pytest_mock import MockerFixture
import requests

from simple_http_checker.checker import check_urls


def test_check_urls_success(mocker: MockerFixture) -> None:
    # Mock the requests.get method to simulate a successful response
    expected_status_code = 200
    urls: Collection[str] = ["http:/example.com"]
    response_ok = True
    response_reason = "OK"

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.ok = response_ok
    mock_response.status_code = expected_status_code
    mock_response.reason = response_reason

    mock_get = mocker.patch("simple_http_checker.checker.requests.get")
    mock_get.return_value = mock_response

    result = check_urls(urls)

    mock_get.assert_called_once_with(urls[0], timeout=5)
    assert result == {"http:/example.com": f"{expected_status_code} {response_reason}"}


def test_check_urls_client_error(mocker: MockerFixture) -> None:
    # Mock the requests.get method to simulate a client error response
    expected_status_code = 404
    urls: Collection[str] = ["http:/example.com"]
    response_ok = False
    response_reason = "Not Found"

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.ok = response_ok
    mock_response.status_code = expected_status_code
    mock_response.reason = response_reason

    mock_get = mocker.patch("simple_http_checker.checker.requests.get")
    mock_get.return_value = mock_response

    result = check_urls(urls)

    mock_get.assert_called_once_with(urls[0], timeout=5)
    assert result == {"http:/example.com": f"{expected_status_code} {response_reason}"}


@pytest.mark.parametrize(
    "error_exception, expected_status",
    [
        pytest.param(requests.exceptions.Timeout, "TIMEOUT", id="timeout"),
        pytest.param(
            requests.exceptions.ConnectionError,
            "CONNECTION_ERROR",
            id="connection_error",
        ),
        pytest.param(
            requests.exceptions.RequestException,
            "REQUEST_ERROR: RequestException",
            id="request_error",
        ),
    ],
)
def test_check_urls_exceptions(
    mocker: MockerFixture,
    error_exception: type[requests.RequestException],
    expected_status: str,
) -> None:
    urls: Collection[str] = ["http:/example.com"]

    mock_get = mocker.patch("simple_http_checker.checker.requests.get")
    mock_get.side_effect = error_exception(f"Simulated {expected_status}")

    result = check_urls(urls)

    mock_get.assert_called_once_with(urls[0], timeout=5)
    assert result == {"http:/example.com": expected_status}


def test_check_urls_multiple_urls(mocker: MockerFixture) -> None:
    test_data: dict[
        str, tuple[bool | type[requests.RequestException], int | None, str | None, str]
    ] = {
        "http:/success.com": (True, 200, "OK", "200 OK"),
        "http:/servererror.org": (
            False,
            503,
            "Service Unavailable",
            "503 Service Unavailable",
        ),
        "http:/timeout.net": (requests.exceptions.Timeout, None, None, "TIMEOUT"),
    }
    urls: Collection[str] = test_data.keys()

    mock_get = mocker.patch("simple_http_checker.checker.requests.get")

    get_side_effect: list[requests.Response | requests.RequestException] = []
    for _url, (ok, status_code, reason, expected_status) in test_data.items():
        if isinstance(ok, bool):
            mock_response = mocker.MagicMock(spec=requests.Response)
            mock_response.ok = ok
            mock_response.status_code = status_code
            mock_response.reason = reason
            get_side_effect.append(mock_response)
        else:
            get_side_effect.append(ok(f"Simulated {expected_status}"))

    mock_get.side_effect = get_side_effect

    result = check_urls(urls)

    assert len(result) == len(test_data)
    assert mock_get.call_count == len(test_data)

    for url in urls:
        mock_get.assert_any_call(url, timeout=5)
        assert result[url] == test_data[url][3]


def test_check_urls_empty_list() -> None:
    urls: Collection[str] = []

    result = check_urls(urls)

    assert result == {}


def test_check_urls_custom_timeout(mocker: MockerFixture) -> None:
    # Mock the requests.get method to simulate a successful response
    expected_status_code = 200
    urls = ["http:/example.com"]
    response_ok = True
    response_reason = "OK"
    timeout = 10

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.ok = response_ok
    mock_response.status_code = expected_status_code
    mock_response.reason = response_reason

    mock_get = mocker.patch("simple_http_checker.checker.requests.get")
    mock_get.return_value = mock_response

    result = check_urls(urls, timeout=timeout)

    mock_get.assert_called_once_with(urls[0], timeout=timeout)
    assert result == {"http:/example.com": f"{expected_status_code} {response_reason}"}
