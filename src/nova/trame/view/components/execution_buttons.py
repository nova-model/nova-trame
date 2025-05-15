"""Module for the Progress Tab."""

from trame.app import get_server
from trame.widgets import client
from trame.widgets import vuetify3 as vuetify
from trame_client.widgets import html

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.view_model.execution_buttons import ExecutionButtonsViewModel


class ExecutionButtons:
    """Execution buttons class. Adds Run/Stop/Cancel/Download buttons to the view.

    This is intended to be used with the `nova-galaxy ToolRunner <https://nova-application-development.readthedocs.io/projects/nova-galaxy/en/latest/core_concepts/tool_runner.html>`__.
    """

    def __init__(self, id: str, stop_btn: bool = False, download_btn: bool = False) -> None:
        """Constructor for ExecutionButtons.

        Parameters
        ----------
        id : str
            Component id. Should be used consistently with ToolRunner and other components.
        stop_btn: bool
            Display stop button.
        download_btn : bool
            Display download button.

        Returns
        -------
        None
        """
        self.id = f"execution_{id}"

        self.server = get_server(None, client_type="vue3")
        binding = TrameBinding(self.server.state)
        self.ctrl = self.server.controller
        self.stop_btn = stop_btn
        self.download_btn = download_btn
        self.view_model = ExecutionButtonsViewModel(id, binding)
        self.view_model.buttons_state_bind.connect(self.id)
        self._download = client.JSEval(
            exec=(
                "async ($event) => {"
                " const blob = new window.Blob([$event], {type: 'application/zip'});"
                "  const url = window.URL.createObjectURL(blob);"
                "  const anchor = window.document.createElement('a');"
                "  anchor.setAttribute('href', url);"
                "  anchor.setAttribute('download', 'results.zip');"
                "  window.document.body.appendChild(anchor);"
                "  anchor.click();"
                "  window.document.body.removeChild(anchor);"
                "  setTimeout(() => window.URL.revokeObjectURL(url), 1000);"
                "}"
            )
        ).exec

        self.create_ui()

    def create_ui(self) -> None:
        with html.Div(classes="d-flex justify-center my-4 w-100"):
            vuetify.VBtn(
                "Run",
                disabled=(f"{self.id}.run_disabled",),
                prepend_icon="mdi-play",
                classes="mr-4",
                id=f"{self.id}_run",
                click=self.run,
            )
            if self.stop_btn:
                vuetify.VBtn(
                    "Stop",
                    disabled=(f"{self.id}.stop_disabled",),
                    loading=(f"{self.id}.stop_in_progress",),
                    classes="mr-4",
                    id=f"{self.id}_stop",
                    prepend_icon="mdi-stop",
                    click=self.stop,
                )
            vuetify.VBtn(
                "Cancel",
                disabled=(f"{self.id}.cancel_disabled",),
                color="error",
                loading=(f"{self.id}.cancel_in_progress",),
                prepend_icon="mdi-cancel",
                classes="mr-4",
                id=f"{self.id}_cancel",
                click=self.cancel,
            )
            if self.download_btn:
                vuetify.VBtn(
                    "Download Results",
                    disabled=(f"{self.id}.download_disabled",),
                    loading=(f"{self.id}.download_in_progress",),
                    id=f"{self.id}.download",
                    click=self.download,
                )

    async def download(self) -> None:
        content = await self.view_model.prepare_results()
        if content:
            self._download(content)

    async def run(self) -> None:
        await self.view_model.run()

    async def cancel(self) -> None:
        await self.view_model.cancel()

    async def stop(self) -> None:
        await self.view_model.stop()
