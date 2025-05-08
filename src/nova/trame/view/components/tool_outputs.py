"""Module for the Tool outputs."""

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.view.components import InputField
from trame.app import get_server
from trame.widgets import vuetify3 as vuetify

from nova.trame.view_model.tool_outputs import ToolOutputsViewModel


class ToolOutputWindows:
    """Tool outputs class. Displays windows with tool stdout/stderr."""

    def __init__(self, id: str) -> None:
        """Constructor for ToolOutputWindows.

        Parameters
        ----------
        id : str
            Component id. Should be used consistently with ToolRunner and other components
        Returns
        -------
        None
        """

        self.id = f"tool_outputs_{id}"
        self.create_viewmodel(id)
        self.view_model.tool_outputs_bind.connect(self.id)
        self.create_ui()

    def create_viewmodel(self, id: str) -> None:
        server = get_server(None, client_type="vue3")
        binding = TrameBinding(server.state)
        self.view_model = ToolOutputsViewModel(id, binding)

    def create_ui(self) -> None:
        with vuetify.VContainer(classes="d-flex", fluid=True):
            with vuetify.VTabs(v_model=(f"{self.id}_active_output_tab", "0"), direction="vertical"):
                vuetify.VTab("Console output", value=1)
                vuetify.VTab("Console error", value=2)
            with vuetify.VWindow(v_model=f"{self.id}_active_output_tab", classes="flex-grow-1"):
                with vuetify.VWindowItem(value=1, reverse_transition="false", transition="false"):
                    InputField(
                        v_model=f"{self.id}.stdout",
                        type="autoscroll",
                        auto_grow=True,
                        readonly=True,
                        max_rows="30",
                    )
                with vuetify.VWindowItem(value=2, reverse_transition="false", transition="false"):
                    InputField(
                        v_model=f"{self.id}.stderr",
                        type="autoscroll",
                        auto_grow=True,
                        readonly=True,
                        max_rows="30",
                    )
