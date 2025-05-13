"""View Implementation for DataSelector."""

from typing import Any, List, Optional, cast
from warnings import warn

from trame.app import get_server
from trame.widgets import client, html
from trame.widgets import vuetify3 as vuetify

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.model.data_selector import DataSelectorModel
from nova.trame.view.layouts import GridLayout, VBoxLayout
from nova.trame.view_model.data_selector import DataSelectorViewModel

from .input_field import InputField

vuetify.enable_lab()


class DataSelector(vuetify.VDataTableVirtual):
    """Allows the user to select datafiles from an IPTS experiment."""

    def __init__(
        self,
        v_model: str,
        facility: str = "",
        instrument: str = "",
        extensions: Optional[List[str]] = None,
        prefix: str = "",
        select_strategy: str = "all",
        show_user_directories: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructor for DataSelector.

        Parameters
        ----------
        v_model : str
            The name of the state variable to bind to this widget. The state variable will contain a list of the files
            selected by the user.
        facility : str, optional
            The facility to restrict data selection to. Options: HFIR, SNS
        instrument : str, optional
            The instrument to restrict data selection to. Please use the instrument acronym (e.g. CG-2).
        extensions : List[str], optional
            A list of file extensions to restrict selection to. If unset, then all files will be shown.
        prefix : str, optional
            A subdirectory within the user's chosen experiment to show files. If not specified, the user will be shown a
            folder browser and will be able to see all files in the experiment that they have access to.
        select_strategy : str, optional
            The selection strategy to pass to the `VDataTable component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VDataTable>`__.
            If unset, the `all` strategy will be used.
        show_user_directories : bool, optional
            Whether or not to allow users to select data files from user directories. Ignored if the facility parameter
            is set.
        **kwargs
            All other arguments will be passed to the underlying
            `VDataTable component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VDataTable>`_.

        Returns
        -------
        None
        """
        if "items" in kwargs:
            raise AttributeError("The items parameter is not allowed on DataSelector widget.")

        if "label" in kwargs:
            self._label = kwargs["label"]
        else:
            self._label = None

        if facility and show_user_directories:
            warn("show_user_directories will be ignored since the facility parameter is set.", stacklevel=1)

        self._v_model = v_model
        self._v_model_name_in_state = v_model.split(".")[0]
        self._extensions = extensions if extensions is not None else []
        self._prefix = prefix
        self._select_strategy = select_strategy
        self._show_user_directories = show_user_directories

        self._state_name = f"nova__dataselector_{self._next_id}_state"
        self._facilities_name = f"nova__dataselector_{self._next_id}_facilities"
        self._instruments_name = f"nova__dataselector_{self._next_id}_instruments"
        self._experiments_name = f"nova__dataselector_{self._next_id}_experiments"
        self._directories_name = f"nova__dataselector_{self._next_id}_directories"
        self._datafiles_name = f"nova__dataselector_{self._next_id}_datafiles"

        self._flush_state = f"flushState('{self._v_model_name_in_state}');"
        self._reset_state = client.JSEval(exec=f"{self._v_model} = []; {self._flush_state}").exec

        self.create_model(facility, instrument)
        self.create_viewmodel()

        self.create_ui(facility, instrument, **kwargs)

    def create_ui(self, facility: str, instrument: str, **kwargs: Any) -> None:
        with VBoxLayout(classes="nova-data-selector", height="100%"):
            with GridLayout(columns=3):
                columns = 3
                if facility == "":
                    columns -= 1
                    InputField(
                        v_model=f"{self._state_name}.facility", items=(self._facilities_name,), type="autocomplete"
                    )
                if instrument == "":
                    columns -= 1
                    InputField(
                        v_if=f"{self._state_name}.facility !== 'User Directory'",
                        v_model=f"{self._state_name}.instrument",
                        items=(self._instruments_name,),
                        type="autocomplete",
                    )
                InputField(
                    v_if=f"{self._state_name}.facility !== 'User Directory'",
                    v_model=f"{self._state_name}.experiment",
                    column_span=columns,
                    items=(self._experiments_name,),
                    type="autocomplete",
                )
                InputField(v_else=True, v_model=f"{self._state_name}.user_directory", column_span=2)

            with GridLayout(columns=2, classes="flex-1-0 h-0", valign="start"):
                if not self._prefix:
                    with html.Div(classes="d-flex flex-column h-100 overflow-hidden"):
                        vuetify.VListSubheader("Available Directories", classes="flex-0-1 justify-center px-0")
                        vuetify.VTreeview(
                            v_if=(f"{self._directories_name}.length > 0",),
                            activatable=True,
                            active_strategy="single-independent",
                            classes="flex-1-0 h-0 overflow-y-auto",
                            item_value="path",
                            items=(self._directories_name,),
                            update_activated=(self._vm.set_directory, "$event"),
                        )
                        vuetify.VListItem("No directories found", classes="flex-0-1 text-center", v_else=True)

                super().__init__(
                    v_model=self._v_model,
                    classes="h-100 overflow-y-auto",
                    fixed_header=True,
                    headers=("[{ align: 'left', key: 'title', title: 'Available Datafiles' }]",),
                    item_title="title",
                    item_value="path",
                    select_strategy=self._select_strategy,
                    show_select=True,
                    **kwargs,
                )
                if self._label:
                    self.label = self._label
                self.items = (self._datafiles_name,)
                if "update_modelValue" not in kwargs:
                    self.update_modelValue = self._flush_state

            with cast(
                vuetify.VSelect,
                InputField(
                    v_model=self._v_model,
                    classes="flex-0-1 nova-readonly",
                    clearable=True,
                    readonly=True,
                    type="select",
                    click_clear=self.reset,
                ),
            ):
                with vuetify.Template(raw_attrs=['v-slot:selection="{ item, index }"']):
                    vuetify.VChip("{{ item.title.split('/').reverse()[0] }}", v_if="index < 2")
                    html.Span(
                        f"(+{{{{ {self._v_model}.length - 2 }}}} others)", v_if="index === 2", classes="text-caption"
                    )

    def create_model(self, facility: str, instrument: str) -> None:
        self._model = DataSelectorModel(
            facility, instrument, self._extensions, self._prefix, self._show_user_directories
        )

    def create_viewmodel(self) -> None:
        server = get_server(None, client_type="vue3")
        binding = TrameBinding(server.state)

        self._vm = DataSelectorViewModel(self._model, binding)
        self._vm.state_bind.connect(self._state_name)
        self._vm.facilities_bind.connect(self._facilities_name)
        self._vm.instruments_bind.connect(self._instruments_name)
        self._vm.experiments_bind.connect(self._experiments_name)
        self._vm.directories_bind.connect(self._directories_name)
        self._vm.datafiles_bind.connect(self._datafiles_name)
        self._vm.reset_bind.connect(self.reset)

        self._vm.update_view()

    def reset(self, _: Any = None) -> None:
        self._reset_state()

    def set_state(
        self, facility: Optional[str] = None, instrument: Optional[str] = None, experiment: Optional[str] = None
    ) -> None:
        """Programmatically set the facility, instrument, and/or experiment to restrict data selection to.

        If a parameter is None, then it will not be updated.

        Parameters
        ----------
        facility : str, optional
            The facility to restrict data selection to. Options: HFIR, SNS
        instrument : str, optional
            The instrument to restrict data selection to. Must be at the selected facility.
        experiment : str, optional
            The experiment to restrict data selection to. Must begin with "IPTS-". It is your responsibility to validate
            that the provided experiment exists within the instrument directory. If it doesn't then no datafiles will be
            shown to the user.

        Returns
        -------
        None
        """
        self._vm.set_state(facility, instrument, experiment)
