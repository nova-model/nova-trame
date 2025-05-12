"""Unit tests for LocalStorageManager."""

from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By


def test_tool_components(driver: Firefox) -> None:
    run_button = driver.find_element(By.ID, "execution_test_run")
    cancel_button = driver.find_element(By.ID, "execution_test_cancel")
    progress_bar_running = driver.find_element(By.ID, "progress_bar_test_show_progress")
    progress_bar_finished = driver.find_element(By.ID, "progress_bar_test_show_ok")
    outputs = driver.find_element(By.ID, "tool_outputs_test_outputs")
    errors = driver.find_element(By.ID, "tool_outputs_test_errors")

    ActionChains(driver).click(run_button).pause(2).perform()
    # The progress bar should be visible and the output textareas should have content.
    running_style = progress_bar_running.get_attribute("style")
    assert running_style and "display: none;" not in running_style
    assert outputs.get_attribute("value") == "test_output"
    assert errors.get_attribute("value") == "test_error"

    ActionChains(driver).click(cancel_button).pause(2).perform()
    # The finished bar should be visible.
    running_style = progress_bar_running.get_attribute("style")
    assert running_style and "display: none;" in running_style
    finished_style = progress_bar_finished.get_attribute("style")
    assert finished_style and "display: none;" not in finished_style
