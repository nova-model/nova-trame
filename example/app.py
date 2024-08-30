import json
import logging
from pathlib import Path

from trame.app import get_server
from trame.decorators import TrameApp
from trame.widgets import html, vuetify3 as vuetify

from trame_facade import ThemedApp
from trame_facade.components import EasyGrid, InputField

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@TrameApp()
class App(ThemedApp):
    def __init__(self, server=None):
        try:
            with open(Path(__file__).parent / "vuetify_config.json", "r") as _file:
                vuetify_config = json.load(_file)
                logger.warning(
                    "WARN: Gallery loaded a local Vuetify config. This is only provided as an example and should not be used in production."
                )
        except (FileNotFoundError, ValueError):
            vuetify_config = {}
        super().__init__(server=server, vuetify_config_overrides=vuetify_config)

        self.server = get_server(server, client_type="vue3")

        self.create_ui()

    @property
    def state(self):
        return self.server.state

    def test_callable_update(self, *args, **kwargs):
        assert args == ()
        assert kwargs == {}

    def test_callable_args_update(self, value, value2, **kwargs):
        assert value == "a"
        assert value2 == "b"
        assert kwargs == {}

    def test_callable_kwargs_update(self, value, value2, **kwargs):
        assert value == "a"
        assert value2 == "b"
        assert kwargs == {"test": "test"}

    def create_ui(self):
        self.state.facade__menu = True
        self.state.select1 = []
        self.state.select2 = []
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
                        vuetify.VCardTitle("Grid")
                        with EasyGrid(cols_per_row=2):
                            vuetify.VBtn(
                                "{{ item }} - {{ index }}",
                                v_for="(item, index) in ['a', 'b', 'c']",
                            )
                            vuetify.VBtn("d - 3")

                        vuetify.VCardTitle("Containment Components")
                        with EasyGrid(cols_per_row=3):
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

                        vuetify.VCardTitle("Navigation Components")
                        with EasyGrid(cols_per_row=1):
                            with vuetify.VTabs():
                                vuetify.VTab("Tab 1")
                                vuetify.VTab("Tab 2")
                                vuetify.VTab("Tab 3")

                        vuetify.VCardTitle("Form Inputs & Controls")
                        with EasyGrid(cols_per_row=3):
                            InputField(type="checkbox", label="Checkbox")
                            InputField(type="file", label="File Upload")
                            with InputField(type="radio"):
                                vuetify.VRadio(label="Radio 1", value="radio1")
                                vuetify.VRadio(label="Radio 2", value="radio2")
                            InputField(
                                type="select",
                                items="['Option 1', 'Option 2']",
                                label="Select",
                            )
                            InputField(type="slider", label="Slider")
                            InputField(type="switch", label="Switch")
                            InputField(type="textarea", label="Text Area")
                            InputField(label="Text Field")

                        vuetify.VCardTitle("Validation")
                        with vuetify.VForm():
                            with EasyGrid(cols_per_row=3):
                                InputField(label="Required Field", required=True)
                                InputField(
                                    label="Optional Field",
                                    update_modelValue=self.test_callable_update,
                                )
                                InputField(
                                    label="Text Only Optional Field",
                                    rules=(
                                        "[(value) => /[0-9]/.test(value) ? 'Field must not contain numbers' : true]",
                                    ),
                                    update_modelValue=(
                                        self.test_callable_args_update,
                                        "['a', 'b']",
                                    ),
                                )
                                InputField(
                                    ref="gallery_select",
                                    v_model="select1",
                                    type="select",
                                    items="['Option 1', 'Option 2']",
                                    label="Required Select",
                                    multiple=True,
                                    required=True,
                                    update_modelValue=(
                                        self.test_callable_kwargs_update,
                                        "['a', 'b']",
                                        "{ test: 'test' }",
                                    ),
                                )
                                InputField(
                                    v_model="select2",
                                    type="select",
                                    items="['Option 1', 'Option 2']",
                                    label="Cross-validated Select",
                                    multiple=True,
                                    required=True,
                                    rules=(
                                        "[(value) => value?.length === select1.length || 'Must have the same number of selections as the previous select']",
                                    ),
                                )

                        vuetify.VCardTitle("Feedback Components")
                        with EasyGrid(cols_per_row=3):
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
