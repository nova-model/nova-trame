"""Unit tests for Interactive2DPlot."""

from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By

from nova.trame.view.components.visualization import Interactive2DPlot


def test_interactive_2d_plot() -> None:
    # [setup 2d plot]
    from altair import Chart, selection_interval
    from vega_datasets import data

    brush = selection_interval(name="brush")
    chart = (
        Chart(data.cars())
        .mark_circle()
        .encode(x="Horsepower:Q", y="Miles_per_Gallon:Q", color="Origin:N")
        .add_params(brush)
    )
    plot = Interactive2DPlot(figure=chart)
    # [setup 2d plot complete]
    assert plot._figure == chart


def test_missing_figure() -> None:
    plot = Interactive2DPlot()
    assert plot._figure is None


def test_state_synchronization(driver: Firefox) -> None:
    plot = driver.find_element(By.ID, "interactive-plot")
    ActionChains(driver).drag_and_drop_by_offset(plot, 10, 5).perform()

    # Look for the interval in the state. I want to avoid using the exact ref since it's pseudo-random
    # (e.g. nova__vega_203) here.
    trame_state = driver.execute_script("return window.trame.state.state")
    for key, value in trame_state.items():
        if isinstance(value, dict):
            for sub_key in value:
                if sub_key == "interval" and key.startswith("nova__vega"):
                    interval = value[sub_key]

    # We could check exact values, but that seems more sensitive to changes in the gallery.
    assert "Horsepower" in interval and isinstance(interval["Horsepower"], list)
