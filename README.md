# Installation
TODO

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
                # Add your content here

### Using convenience components
TODO

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

# Example Application
This package includes an example Trame application that shows commonly used Vuetify components for visual testing of our themes.

You can run it via:

    poetry install
    poetry run start [--server]
