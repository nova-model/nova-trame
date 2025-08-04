"""View Implementation for DataSelector."""

from asyncio import ensure_future, sleep
from typing import Any, List, Tuple, Union, cast
from warnings import warn

from trame.app import get_server
from trame.widgets import client, datagrid, html
from trame.widgets import vuetify3 as vuetify
from trame_server.core import State

from nova.mvvm._internal.utils import rgetdictvalue
from nova.mvvm.trame_binding import TrameBinding
from nova.trame._internal.utils import get_state_param, set_state_param
from nova.trame.model.data_selector import DataSelectorModel, DataSelectorState
from nova.trame.view.layouts import GridLayout, HBoxLayout, VBoxLayout
from nova.trame.view_model.data_selector import DataSelectorViewModel

from .input_field import InputField

vuetify.enable_lab()


class DataSelector(datagrid.VGrid):
    """Allows the user to select datafiles from the server."""

    def __init__(
        self,
        v_model: Union[str, Tuple],
        directory: Union[str, Tuple],
        extensions: Union[List[str], Tuple, None] = None,
        prefix: Union[str, Tuple] = "",
        subdirectory: Union[str, Tuple] = "",
        refresh_rate: Union[int, Tuple] = 30,
        select_strategy: Union[str, Tuple] = "all",
        **kwargs: Any,
    ) -> None:
        """Constructor for DataSelector.

        Parameters
        ----------
        v_model : Union[str, Tuple]
            The name of the state variable to bind to this widget. The state variable will contain a list of the files
            selected by the user.
        directory : Union[str, Tuple]
            The top-level folder to expose to users. Only contents of this directory and its children will be exposed to
            users.
        extensions : Union[List[str], Tuple], optional
            A list of file extensions to restrict selection to. If unset, then all files will be shown.
        prefix : Union[str, Tuple], optional
            Deprecated. Please refer to the `subdirectory` parameter.
        subdirectory : Union[str, Tuple], optional
            A subdirectory within the selected top-level folder to show files. If not specified as a string, the user
            will be shown a folder browser and will be able to see all files in the selected top-level folder.
        refresh_rate : Union[int, Tuple], optional
            The number of seconds between attempts to automatically refresh the file list. Set to zero to disable this
            feature. Defaults to 30 seconds.
        select_strategy : Union[str, Tuple], optional
            The selection strategy to pass to the `VDataTable component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VDataTable>`__.
            If unset, the `all` strategy will be used.
        **kwargs
            All other arguments will be passed to the underlying
            `VDataTable component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VDataTable>`_.

        Returns
        -------
        None
        """
        if "allow_custom_directory" in kwargs or "facility" in kwargs or "instrument" in kwargs:
            raise TypeError(
                "The old DataSelector component has been renamed to NeutronDataSelector. Please import it from "
                "`nova.trame.view.components.ornl`."
            )

        if "items" in kwargs:
            raise AttributeError("The items parameter is not allowed on DataSelector widget.")

        if "label" in kwargs:
            self._label = kwargs["label"]
        else:
            self._label = None

        if prefix:
            warn(
                "The prefix parameter has been deprecated. Please switch to using the subdirectory parameter.",
                category=DeprecationWarning,
                stacklevel=1,
            )

            if not subdirectory:
                subdirectory = prefix

        self._v_model = v_model
        if isinstance(v_model, str):
            self._v_model_name_in_state = v_model.split(".")[0]
        else:
            self._v_model_name_in_state = v_model[0].split(".")[0]

        self._directory = directory
        self._last_directory = get_state_param(self.state, self._directory)
        self._extensions = extensions if extensions is not None else []
        self._last_extensions = get_state_param(self.state, self._extensions)
        self._subdirectory = subdirectory
        self._last_subdirectory = get_state_param(self.state, self._subdirectory)
        self._refresh_rate = refresh_rate
        self._select_strategy = select_strategy

        self._revogrid_id = f"nova__dataselector_{self._next_id}_rv"
        self._state_name = f"nova__dataselector_{self._next_id}_state"
        self._directories_name = f"nova__dataselector_{self._next_id}_directories"
        self._datafiles_name = f"nova__dataselector_{self._next_id}_datafiles"

        self._flush_state = f"flushState('{self._v_model_name_in_state}');"
        self._reset_rv_grid = client.JSEval(
            exec=f"window.grid_manager.get('{self._revogrid_id}').updateCheckboxes()"
        ).exec
        self._reset_state = client.JSEval(exec=f"{self._v_model} = []; {self._flush_state}").exec

        self._create_model()
        self._create_viewmodel()
        self._setup_bindings()

        self.create_ui(**kwargs)

        ensure_future(self._refresh_loop())

    @property
    def state(self) -> State:
        return get_server(None, client_type="vue3").state

    def create_ui(self, *args: Any, **kwargs: Any) -> None:
        with VBoxLayout(classes="nova-data-selector", height="100%") as self._layout:
            with HBoxLayout(valign="center"):
                self._layout.filter = html.Div(classes="flex-1-1")
                with vuetify.VBtn(
                    classes="mx-1", density="compact", icon=True, variant="text", click=self.refresh_contents
                ):
                    vuetify.VIcon("mdi-refresh")
                    vuetify.VTooltip("Refresh Contents", activator="parent")

            with GridLayout(columns=2, classes="flex-1-0 h-0", valign="start"):
                if isinstance(self._subdirectory, tuple) or not self._subdirectory:
                    with html.Div(classes="d-flex flex-column h-100 overflow-hidden"):
                        vuetify.VListSubheader("Available Directories", classes="flex-0-1 justify-center px-0")
                        vuetify.VTreeview(
                            v_if=(f"{self._directories_name}.length > 0",),
                            activatable=True,
                            active_strategy="single-independent",
                            classes="flex-1-0 h-0 overflow-y-auto",
                            fluid=True,
                            item_value="path",
                            items=(self._directories_name,),
                            click_open=(self._vm.expand_directory, "[$event.path]"),
                            update_activated=(self.set_subdirectory, "$event"),
                        )
                        vuetify.VListItem("No directories found", classes="flex-0-1 text-center", v_else=True)

                if "columns" in kwargs:
                    columns = kwargs.pop("columns")
                else:
                    columns = (
                        "[{"
                        "    cellTemplate: (createElement, props) =>"
                        f"       window.grid_manager.get('{self._revogrid_id}').cellTemplate(createElement, props),"
                        "    columnTemplate: (createElement) =>"
                        f"       window.grid_manager.get('{self._revogrid_id}').columnTemplate(createElement),"
                        "    name: 'Available Datafiles',"
                        "    prop: 'title',"
                        "}]",
                    )

                super().__init__(
                    v_model=self._v_model,
                    can_focus=False,
                    columns=columns,
                    column_span=1 if isinstance(self._subdirectory, tuple) or not self._subdirectory else 2,
                    frame_size=10,
                    hide_attribution=True,
                    id=self._revogrid_id,
                    readonly=True,
                    stretch=True,
                    source=(self._datafiles_name,),
                    theme="compact",
                    **kwargs,
                )
                if self._label:
                    self.label = self._label
                if "update_modelValue" not in kwargs:
                    self.update_modelValue = self._flush_state

                # Sets up some JavaScript event handlers when the component is mounted.
                with self:
                    client.ClientTriggers(
                        mounted=(
                            "window.grid_manager.add("
                            f"  '{self._revogrid_id}',"
                            f"  '{self._v_model}',"
                            f"  '{self._datafiles_name}',"
                            f"  '{self._v_model_name_in_state}'"
                            ")"
                        )
                    )

            with cast(
                vuetify.VSelect,
                InputField(
                    v_model=self._v_model,
                    classes="flex-0-1 nova-readonly",
                    readonly=True,
                    type="select",
                ),
            ):
                with vuetify.Template(raw_attrs=['v-slot:selection="{ item, index }"']):
                    vuetify.VChip("{{ item.title.split('/').reverse()[0] }}", v_if="index < 2")
                    html.Span(
                        f"(+{{{{ {self._v_model}.length - 2 }}}} others)", v_if="index === 2", classes="text-caption"
                    )

                with vuetify.Template(v_slot_append_inner=True):
                    vuetify.VIcon(
                        "mdi-close-box", v_if=f"{self._v_model}.length > 0", color="primary", size=20, click=self.reset
                    )

    def _create_model(self) -> None:
        state = DataSelectorState()
        self._model = DataSelectorModel(state)

    def _create_viewmodel(self) -> None:
        server = get_server(None, client_type="vue3")
        binding = TrameBinding(server.state)

        self._vm = DataSelectorViewModel(self._model, binding)
        self._vm.state_bind.connect(self._state_name)
        self._vm.directories_bind.connect(self._directories_name)
        self._vm.datafiles_bind.connect(self._datafiles_name)
        self._vm.reset_bind.connect(self.reset)
        self._vm.reset_grid_bind.connect(self._reset_rv_grid)

    def refresh_contents(self) -> None:
        self._vm.update_view(refresh_directories=True)

    def reset(self, _: Any = None) -> None:
        self._reset_state()
        self._reset_rv_grid()

    def set_subdirectory(self, subdirectory_path: str = "") -> None:
        set_state_param(self.state, self._subdirectory, subdirectory_path)
        self._vm.set_subdirectory(subdirectory_path)

    def set_state(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError(
            "The old DataSelector component has been renamed to NeutronDataSelector. Please import it from "
            "`nova.trame.view.components.ornl`."
        )

    # This method sets up Trame state change listeners for each binding parameter that can be changed directly by this
    # component. This allows us to communicate the changes to the developer's bindings without requiring our own. We
    # don't want bindings in the internal implementation as our callbacks could compete with the developer's.
    def _setup_bindings(self) -> None:
        # If the bindings were given initial values, write these to the state.
        set_state_param(self.state, self._directory)
        set_state_param(self.state, self._extensions)
        set_state_param(self.state, self._subdirectory)
        self._vm.set_binding_parameters(
            directory=get_state_param(self.state, self._directory),
            extensions=get_state_param(self.state, self._extensions),
            subdirectory=get_state_param(self.state, self._subdirectory),
        )

        # The component used by this parameter will attempt to set the initial value itself, which will trigger the
        # below change listeners causing unpredictable behavior.
        if isinstance(self._subdirectory, tuple):
            self._subdirectory = (self._subdirectory[0],)

        # Now we set up the change listeners for all bound parameters. These are responsible for updating the component
        # when other portions of the application manipulate these parameters.
        if isinstance(self._directory, tuple):

            @self.state.change(self._directory[0].split(".")[0])
            def on_directory_change(**kwargs: Any) -> None:
                directory = rgetdictvalue(kwargs, self._directory[0])
                if directory != self._last_directory:
                    self._last_directory = directory
                    self._vm.set_binding_parameters(
                        directory=set_state_param(self.state, self._directory, directory),
                    )

        if isinstance(self._extensions, tuple):

            @self.state.change(self._extensions[0].split(".")[0])
            def on_extensions_change(**kwargs: Any) -> None:
                extensions = rgetdictvalue(kwargs, self._extensions[0])
                if extensions != self._last_extensions:
                    self._last_extensions = extensions
                    self._vm.set_binding_parameters(
                        extensions=set_state_param(self.state, self._extensions, extensions),
                    )

        if isinstance(self._subdirectory, tuple):

            @self.state.change(self._subdirectory[0].split(".")[0])
            def on_subdirectory_change(**kwargs: Any) -> None:
                subdirectory = rgetdictvalue(kwargs, self._subdirectory[0])
                if subdirectory != self._last_subdirectory:
                    self._last_subdirectory = subdirectory
                    self._vm.set_binding_parameters(
                        subdirectory=set_state_param(self.state, self._subdirectory, subdirectory),
                    )

    async def _refresh_loop(self) -> None:
        refresh_rate: int = set_state_param(self.state, self._refresh_rate)
        skip = False

        if refresh_rate > 0:
            while True:
                await sleep(refresh_rate)
                if skip:
                    continue

                self.refresh_contents()
                self.state.dirty(self._datafiles_name)

                try:
                    refresh_rate = int(get_state_param(self.state, self._refresh_rate))
                    skip = False
                except TypeError:
                    refresh_rate = 1
                    skip = True
