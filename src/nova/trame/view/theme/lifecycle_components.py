"""Components used to control the lifecycle of a Themed Application."""

import logging
from typing import Any

from trame.app import get_server
from trame.widgets import vuetify3 as vuetify

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ExitButton:
    """Exit button for Trame Applications."""

    def __init__(self, exit_callback: Any = None, job_status_callback: Any = None) -> None:
        self.server = get_server(None, client_type="vue3")
        self.server.state.nova_kill_jobs_on_exit = False
        self.server.state.nova_show_exit_dialog = False
        self.server.state.nova_show_stop_jobs_on_exit_checkbox = False
        self.server.state.nova_running_jobs = []
        self.server.state.nova_show_exit_progress = False
        self.exit_application_callback = exit_callback
        self.job_status_callback = job_status_callback
        self.create_ui()

    def create_ui(self) -> None:
        with vuetify.VBtn(
            "Exit",
            prepend_icon="mdi-close-box",
            classes="mr-4 bg-error",
            id="shutdown_app_theme_button",
            color="white",
            click=self.open_exit_dialog,
        ):
            with vuetify.VDialog(v_model="nova_show_exit_dialog", persistent="true"):
                with vuetify.VCard(classes="pa-4 ma-auto"):
                    vuetify.VCardTitle("Exit Application")
                    with vuetify.VCardText(
                        "Are you sure you want to exit this application?",
                        variant="outlined",
                    ):
                        vuetify.VCheckbox(
                            v_model="nova_kill_jobs_on_exit",
                            label="Stop All Jobs On Exit.",
                            v_if="nova_running_jobs.length > 0",
                        )
                        with vuetify.VList():
                            vuetify.VListSubheader("Running Jobs:", v_if="nova_running_jobs.length > 0")
                            vuetify.VListItem("{{ item }}", v_for="(item, index) in nova_running_jobs")
                    with vuetify.VCardActions(v_if="!nova_show_exit_progress"):
                        vuetify.VBtn(
                            "Exit App",
                            click=self.exit_application_callback,
                            color="error",
                        )
                        vuetify.VBtn(
                            "Stay In App",
                            click=self.close_exit_dialog,
                        )
                    with vuetify.VCardActions(v_else=True):
                        vuetify.VCardText(
                            "Exiting Application...",
                            variant="outlined",
                        )
                        vuetify.VProgressCircular(indeterminate=True)

    async def open_exit_dialog(self) -> None:
        self.server.state.nova_show_exit_dialog = True
        await self.job_status_callback()

    async def close_exit_dialog(self) -> None:
        self.server.state.nova_show_exit_dialog = False
