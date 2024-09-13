# Overview
`trame-facade` is a Python package for styling Trame applications used in the [NDIP](https://code.ornl.gov/ndip) project.

# Requirements
* [Python 3.10](https://www.python.org/)
* [Trame](https://kitware.github.io/trame/)

# Installation
You can install this package directly with

    pip install --index-url https://code.ornl.gov/api/v4/projects/16294/packages/pypi/simple trame-facade

or with [Poetry](https://python-poetry.org/) by placing the following in your `pyproject.toml` (you can version lock with typical [Semantic Versioning](https://semver.org/) syntax)

    [tool.poetry.dependencies]
    trame-facade = "*"

    [[tool.poetry.source]]
    name = "trame-facade"
    url = "https://code.ornl.gov/api/v4/projects/16294/packages/pypi/simple"
    priority = "primary"

# Usage
The following code snippet is the bare minimum to import and use this package.
This will default to using our ModernTheme.

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

# Convenience Components

### Grids
To help with generating even-width [Vuetify Grids](https://vuetifyjs.com/en/components/grids/#usage), we provide a convenience component
that can be used as follows (example creates a 3-column grid):

    from trame_facade.components import EasyGrid


    # Rest of your code to create a Trame layout

    with layout.content:
        with EasyGrid(cols_per_row=3):
            vuetify.VBtn("Button 1")
            vuetify.VBtn("Button 2")
            vuetify.VBtn("Button 3")

`cols_per_row` will determine the "width" of the grid, so `cols_per_row=2` will create a 2-column grid. Please note that
Vuetify grids are 12-point grids. This means that you cannot create a grid with more than 12 columns, and you generally
shouldn't create an n-grid column where 12 isn't divisible by n. If you need to do this, you will need to build your
VRow/VCol components manually.

If you need to manually specify the column width of a child, you can do so by applying the typical Vuetify column width
fields on it (cols, lg, md, sm, etc.).

### Inputs
To help with generating inputs for [Vuetify Forms](https://vuetifyjs.com/en/components/forms/#usage), we provide a convenience component
that can be used as follows (example creates a VSelect input):

    from trame_facade.components import InputField


    with layout.content:
        InputField(items=("['Option 1', 'Option 2']",), required=True, type="select")

The following types are available: `autocomplete`, `checkbox`, `combobox`, `file`, `input`, `otp`, `radio`, `range-slider`, `select`,
`slider`, `switch`, and `textarea`. Any other provided type will produce a VTextField and type will be passed as an
[HTML input type](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#input_types).

`InputField` will automatically update an input's label and rules list if marked as required.

`InputField` also automatically supports cross-field validation.

# Themes
The following themes are currently available:
1. ModernTheme - The recommended theme for most applications. Leverages ORNL brand colors and a typical Vuetify appearance.
2. TechnicalTheme - This loosely mimics an older QT Fusion theme. Use at your own peril.

### Choosing a default theme
After calling `ThemedApp.create_ui()`, you can choose the initial theme for your application with:

    self.set_theme('ModernTheme')

### Allowing user theme selection
If you want to allow the user to choose between any of the existing themes in this package, then
you can add a theme selection menu to the top right of your page with the following code after calling
`ThemedApp.__init__()`:

    self.server.state.facade__menu = True

Note that if you are using [py-mvvm](https://code.ornl.gov/ndip/public-packages/py-mvvm) then you may want
to use that library to set this state variable for consistency.

# Customization
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

# Example Application
This package includes an example Trame application that shows commonly used Vuetify components for visual testing of our themes.

You can run it via:

    poetry install
    poetry run start [--server]

# Development
Please use [Black](https://github.com/psf/black) to format code being worked on in this repository.

### PyPI
If you are making a change to this repository, then please use the following process:

1. Make your changes.
2. Update the package version in pyproject.toml using [Semantic Versioning](https://semver.org/) and your best judgement.
3. Append "-dev.X" to the version number in pyproject.toml, where X is the build version you want to test.
4. Open a merge request and run the package-build pipeline to send your build to PyPI.
5. Use the PyPI build to test your changes.
6. Once your changes are approved, remove "-dev.X" from pyproject.toml.
7. Merge your changes and run the package-build pipeline to send a production build to PyPI.
