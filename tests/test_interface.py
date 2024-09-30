"""Test the UI via Selenium."""

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


def test_interface(driver: Firefox) -> None:
    title = driver.find_element(By.CLASS_NAME, "v-toolbar-title__placeholder").text
    assert title == "Widget Gallery"
