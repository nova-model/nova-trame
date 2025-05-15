"""Module for the Progress Tab."""

from trame.app import get_server
from trame.widgets import vuetify3 as vuetify
from trame_client.widgets import html

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.view_model.progress_bar import ProgressBarViewModel


class ProgressBar:
    """Progress bar class. Adds progress bar that displays job status to the view.

    This is intended to be used with the `nova-galaxy ToolRunner <https://nova-application-development.readthedocs.io/projects/nova-galaxy/en/latest/core_concepts/tool_runner.html>`__.
    """

    def __init__(self, id: str) -> None:
        """Constructor for ProgressBar.

        Parameters
        ----------
        id : str
            Component id. Should be used consistently with ToolRunner and other components

        Returns
        -------
        None
        """
        self.id = f"progress_bar_{id}"
        self.create_viewmodel(id)
        self.view_model.progress_state_bind.connect(self.id)
        self.create_ui()

    def create_viewmodel(self, id: str) -> None:
        server = get_server(None, client_type="vue3")
        binding = TrameBinding(server.state)
        self.view_model = ProgressBarViewModel(id, binding)

    def create_ui(self) -> None:
        with vuetify.VProgressLinear(
            height="25",
            model_value=(f"{self.id}.progress", "0"),
            striped=True,
            id=f"{self.id}_show_progress",
            v_show=(f"{self.id}.show_progress",),
        ):
            html.H5(v_text=f"{self.id}.details")
        with vuetify.VProgressLinear(
            height="25",
            model_value="100",
            striped=False,
            color="error",
            id=f"{self.id}_show_failed",
            v_show=(f"{self.id}.show_failed",),
        ):
            html.H5(v_text=f"{self.id}.details", classes="text-white")
        with vuetify.VProgressLinear(
            height="25",
            model_value="100",
            striped=False,
            color="primary",
            id=f"{self.id}_show_ok",
            v_show=(f"{self.id}.show_ok",),
        ):
            html.H5(v_text=f"{self.id}.details", classes="text-white")
