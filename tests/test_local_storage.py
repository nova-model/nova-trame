"""Unit tests for LocalStorageManager."""

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def test_local_storage(driver: Firefox) -> None:
    assert driver.execute_script("window.localStorage.getItem('local_storage_test');") is None

    text_field = driver.find_element(By.ID, "local-storage-input")
    text_field.clear()
    text_field.click()
    text_field.send_keys("1")
    driver.execute_script("window.document.getElementById('local-storage-set').click();")
    WebDriverWait(driver, 10).until(
        lambda *args: driver.execute_script("return window.localStorage.getItem('local_storage_test');") == "1"
    )

    driver.execute_script("window.document.getElementById('local-storage-remove').click();")
    assert driver.execute_script("window.localStorage.getItem('local_storage_test');") is None
