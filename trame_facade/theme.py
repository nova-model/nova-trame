import json
import logging
import os
from pathlib import Path

from mergedeep import merge, Strategy
import sass

from trame.app import get_server
from trame.assets.local import LocalFileManager
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import client, vuetify3 as vuetify
from trame_client.widgets import html


THEME_PATH = Path(__file__).parent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ThemedApp:
    """Parent class for Trame applications that injects theming into the application."""

    def __init__(self, server=None, vuetify_config_overrides={}):
        self.server = get_server(server, client_type="vue3")
        self.layout = None
        self.local_storage = None

        self.css = None
        try:
            with open(THEME_PATH / "core_style.scss", "r") as scss_file:
                self.css = sass.compile(string=scss_file.read())
        except Exception as e:
            logger.warning("Could not load base scss stylesheet.")
            logger.error(e)

        theme_path = THEME_PATH / "vuetify_config.json"
        try:
            with open(theme_path, "r") as vuetify_config:
                self.vuetify_config = json.load(vuetify_config)

                merge(
                    self.vuetify_config,
                    vuetify_config_overrides,
                    strategy=Strategy.REPLACE,
                )
        except Exception as e:
            logger.warning(f"Could not load vuetify config from {theme_path}.")
            logger.error(e)
        for shortcut in ["primary", "secondary", "accent"]:
            if shortcut in self.vuetify_config:
                self.vuetify_config["theme"]["themes"]["ModernTheme"]["colors"][
                    shortcut
                ] = self.vuetify_config[shortcut]

        # Since this is only intended for theming Trame apps, I don't think we need to invoke the MVVM framework here,
        # and working directly with the Trame state makes this easier for me to manage.
        self.state.facade__menu = False
        self.state.facade__defaults = self.vuetify_config["theme"]["themes"][
            "ModernTheme"
        ].get("defaults", {})
        self.state.facade__theme = "ModernTheme"
        self.state.trame__favicon = LocalFileManager(__file__).url(
            "favicon", "./assets/favicon.png"
        )

    @property
    def state(self):
        return self.server.state

    def set_theme(self, theme, force=True):
        # I set force to True by default as I want the user to be able to say self.set_theme('MyTheme')
        # while still blocking theme.py calls to set_theme if the selection menu is disabled.
        if self.state.facade__menu or force:
            with self.state:
                self.state.facade__defaults = (
                    self.vuetify_config["theme"]["themes"]
                    .get(theme, {})
                    .get("defaults", {})
                )
                self.state.facade__theme = theme

        # We only want to sync to localStorage if the user is selecting and we want to preserve the selection.
        if self.state.facade__menu:
            self.local_storage({"key": "facade__theme", "value": theme})

    def create_ui(self):
        with VAppLayout(self.server, vuetify_config=self.vuetify_config) as layout:
            client.ClientTriggers(
                mounted=(
                    self.set_theme,
                    "[window.localStorage.getItem('facade__theme'), false]",
                )
            )

            self.layout = layout
            self.local_storage = client.JSEval(
                exec="window.localStorage.setItem($event.key, $event.value);"
            ).exec

            client.Style(self.css)

            with vuetify.VDefaultsProvider(defaults=("facade__defaults",)) as defaults:
                layout.defaults = defaults

                with vuetify.VThemeProvider(theme=("facade__theme",)) as theme:
                    layout.theme = theme

                    with vuetify.VAppBar() as toolbar:
                        layout.toolbar = toolbar

                        with vuetify.VAppBarTitle() as toolbar_title:
                            layout.toolbar_title = toolbar_title
                        vuetify.VSpacer()
                        with html.Div(classes="mr-2") as actions:
                            layout.actions = actions

                            with vuetify.VMenu(
                                v_if="facade__menu",
                                close_delay=10000,
                                open_on_hover=True,
                            ) as theme_menu:
                                layout.theme_menu = theme_menu

                                with vuetify.Template(v_slot_activator="{ props }"):
                                    vuetify.VBtn(
                                        v_bind="props",
                                        classes="mr-2",
                                        icon="mdi-brush-variant",
                                    )

                                with vuetify.VList(width=200):
                                    vuetify.VListSubheader("Select Theme")
                                    vuetify.VDivider()
                                    with vuetify.VListItem(
                                        click=(self.set_theme, ["ModernTheme"])
                                    ):
                                        vuetify.VListItemTitle("Modern")
                                        vuetify.VListItemSubtitle(
                                            "Selected",
                                            v_if="facade__theme === 'ModernTheme'",
                                        )
                                    with vuetify.VListItem(
                                        click=(
                                            self.set_theme,
                                            ["TechnicalTheme"],
                                        )
                                    ):
                                        vuetify.VListItemTitle("Technical")
                                        vuetify.VListItemSubtitle(
                                            "Selected",
                                            v_if="facade__theme === 'TechnicalTheme'",
                                        )

                    with vuetify.VMain() as content:
                        layout.content = content

                    with vuetify.VFooter(
                        app=True,
                        classes="my-0 px-1 py-0 text-center justify-center",
                        border=True,
                    ) as footer:
                        layout.footer = footer

                        vuetify.VProgressCircular(
                            classes="mr-1",
                            color="primary",
                            indeterminate=("!!galaxy_running",),
                            size=16,
                            width=3,
                        )
                        html.A(
                            "Powered by Calvera",
                            classes="text-grey-lighten-1 text-caption text-decoration-none",
                            href=("galaxy_url",),
                            target="_blank",
                        )
                        vuetify.VSpacer()
                        footer.add_child(
                            '<a href="https://www.ornl.gov/" class="text-grey-lighten-1 text-caption text-decoration-none" '
                            'target="_blank">© 2024 ORNL</a>'
                        )

            return layout
