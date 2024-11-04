"""Creates the UI for the widget gallery."""

import json
import logging
from asyncio import create_task
from pathlib import Path
from typing import cast

from altair import Chart, X, Y, selection_interval
from trame.app import get_server
from trame.decorators import TrameApp
from trame.widgets import client, html
from trame.widgets import vuetify3 as vuetify
from trame_client.widgets.core import AbstractElement
from trame_server.core import Server
from trame_server.state import State
from vega_datasets import data

from trame_facade import ThemedApp
from trame_facade.view.components import InputField, RemoteFileInput
from trame_facade.view.components.visualization import Interactive2DPlot
from trame_facade.view.layouts import GridLayout, HBoxLayout, VBoxLayout

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@TrameApp()
class App(ThemedApp):
    """Root Trame class for defining the UI."""

    def __init__(self, server: Server = None) -> None:
        """Constructor for the App class."""
        try:
            with open(Path(__file__).parent / "vuetify_config.json", "r") as _file:
                vuetify_config = json.load(_file)
                logger.warning(
                    "WARN: Gallery loaded a local Vuetify config. This is only provided as an example and should not "
                    "be used in production."
                )
        except (FileNotFoundError, ValueError):
            vuetify_config = {}
        super().__init__(server=server, vuetify_config_overrides=vuetify_config)

        self.server = get_server(server, client_type="vue3")

        self.create_state()
        self.create_ui()

    @property
    def state(self) -> State:
        return self.server.state

    def create_state(self) -> None:
        self.state.autoscroll = ""
        self.state.facade__menu = True
        self.state.local_storage_test = ""
        self.state.nested = {
            "selected_file": "",
        }
        self.state.select1 = []
        self.state.select2 = []
        self.state.selected_file = ""
        self.state.selected_folder = ""
        self.state.snackbar = True
        self.state.trame__title = "Widget Gallery"

    def create_ui(self) -> None:
        with super().create_ui() as layout:
            client.ClientTriggers(mounted=self.read_local_storage)

            layout.toolbar_title.set_text("Widget Gallery")

            # [slot child example]
            with layout.actions:
                vuetify.VBtn("Text Button")
            # [slot child example complete]

            with layout.pre_content:
                html.Div("Sticky Top Content", classes="text-center w-100")

            with layout.content:
                with vuetify.VCard(
                    classes="align-center d-flex flex-column text-center",
                    subtitle="This page is for visual testing of this theming package.",
                    title="Widget Gallery",
                ):
                    vuetify.VCardTitle("Layouts")
                    html.P("GridLayout")
                    # [ setup grid ]
                    with GridLayout(classes="mb-4", columns=2, halign="center", valign="center"):
                        vuetify.VBtn(
                            "{{ item }} - {{ index }}",
                            v_for="(item, index) in ['a', 'b', 'c', 'd']",
                        )
                    # [ setup grid complete ]
                    html.P("HBoxLayout")
                    # [ setup hbox ]
                    with HBoxLayout(classes="mb-4"):
                        vuetify.VBtn("Button 1")
                        vuetify.VBtn("Button 2")
                        vuetify.VBtn("Button 3")
                    # [ setup hbox complete ]
                    html.P("VBoxLayout")
                    # [ setup vbox ]
                    with VBoxLayout(classes="mb-4"):
                        vuetify.VBtn("Button 1")
                        vuetify.VBtn("Button 2")
                        vuetify.VBtn("Button 3")
                    # [ setup vbox complete ]

                    vuetify.VCardTitle("Advanced Layouts")
                    with html.Div(classes="text-left"):
                        # [ grid row and column span example ]
                        html.P("Grid cells can span multiple rows and/or columns.", classes="text-center")
                        with GridLayout(columns=3, height=400, halign="center", valign="center"):
                            # The classes parameter is used to highlight the different cells for demonstration purposes.
                            vuetify.VLabel("Item 1", classes="bg-primary h-100 w-100 justify-center")
                            vuetify.VLabel("Item 2", classes="bg-secondary h-100 w-100 justify-center")
                            vuetify.VLabel("Row Span", classes="bg-primary h-100 w-100 justify-center", row_span=2)
                            vuetify.VLabel("Column Span", classes="bg-error h-100 w-100 justify-center", column_span=2)
                            vuetify.VLabel(
                                "Row and Column Span",
                                classes="bg-secondary h-100 w-100 justify-center",
                                row_span=2,
                                column_span=3,
                            )
                        # [ grid row and column span example end ]

                        # [ whitespace example ]
                        html.P("Grid cells can be left blank.", classes="text-center")
                        with GridLayout(columns=3):
                            vuetify.VSheet()
                            InputField(label="Input 1")
                            vuetify.VSheet()
                            InputField(label="Input 2")
                            vuetify.VSheet()
                            InputField(label="Input 3")
                        # [ whitespace example end ]

                        # [ mixed boxes example 1 ]
                        html.P(
                            "HBoxLayout can contain VBoxLayouts.",
                            classes="text-center",
                        )
                        with HBoxLayout():
                            with VBoxLayout(classes="bg-primary pa-2"):
                                vuetify.VLabel("VBoxLayout 1 - Item 1", classes="mb-4")
                                vuetify.VLabel("VBoxLayout 1 - Item 2")
                            with VBoxLayout(classes="bg-secondary pa-2", halign="center", width=600):
                                vuetify.VLabel("VBoxLayout 2 - Item 1", classes="mb-4")
                                vuetify.VLabel("VBoxLayout 2 - Item 2")
                        # [ mixed boxes example 1 end ]

                        # [ mixed boxes example 2 ]
                        html.P(
                            "VBoxLayout can contain HBoxLayouts.",
                            classes="text-center",
                        )
                        with VBoxLayout():
                            with HBoxLayout(classes="bg-primary", halign="space-around"):
                                vuetify.VLabel("HBoxLayout 1 - Item 1")
                                vuetify.VLabel("HBoxLayout 1 - Item 2")
                                vuetify.VLabel("HBoxLayout 1 - Item 3")
                            with HBoxLayout(classes="bg-secondary", halign="space-around"):
                                vuetify.VLabel("HBoxLayout 2 - Item 1")
                                vuetify.VLabel("HBoxLayout 2 - Item 2")
                                vuetify.VLabel("HBoxLayout 2 - Item 3")
                        # [ mixed boxes example 2 end ]

                        # [ mixed boxes example 3 ]
                        html.P("GridLayout can also contain HBoxLayouts and VBoxLayouts.", classes="text-center")
                        with GridLayout(columns=10):
                            with HBoxLayout(classes="bg-primary", column_span=7, halign="space-around"):
                                vuetify.VLabel("HBoxLayout Item 1")
                                vuetify.VLabel("HBoxLayout Item 2")
                            with VBoxLayout(classes="bg-secondary", column_span=3, halign="center"):
                                vuetify.VLabel("VBoxLayout Item 1")
                                vuetify.VLabel("VBoxLayout Item 2")
                        # [ mixed boxes example 3 end ]

                    vuetify.VCardTitle("Containment Components")
                    with GridLayout(columns=3, halign="center", valign="center"):
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
                            vuetify.VExpansionPanel(text="Lorem Ipsum", title="Expansion Panel")
                        with vuetify.VList():
                            vuetify.VListItem(subtitle="Lorem Ipsum", title="List Item 1")
                            vuetify.VListItem(subtitle="Lorem Ipsum", title="List Item 2")
                            with vuetify.VListItem(subtitle="Lorem Ipsum", title="List Item 3"):
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
                    with GridLayout(classes="mb-4", columns=1, halign="center", valign="center"):
                        with vuetify.VTabs():
                            vuetify.VTab("Tab 1")
                            vuetify.VTab("Tab 2")
                            vuetify.VTab("Tab 3")

                    vuetify.VCardTitle("Form Inputs & Controls")
                    with GridLayout(columns=3, valign="center"):
                        with html.Div():
                            InputField(
                                v_model="autoscroll",
                                auto_grow=True,
                                classes="mb-2",
                                label="Autoscroll Text Area",
                                max_rows=5,
                                rows=1,
                                type="autoscroll",
                            )
                            vuetify.VBtn("Add Line to Autoscroller", click=self.append_to_autoscroll)
                        InputField(type="checkbox", label="Checkbox")
                        InputField(type="file", label="File Upload")
                        with cast(AbstractElement, InputField(type="radio")):
                            vuetify.VRadio(label="Radio 1", value="radio1")
                            vuetify.VRadio(label="Radio 2", value="radio2")
                        InputField(
                            type="select",
                            items="['Option 1', 'Option 2']",
                            label="Select",
                        )
                        InputField(type="slider", label="Slider")
                        InputField(type="switch", label="Switch")
                        InputField(type="textarea", auto_grow=True, label="Text Area")
                        InputField(label="Text Field")
                        RemoteFileInput(
                            v_model="selected_file",
                            base_paths=["/run"],
                            extensions=[".pid", ".lock"],
                            label="File Selector",
                        )
                        RemoteFileInput(
                            v_model="selected_folder",
                            allow_files=False,
                            allow_folders=True,
                            base_paths=["/usr"],
                            label="Folder Selector",
                        )
                        RemoteFileInput(
                            v_model="nested.selected_file",
                            base_paths=["/run"],
                            label="Nested v_model File Selector",
                        )

                    vuetify.VCardTitle("Validation")
                    with vuetify.VForm():
                        with GridLayout(classes="mb-4", columns=3, width=600, valign="center"):
                            InputField(label="Required Field", required=True)
                            InputField(label="Optional Field")
                            InputField(
                                label="Text Only Optional Field",
                                rules=("[(value) => /[0-9]/.test(value) ? 'Field must not contain numbers' : true]",),
                            )
                            InputField(
                                ref="gallery_select",
                                v_model="select1",
                                type="select",
                                items="['Option 1', 'Option 2']",
                                label="Required Select",
                                multiple=True,
                                required=True,
                            )
                            InputField(
                                v_model="select2",
                                type="select",
                                items="['Option 1', 'Option 2']",
                                label="Cross-validated Select",
                                multiple=True,
                                required=True,
                                rules=(
                                    (
                                        "[(value) => value?.length === select1.length || 'Must have the same "
                                        "number of selections as the previous select']"
                                    ),
                                ),
                            )

                    vuetify.VCardTitle("Feedback Components")
                    with GridLayout(columns=3, halign="center", valign="center"):
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

                    vuetify.VCardTitle("Visualization Components")
                    self.plot = Interactive2DPlot(
                        figure=self.create_test_2d_plot(),
                        id="interactive-plot",
                        __events=["pointerup"],
                        pointerup=self.read_plot_signal,
                    )
                    html.P(f"Selected interval: {{{{ {self.plot.ref}['interval'] }}}}")

                    vuetify.VCardTitle("Local Storage")
                    with html.Div():
                        vuetify.VTextField(
                            v_model="local_storage_test",
                            classes="mb-2 mt-0 mx-auto",
                            id="local-storage-input",
                            label="Local Storage Test",
                            width=400,
                        )
                        vuetify.VBtn(
                            "Save to LocalStorage", classes="mr-2", id="local-storage-set", click=self.set_local_storage
                        )
                        vuetify.VBtn("Clear LocalStorage", id="local-storage-remove", click=self.remove_local_storage)

            with layout.post_content:
                html.Div("Sticky Bottom Content", classes="text-center w-100")

            return layout

    def create_test_2d_plot(self) -> Chart:
        brush = selection_interval(encodings=["x"], name="interval", zoom=False)

        return (
            Chart(data.cars(), title="Interactive 2D Plot")
            .mark_circle()
            .encode(
                X("Horsepower", type="quantitative"),
                Y("Miles_per_Gallon", type="quantitative"),
                color="Origin:N",
            )
            .properties(height=400, width=1000)
            .add_params(brush)
        )

    def read_plot_signal(self) -> None:
        logger.info(f"Interval signal state: {self.plot.get_signal_state('interval')}")

    async def _read_local_storage(self) -> None:
        if self.local_storage:
            with self.state:
                self.state.local_storage_test = await self.local_storage.get("local_storage_test")

    def read_local_storage(self) -> None:
        create_task(self._read_local_storage())

    def remove_local_storage(self) -> None:
        if self.local_storage:
            self.local_storage.remove("local_storage_test")

    def set_local_storage(self) -> None:
        if self.local_storage:
            self.local_storage.set("local_storage_test", self.state.local_storage_test)

    def append_to_autoscroll(self) -> None:
        self.state.autoscroll += "Line added by button\n"
