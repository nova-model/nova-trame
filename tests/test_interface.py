"""Test the UI via Selenium."""

from multiprocessing import Process
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

from tests.gallery import main


def _run_interface() -> None:
    main(open_browser=False)


def _setup_selenium() -> webdriver.Firefox:
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")

    driver = webdriver.Firefox(options=options)
    driver.get("http://localhost:8080")
    driver.implicitly_wait(10)

    return driver


def test_interface() -> None:
    server_process = Process(target=_run_interface)
    server_process.start()

    # TODO: Surely there's a better way to wait for the server to start.
    sleep(1)

    try:
        driver = _setup_selenium()
        title = driver.find_element(By.CLASS_NAME, "v-toolbar-title__placeholder").text
        assert title == "Widget Gallery"
    finally:
        server_process.terminate()
