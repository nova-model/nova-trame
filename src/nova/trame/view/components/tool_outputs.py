"""Module for the Tool outputs."""

from trame.app import get_server
from trame.widgets import vuetify3 as vuetify

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.view.components import InputField
from nova.trame.view.layouts import HBoxLayout
from nova.trame.view_model.tool_outputs import ToolOutputsViewModel


class ToolOutputWindows:
    """Tool outputs class. Displays windows with tool stdout/stderr.

    This is intended to be used with the `nova-galaxy ToolRunner <https://nova-application-development.readthedocs.io/projects/nova-galaxy/en/latest/core_concepts/tool_runner.html>`__.
    """

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
        with HBoxLayout(classes="d-flex", width="100%"):
            with vuetify.VTabs(v_model=(f"{self.id}_active_output_tab", "1"), direction="vertical"):
                vuetify.VTab("Console output", value=1)
                vuetify.VTab("Console error", value=2)
            with HBoxLayout(classes="flex-grow-1"):
                InputField(
                    v_show=f"{self.id}_active_output_tab === '1'",
                    v_model=f"{self.id}.stdout",
                    id=f"{self.id}_outputs",
                    type="autoscroll",
                    auto_grow=True,
                    readonly=True,
                    max_rows="30",
                )
                InputField(
                    v_show=f"{self.id}_active_output_tab === '2'",
                    v_model=f"{self.id}.stderr",
                    id=f"{self.id}_errors",
                    type="autoscroll",
                    auto_grow=True,
                    readonly=True,
                    max_rows="30",
                )
