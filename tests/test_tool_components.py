"""Unit tests for LocalStorageManager."""

from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def test_tool_components(driver: Firefox) -> None:
    wait = WebDriverWait(driver, timeout=10)
    run_button = driver.find_element(By.ID, "execution_test_run")
    cancel_button = driver.find_element(By.ID, "execution_test_cancel")

    ActionChains(driver).click(run_button).perform()
    # The progress bar should be visible and the output textareas should have content.
    wait.until(expected_conditions.visibility_of_element_located((By.ID, "progress_bar_test_show_progress")))
    assert driver.find_element(By.ID, "tool_outputs_test_outputs").get_attribute("value") == "test_output"
    assert driver.find_element(By.ID, "tool_outputs_test_errors").get_attribute("value") == "test_error"

    ActionChains(driver).click(cancel_button).perform()
    # The finished bar should be visible.
    wait.until(expected_conditions.visibility_of_element_located((By.ID, "progress_bar_test_show_ok")))
