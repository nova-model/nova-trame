# Introduction
`trame-facade` is a Python package for styling Trame applications used in the [NDIP](https://code.ornl.gov/ndip) project.

## Installation
You can install this package directly with

```commandline
pip install --index-url https://code.ornl.gov/api/v4/projects/16294/packages/pypi/simple trame-facade
```

or with [Poetry](https://python-poetry.org/) by placing the following in your `pyproject.toml` (you can version lock with typical [Semantic Versioning](https://semver.org/) syntax)

```
[tool.poetry.dependencies]
trame-facade = "*"

[[tool.poetry.source]]
name = "trame-facade"
url = "https://code.ornl.gov/api/v4/projects/16294/packages/pypi/simple"
priority = "primary"
```

## Usage
The following code snippet is the bare minimum to import and use this package.
This will default to using our ModernTheme.

```python
from trame_facade import ThemedApp


class MyApp(ThemedApp):
    def __init__(self, server=None):
        super().__init__(server=server)

        # Do any initialization you need to here

        self.create_ui()

    def create_ui(self):
        with super().create_ui() as layout:
            with layout.pre_content:
                # Add sticky-positioned elements before v-main

            with layout.content:
                # Add contents to the v-main block

            with layout.post_content:
                # Add sticky-positioned elements after v-main
```

## Convenience Components

### Grids
To help with generating even-width [Vuetify Grids](https://vuetifyjs.com/en/components/grids/#usage), we provide a convenience component
that can be used as follows (example creates a 3-column grid):

```python
from trame_facade.components import EasyGrid


# Rest of your code to create a Trame layout

with layout.content:
    with EasyGrid(cols_per_row=3):
        vuetify.VBtn("Button 1")
        vuetify.VBtn("Button 2")
        vuetify.VBtn("Button 3")
```

`cols_per_row` will determine the "width" of the grid, so `cols_per_row=2` will create a 2-column grid. Please note that
Vuetify grids are 12-point grids. This means that you cannot create a grid with more than 12 columns, and you generally
shouldn't create an n-grid column where 12 isn't divisible by n. If you need to do this, you will need to build your
VRow/VCol components manually.

If you need to manually specify the column width of a child, you can do so by applying the typical Vuetify column width
fields on it (cols, lg, md, sm, etc.).

### Inputs
To help with generating inputs for [Vuetify Forms](https://vuetifyjs.com/en/components/forms/#usage), we provide a convenience component
that can be used as follows (example creates a VSelect input):

```python
from trame_facade.components import InputField


with layout.content:
    InputField(items=("['Option 1', 'Option 2']",), required=True, type="select")
```

The following types are available: `autocomplete`, `checkbox`, `combobox`, `file`, `input`, `otp`, `radio`, `range-slider`, `select`,
`slider`, `switch`, and `textarea`. Any other provided type will produce a VTextField and type will be passed as an
[HTML input type](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#input_types).

`InputField` will automatically update an input's label and rules list if marked as required.

`InputField` also automatically supports cross-field validation.

### Remote File Selector
`RemoteFileInput` can be used to select files from HFIR/SNS as follows:

    from trame_components import RemoteFileInput


    with layout.content:
        RemoteFileInput(
            v_model="state_name",
            allow_files=True,
            allow_nonexistent_path=False,
            base_paths=["/HFIR", "/SNS"],
            extensions=[".txt"],
            label="File Selector",
        )

Additionally, you can pass dictionaries to `dialog_props` and `input_props` to set Vuetify attributes directly on the dialog (eg setting a width) and the text field, respectively.

Note that all directories and files (if `allow_files` is True) in the provided `base_paths` will be visible to the user. Please use this carefully.

## Visualization

### Interactive 2D Plotting
Trame provides two primary mechanisms for composing 2D plots: [Plotly](https://github.com/Kitware/trame-plotly) and [Vega-Lite](https://github.com/Kitware/trame-vega)/[Altair](https://altair-viz.github.io/index.html). If you only need static plots or basic browser event handling, then please use these libraries directly.

If you need to capture complex front-end interactions, then you can use our provided `Interactive2DPlot` widget that is based on Vega-Lite. This uses the same API as Trame's `vega.Figure`, except that it will automatically sync Vega's signal states as the user interacts with the plot.

The following allows the user to select a region of the plot, and then prints that region out in the Trame application:

```python
selector = altair.selection_interval(name="selector")
my_plot = Interactive2DPlot(
    figure=altair.Chart(my_data, title="My Interactive Chart").add_params(selector)
)

my_plot.get_signal_state("selector")  # Will show the currently selected region of the plot
```

## Themes
The following themes are currently available:
1. ModernTheme - The recommended theme for most applications. Leverages ORNL brand colors and a typical Vuetify appearance.
2. TechnicalTheme - This loosely mimics an older QT Fusion theme. Use at your own peril.

### Choosing a default theme
After calling `ThemedApp.create_ui()`, you can choose the initial theme for your application with:

```python
self.set_theme('ModernTheme')
```

### Allowing user theme selection
If you want to allow the user to choose between any of the existing themes in this package, then
you can add a theme selection menu to the top right of your page with the following code after calling
`ThemedApp.__init__()`:

```python
self.server.state.facade__menu = True
```

Note that if you are using [py-mvvm](https://code.ornl.gov/ndip/public-packages/py-mvvm) then you may want
to use that library to set this state variable for consistency.

## Customization
If you want more control than selecting one of the pre-built themes, then you can provide your own
[Vuetify Configuration](https://vuetifyjs.com/en/features/global-configuration/) where you can define your
own themes or override the component defaults this package provides. You can pass a Python dictionary via
`ThemedApp.__init__(vuetify_config_overrides=YOUR_CONFIG)`. This config can be defined in a JSON file and
loaded with `json.load` or you can just define it directly in code.

### Color shortcuts
If you just want to set your color palette without providing a full Vuetify configuration, then there are three
shortcut keys you can put in your Vuetify configuration to set the color palette used by our `ModernTheme`:

```json
{
    "primary": "#f00",
    "secondary": "#0f0",
    "accent": "#00f",
}
```

## Utilities
This package also provides some general utilities for developing Trame applications.

### Local Storage
If you need to manipulate `window.localStorage` to track state across user sessions, then you can do so with the following methods:

```python
from asyncio import create_task

from trame_facade import ThemedApp


class MyApp(ThemedApp):
    # The rest of your application definition here

    def remove_local_storage(self):
        self.local_storage.remove("test")

    def set_local_storage(self):
        self.local_storage.set("test", "value")

    async def _get_local_storage(self):
        result = await self.local_storage.get("test")
        # Do something with result

    def get_local_storage(self):
        create_task(_get_local_storage())
```

Interactions with `window.localStorage` are asynchronous because the server must transmit your request to the browser which then executes it asynchronously. `local_storage.remove` and `local_storage.set` don't return a value, so no special consideration is needed. `local_storage.get` does return a value, however, so you'll need to use `await` to get the return value. When the browser is done reading `window.localStorage`, the response it gives to Trame is processed by the main Trame coroutine. This means that you cannot call await in the main Trame coroutine, as that would result in deadlock. This is handled in the above example with `asyncio.create_task`.

## Example Application
This package includes an example Trame application that shows commonly used Vuetify components for visual testing of our themes.

You can run it via:
```commandline
poetry install
poetry run start [--server]
```

## Formatting
```commandline
poetry run ruff format
```

## Linting
```commandline
poetry run ruff check
poetry run mypy .
```

## Testing
You will need a working [Firefox](https://www.mozilla.org/en-US/firefox/) install available in order to run all tests [Selenium](https://www.selenium.dev/).
Otherwise, all Selenium-based tests will fail.

```commandline
poetry run pytest
```
or, with coverage
```commandline
poetry run coverage run
poetry run coverage report
```
