from trame.app import get_server
from trame.decorators import TrameApp
from trame.widgets import html, vuetify3 as vuetify

from trame_facade import ThemedApp
from trame_facade.components import EasyGrid


@TrameApp()
class App(ThemedApp):
    def __init__(self, server=None):
        super().__init__(server=server)

        self.server = get_server(server, client_type="vue3")

        self.create_ui()

    @property
    def state(self):
        return self.server.state

    def create_ui(self):
        self.state.facade__menu = True
        self.state.snackbar = True
        self.state.trame__title = "Widget Gallery"

        with super().create_ui() as layout:
            # self.set_theme("TechnicalTheme")  # sets the default theme, must not call before layout exists
            layout.toolbar_title.set_text("Widget Gallery")

            with layout.actions:
                vuetify.VBtn("Text Button")

            with layout.content:
                with vuetify.VSheet(
                    classes="align-center bg-background d-flex flex-column"
                ):
                    with vuetify.VCard(
                        classes="mt-16 text-center",
                        subtitle="This page is for visual testing of this theming package.",
                        title="Widget Gallery",
                        width=800,
                    ):
                        with EasyGrid(cols_per_row=3):
                            # Grid
                            with html.Div():
                                html.Span("Grid", classes="text-center")
                                with EasyGrid(cols_per_row=2):
                                    vuetify.VBtn(
                                        "{{ item }} - {{ index }}",
                                        v_for="(item, index) in ['a', 'b', 'c']",
                                    )
                                    vuetify.VBtn("d - 3")

                            # Containment
                            vuetify.VBtn(
                                "Elevated Button",
                            )
                            vuetify.VBtn(
                                icon="mdi-ab-testing",
                            )
                            vuetify.VBtn(
                                "Text Button",
                                variant="text",
                            )
                            with vuetify.VBtnToggle():
                                vuetify.VBtn("Button 1")
                                vuetify.VBtn("Button 2")
                            vuetify.VChip("Chip")
                            with vuetify.VDialog(max_width=500):
                                with vuetify.Template(v_slot_activator="{ props }"):
                                    vuetify.VBtn("Open Dialog", v_bind="props")
                                with vuetify.Template(v_slot_default=True):
                                    vuetify.VCard(title="Dialog")
                            with html.Div():
                                html.Span("Divider")
                                vuetify.VDivider()
                            with vuetify.VExpansionPanels():
                                vuetify.VExpansionPanel(
                                    text="Lorem Ipsum", title="Expansion Panel"
                                )
                            with vuetify.VList():
                                vuetify.VListItem(
                                    subtitle="Lorem Ipsum", title="List Item 1"
                                )
                                vuetify.VListItem(
                                    subtitle="Lorem Ipsum", title="List Item 2"
                                )
                                with vuetify.VListItem(
                                    subtitle="Lorem Ipsum", title="List Item 3"
                                ):
                                    vuetify.VBtn("Button", classes="mt-2")
                            with vuetify.VMenu():
                                with vuetify.Template(v_slot_activator="{ props }"):
                                    vuetify.VBtn("Open Menu", v_bind="props")
                                with vuetify.VList():
                                    vuetify.VListItem("Menu Item")
                            with vuetify.VTooltip(text="Tooltip"):
                                with vuetify.Template(v_slot_activator="{ props }"):
                                    vuetify.VBtn("Tooltip", v_bind="props")

                            # Navigation
                            with vuetify.VTabs():
                                vuetify.VTab("Tab 1")
                                vuetify.VTab("Tab 2")
                                vuetify.VTab("Tab 3")

                            # Form Inputs & Controls
                            vuetify.VCheckbox(label="Checkbox")
                            vuetify.VFileInput(label="File Upload")
                            with vuetify.VRadioGroup():
                                vuetify.VRadio(label="Radio 1", value="radio1")
                                vuetify.VRadio(label="Radio 2", value="radio2")
                            vuetify.VSelect(
                                items=("['Option 1', 'Option 2']",), label="Select"
                            )
                            vuetify.VSlider(label="Slider")
                            vuetify.VSwitch(label="Switch")
                            vuetify.VTextField(label="Text Field")
                            vuetify.VTextarea(label="Text Area")

                            # Feedback
                            vuetify.VAlert("Alert")
                            with vuetify.VBadge():
                                vuetify.VIcon("mdi-ab-testing")
                            vuetify.VProgressCircular(indeterminate=True)
                            vuetify.VProgressLinear(indeterminate=True)
                            with vuetify.VSnackbar(
                                "Snackbar",
                                v_model="snackbar",
                                timeout=-1,
                            ):
                                with vuetify.Template(v_slot_actions=True):
                                    vuetify.VBtn("Close", click="snackbar = false")

            return layout
