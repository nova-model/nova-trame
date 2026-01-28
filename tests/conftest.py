"""pytest Fixture for setting up the Selenium driver and the server."""

from functools import partial
from multiprocessing import Process
from time import sleep
from typing import Generator

from pytest import fixture
from selenium.webdriver import Firefox, FirefoxOptions

from tests.gallery import main


def _setup_selenium() -> Firefox:
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.add_argument("--height=20000")

    driver = Firefox(options=options)
    driver.get("http://localhost:8080")
    driver.implicitly_wait(10)

    return driver


@fixture(autouse=True, scope="session")
def driver() -> Generator[Firefox, None, None]:
    server_process = Process(target=partial(main, open_browser=False))
    server_process.start()

    # TODO: Surely there's a better way to wait for the server to start.
    sleep(1)

    yield _setup_selenium()

    server_process.terminate()
