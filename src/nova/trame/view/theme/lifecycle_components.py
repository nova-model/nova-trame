"""Components used to control the lifecycle of a Themed Application."""

import blinker
from trame.app import get_server
from trame.widgets import vuetify3 as vuetify
from trame_client.widgets import html

from nova.common.signals import Signal


class ExitButton:
    """Exit button for Trame Applications."""

    def __init__(self) -> None:
        self.create_ui()
        self.server = get_server(None, client_type="vue3")
        self.server.state.nova_kill_jobs_on_exit = True
        self.server.state.nova_show_exit_dialog = False

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
                with vuetify.VCard(classes="pa-4 justify-md-center ma-auto"):
                    vuetify.VCardText(
                        "Are you sure you want to exit this application?",
                        classes="text-h6",
                        variant="outlined",
                    )
                    vuetify.VCheckbox(v_model="nova_kill_jobs_on_exit", label="Stop All Jobs On Exit.")
                    with html.Div(classes="text-center"):
                        vuetify.VBtn(
                            "Exit App",
                            classes="mr-4",
                            click=self.exit_application,
                            color="error",
                        )
                        vuetify.VBtn(
                            "Stay In App",
                            click=self.close_exit_dialog,
                        )

    def open_exit_dialog(self) -> None:
        self.server.state.nova_show_exit_dialog = True

    def close_exit_dialog(self) -> None:
        self.server.state.nova_show_exit_dialog = False

    async def exit_application(self) -> None:
        print(f"Closing App. Killing jobs: {self.server.state.nova_kill_jobs_on_exit}")
        if self.server.state.nova_kill_jobs_on_exit:
            stop_signal = blinker.signal(Signal.EXIT_SIGNAL)
            await stop_signal.send_async("nova-trame-exit")
        await self.server.stop()
