import logging
from typing import Collection

import click

from .checker import check_urls

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@click.command()
@click.argument("urls", nargs=-1)
@click.option("--timeout", default=5, help="Timeout for HTTP requests in seconds.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
def main(urls: Collection[str], timeout: int, verbose: bool) -> None:
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    logger.debug(f"Received urls: {urls}")
    logger.debug(f"Received timeout: {timeout}")
    logger.debug(f"Received verbose: {verbose}")

    if not urls:
        logger.warning("No URLs provided. Please provide at least one URL to check.")
        click.echo(
            "Usage: check-urls <URL1> <URL2> ... [--timeout <seconds>] [--verbose]"
        )
        return

    logger.info(f"Checking {len(urls)} URLs with a timeout of {timeout} seconds.")

    result: dict[str, str] = check_urls(urls, timeout)

    for url, status in result.items():
        fg_color = "green" if "OK" in status else "red"
        click.secho(f"{url:<40} -> {status}", fg=fg_color)
