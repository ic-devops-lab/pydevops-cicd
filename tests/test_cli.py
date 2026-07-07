import logging

from click.testing import CliRunner
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture

from simple_http_checker.cli import main


def test_main_no_urls() -> None:
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code == 0
    assert "Usage: check-urls" in result.output


def test_main_single_url(mocker: MockerFixture) -> None:
    url = "https://www.example.com"
    status = "200 OK"

    mock_check = mocker.patch("simple_http_checker.cli.check_urls")
    mock_check.return_value = {url: status}

    runner = CliRunner()
    result = runner.invoke(main, [url])

    assert result.exit_code == 0
    mock_check.assert_called_once_with((url,), 5)

    assert "--- Results ---" in result.output
    assert f"{url}" in result.output
    assert f"-> {status}" in result.output


def test_main_timeout_option(mocker: MockerFixture) -> None:
    url = "https://www.timeout.com"
    status = "TIMEOUT"
    timeout = 10

    mock_check = mocker.patch("simple_http_checker.cli.check_urls")
    mock_check.return_value = {url: status}

    runner = CliRunner()
    result = runner.invoke(main, [url, "--timeout", str(timeout)])

    assert result.exit_code == 0
    mock_check.assert_called_once_with((url,), timeout)

    assert "--- Results ---" in result.output
    assert f"{url}" in result.output
    assert f"-> {status}" in result.output


def test_main_verbose_option(mocker: MockerFixture, caplog: LogCaptureFixture) -> None:
    url = "https://www.example.com"
    status = "200 OK"

    mock_check = mocker.patch("simple_http_checker.cli.check_urls")
    mock_check.return_value = {url: status}

    caplog.set_level(logging.DEBUG, logger="simple_http_checker.cli")

    runner = CliRunner()
    result = runner.invoke(main, [url, "--verbose"])

    assert result.exit_code == 0
    mock_check.assert_called_once_with((url,), 5)

    assert "Verbose mode enabled." in caplog.text
    assert "Received urls:" in caplog.text
    assert "Received timeout:" in caplog.text
    assert "Received verbose: True" in caplog.text
    assert "Checking 1 URL(s) with a timeout of 5 seconds." in caplog.text

    assert "--- Results ---" in result.output
    assert f"{url}" in result.output
    assert f"-> {status}" in result.output


def test_main_verbose_option_short(
    mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    url = "https://www.example.com"
    status = "200 OK"

    mock_check = mocker.patch("simple_http_checker.cli.check_urls")
    mock_check.return_value = {url: status}

    caplog.set_level(logging.DEBUG, logger="simple_http_checker.cli")

    runner = CliRunner()
    result = runner.invoke(main, [url, "-v"])

    assert result.exit_code == 0
    mock_check.assert_called_once_with((url,), 5)

    assert "Verbose mode enabled." in caplog.text
    assert "Received urls:" in caplog.text
    assert "Received timeout:" in caplog.text
    assert "Received verbose: True" in caplog.text
    assert "Checking 1 URL(s) with a timeout of 5 seconds." in caplog.text

    assert "--- Results ---" in result.output
    assert f"{url}" in result.output
    assert f"-> {status}" in result.output
