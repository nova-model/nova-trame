"""Creates the UI for the widget gallery."""

import json
import logging
from asyncio import create_task
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import blinker
import numpy as np
from altair import Chart, X, Y, selection_interval
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pydantic import BaseModel, Field, field_validator
from trame.app import get_server
from trame.decorators import TrameApp
from trame.widgets import client, html
from trame.widgets import vuetify3 as vuetify
from trame_server.core import Server
from trame_server.state import State
from vega_datasets import data

from nova.common.job import ToolOutputs, WorkState
from nova.common.signals import Signal, ToolCommand, get_signal_id
from nova.mvvm.trame_binding import TrameBinding
from nova.trame import ThemedApp
from nova.trame.view.components import DataSelector, FileUpload, InputField, RemoteFileInput
from nova.trame.view.components.execution_buttons import ExecutionButtons
from nova.trame.view.components.ornl import NeutronDataSelector
from nova.trame.view.components.progress_bar import ProgressBar
from nova.trame.view.components.tool_outputs import ToolOutputWindows
from nova.trame.view.components.visualization import Interactive2DPlot, MatplotlibFigure
from nova.trame.view.layouts import GridLayout, HBoxLayout, VBoxLayout
from nova.trame.view.theme.theme import LocalStorageManager

from ..view_models.data_selector import DataSelectorVM
from ..view_models.file_upload import FileUploadVM
from ..view_models.neutron_data_selector import NeutronDataSelectorVM

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Config(BaseModel):
    """Pydantic object for testing validation."""

    active_tab: int = Field(default=0)
    debounce_rate: int = Field(default=1000, title="Debounce Rate")
    debounce: str = Field(
        default="",
        description="This field is debounced and will not update its state until you've stopped typing for 1 second.",
        title="Debounced Field",
    )
    radio_items: List[Dict[str, Union[str, int]]] = Field(
        default=[{"title": "Item 1", "value": 1}, {"title": "Item 2", "value": 2}]
    )
    throttle: str = Field(
        default="",
        description="This field is throttled and will only update its state every 1 second.",
        title="Throttled Field",
    )
    value: int = Field(default=0, description="This field is validated via Pydantic.", title="Pydantic Field")

    @field_validator("debounce", mode="after")
    @classmethod
    def on_debounce(cls, text: str) -> str:
        if text:
            print(f"received debounced update: {text}")

        return text

    @field_validator("throttle", mode="after")
    @classmethod
    def on_throttle(cls, text: str) -> str:
        if text:
            print(f"received throttled update: {text}")

        return text


class MplTest:
    """Creates a Matplotlib figure using both Trame options for Matplotlib integration."""

    def __init__(self) -> None:
        self.figure1 = Figure(layout="constrained")
        self.figure2 = Figure(layout="constrained")
        self.ax1 = self.figure1.add_subplot()
        self.ax2 = self.figure2.add_subplot()
        self.fig_type = ""

        self.create_ui()
        self.update()

    def create_ui(self) -> None:
        with GridLayout(columns=2, stretch=True):
            with HBoxLayout(stretch=True):
                self.webagg_view = MatplotlibFigure(self.figure1, webagg=True)
            with HBoxLayout(stretch=True, style="overflow: hidden !important"):
                self.svg_view = MatplotlibFigure(self.figure2)
        vuetify.VBtn("Change MPL Figure", click=self.update)

    def update(self) -> None:
        if self.fig_type == "sin":
            self.fig_type = "cos"
        else:
            self.fig_type = "sin"

        self.plot(self.ax1)
        self.plot(self.ax2)

        self.webagg_view.update(self.figure1)
        self.svg_view.update(self.figure2)

    def plot(self, ax: Axes) -> None:
        ax.clear()

        if self.fig_type == "sin":
            ax.set_title("sin")
            t = np.arange(0.0, 3.0, 0.01)
            s = np.sin(2 * np.pi * t)
        else:
            ax.set_title("cos")
            t = np.arange(0.0, 2.0, 0.01)
            s = np.cos(2 * np.pi * t)

        ax.plot(t, s)


class ComponentTab:
    """Tab for holding the component gallery."""

    def __init__(self, state: State, local_storage: Optional[LocalStorageManager], **kwargs: Any) -> None:
        self.state = state
        self.local_storage = local_storage

        self.create_ui(**kwargs)

    def create_ui(self, **kwargs: Any) -> None:
        client.ClientTriggers(mounted=self.read_local_storage)

        with VBoxLayout(classes="pa-16", stretch=True, **kwargs):
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
                        # [ Vuetify class example start ]
                        vuetify.VBtn("Button", classes="pr-1 mt-2")
                        # [ Vuetify class example end ]
                with vuetify.VMenu():
                    with vuetify.Template(v_slot_activator="{ props }"):
                        vuetify.VBtn("Open Menu", v_bind="props")
                    with vuetify.VList():
                        vuetify.VListItem("Menu Item")
                with vuetify.VTooltip(text="Tooltip"):
                    with vuetify.Template(v_slot_activator="{ props }"):
                        vuetify.VBtn("Tooltip", v_bind="props")

            vuetify.VCardTitle("Navigation Components")
            with GridLayout(classes="mb-4", columns=1, valign="center"):
                with vuetify.VTabs():
                    vuetify.VTab("Tab 1")
                    vuetify.VTab("Tab 2")
                    vuetify.VTab("Tab 3")

            vuetify.VCardTitle("Data Selection Widgets")
            with GridLayout(classes="mb-1", columns=2, valign="center"):
                InputField(v_model="ds_params.directory")
                InputField(v_model="ds_params.refresh_rate")
            # The flex-shrink statement forces this component to take a pixel height.
            # Better would be to refactor this gallery code fully to work properly as a full-page application,
            # but until that happens please ignore.
            with VBoxLayout(classes="border-md", height=400, style="flex-shrink: 0 !important"):
                DataSelector(
                    v_model="data_selector.selected_files",
                    chips=True,
                    directory=("ds_params.directory", "/"),
                    subdirectory=("ds_params.subdirectory",),
                    refresh_rate=("ds_params.refresh_rate", 15),
                )
            with GridLayout(classes="mb-1", columns=4, valign="center"):
                InputField(v_model="nds_params.facility")
                InputField(v_model="nds_params.instrument")
                InputField(v_model="nds_params.experiment")
                InputField(v_model="nds_params.allow_custom_directories", type="checkbox")
            with VBoxLayout(classes="border-md", height=400, style="flex-shrink: 0 !important"):
                NeutronDataSelector(
                    v_model="nds_filesystem.selected_files",
                    clear_selection_on_experiment_change=False,
                    extensions=[".h5", ".nxs"],
                    facility=("nds_params.facility", "SNS"),
                    instrument=("nds_params.instrument", "TOPAZ"),
                    experiment=("nds_params.experiment", "IPTS-12132"),
                    allow_custom_directories=("nds_params.allow_custom_directories", True),
                    chips=True,
                )
            with VBoxLayout(classes="border-md", height=400, style="flex-shrink: 0 !important"):
                try:
                    NeutronDataSelector(
                        v_model="nds_oncat.selected_files",
                        data_source="oncat",
                        projection=["indexed.run_number", "metadata.entry.title"],
                        chips=True,
                    )
                except EnvironmentError:
                    # Unit tests will fail without this in the CI since ONCat vars won't be defined.
                    html.Span(
                        "You must define ONCAT_CLIENT_ID and ONCAT_CLIENT_SECRET in your environment in order "
                        "to test the ONCat backend for NeutronDataSelector."
                    )

            vuetify.VCardTitle("Form Inputs & Controls")
            with GridLayout(columns=3, valign="center"):
                FileUpload(
                    v_model="file_upload.file",
                    base_paths=["/HFIR", "/SNS"],
                    extensions=("file_upload.extensions",),
                    label="{{ file_upload.label }}",
                )
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
                InputField(type="radio", label="Radio Buttons", items=("config.radio_items",))
                InputField(
                    type="select",
                    items="['Option 1', 'Option 2']",
                    label="Select",
                )
                InputField(type="slider", label="Slider")
                InputField(type="switch", label="Switch")
                # [ InputField kwargs example start ]
                InputField(type="textarea", auto_grow=True, label="Text Area")
                # [ InputField kwargs example end ]
                InputField(ref="pydantic-field", id="pydantic-field", v_model=("config.value", "test"))
                InputField(v_model=("config.debounce_rate",))
                InputField(v_model=("config.debounce",), debounce=("config.debounce_rate",))
                InputField(v_model=("config.throttle",), throttle=1000)
                RemoteFileInput(
                    v_model="selected_file",
                    base_paths=["/run"],
                    extensions=[".pid", ".lock"],
                    input_props={"label": "File Selector"},
                )
                RemoteFileInput(
                    v_model="selected_folder",
                    allow_files=False,
                    allow_folders=True,
                    base_paths=["/usr"],
                    input_props={"label": "Folder Selector"},
                )
                RemoteFileInput(
                    v_model="nested.selected_file",
                    base_paths=["/run"],
                    input_props={"label": "Nested v_model File Selector"},
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

            ProgressBar("test")
            ToolOutputWindows("test")
            ExecutionButtons("test")
            ExecutionButtons("test_bindings", stop_btn=("true",), download_btn=False)

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


class FullScreenTab:
    """Tab showing MatplotlibFigure in our full-screen layout."""

    def __init__(self, **kwargs: Any) -> None:
        self.create_ui(**kwargs)

    def create_ui(self, **kwargs: Any) -> None:
        with VBoxLayout(stretch=True, **kwargs):
            MplTest()


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
        command_signal = blinker.signal(get_signal_id("test", Signal.TOOL_COMMAND))
        command_signal.connect(self._set_state)
        self.create_state()
        self.create_ui()

    @property
    def state(self) -> State:
        return self.server.state

    async def _set_state(self, _sender: Any, command: str) -> None:
        progress_signal = blinker.signal(get_signal_id("test", Signal.PROGRESS))
        outputs_signal = blinker.signal(get_signal_id("test", Signal.OUTPUTS))

        if command == ToolCommand.START:
            await progress_signal.send_async(
                "test_sender",
                state=WorkState.RUNNING,
                details={
                    "message": "",
                    "original_dict": {
                        "test": "longstring longstring longstring longstring longstring",
                        "test2": "value2",
                    },
                },
            )
            await outputs_signal.send_async(
                "test_sender", outputs=ToolOutputs(stdout="test_output", stderr="test_error")
            )
        else:
            await progress_signal.send_async("test_sender", state=WorkState.FINISHED, details={})

    def create_state(self) -> None:
        binding = TrameBinding(self.state)

        self.data_selector_vm = DataSelectorVM(binding)
        self.data_selector_vm.model_bind.connect("data_selector")
        self.data_selector_vm.parameter_bind.connect("ds_params")

        self.neutron_data_selector_vm = NeutronDataSelectorVM(binding)
        self.neutron_data_selector_vm.analysis_bind.connect("nds_filesystem")
        self.neutron_data_selector_vm.oncat_bind.connect("nds_oncat")
        self.neutron_data_selector_vm.parameter_bind.connect("nds_params")

        self.file_upload_vm = FileUploadVM(binding)
        self.file_upload_vm.model_bind.connect("file_upload")

        self.config = Config()
        config_bind = binding.new_bind(self.config)
        config_bind.connect("config")
        config_bind.update_in_view(self.config)

        self.state.autoscroll = ""
        self.state.config["value"] = "test"
        self.state.nova__menu = True
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
            layout.toolbar_title.set_text("Widget Gallery")

            # [slot child example]
            with layout.actions:
                vuetify.VBtn("Text Button")
            # [slot child example complete]

            with layout.pre_content:
                with vuetify.VTabs(
                    v_model="config.active_tab", classes="pl-6", update_modelValue="flushState('config');"
                ):
                    vuetify.VTab("Components", value=0)
                    vuetify.VTab("Full-screen Layout", value=1)

            with layout.content:
                ComponentTab(self.state, self.local_storage, v_if="config.active_tab == 0")
                FullScreenTab(v_if="config.active_tab == 1")

            with layout.post_content:
                html.Div("Sticky Bottom Content", classes="text-center w-100")

            return layout
