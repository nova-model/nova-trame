"""Unit tests for LocalStorageManager."""

from time import sleep

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_local_storage(driver: Firefox) -> None:
    assert driver.execute_script("window.localStorage.getItem('local_storage_test');") is None

    text_field = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#local-storage-input"))
    )
    text_field.send_keys("1")
    sleep(1)
    driver.execute_script("window.document.getElementById('local-storage-set').click();")
    WebDriverWait(driver, 10).until(
        lambda *args: driver.execute_script("return window.localStorage.getItem('local_storage_test');") == "1"
    )

    driver.execute_script("window.document.getElementById('local-storage-remove').click();")
    assert driver.execute_script("window.localStorage.getItem('local_storage_test');") is None
