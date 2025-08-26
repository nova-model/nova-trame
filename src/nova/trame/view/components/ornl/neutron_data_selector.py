"""View Implementation for DataSelector."""

from typing import Any, List, Literal, Tuple, Union
from warnings import warn

from trame.app import get_server
from trame.widgets import vuetify3 as vuetify

from nova.mvvm._internal.utils import rgetdictvalue
from nova.mvvm.trame_binding import TrameBinding
from nova.trame.model.ornl.analysis_data_selector import (
    CUSTOM_DIRECTORIES_LABEL,
    AnalysisDataSelectorModel,
    AnalysisDataSelectorState,
)
from nova.trame.model.ornl.neutron_data_selector import NeutronDataSelectorModel
from nova.trame.model.ornl.oncat_data_selector import ONCatDataSelectorModel, ONCatDataSelectorState
from nova.trame.view.layouts import GridLayout
from nova.trame.view_model.ornl.neutron_data_selector import NeutronDataSelectorViewModel

from ..data_selector import DataSelector, get_state_param, set_state_param
from ..input_field import InputField

vuetify.enable_lab()


class NeutronDataSelector(DataSelector):
    """Allows the user to select datafiles from an IPTS experiment."""

    def __init__(
        self,
        v_model: Union[str, Tuple],
        allow_custom_directories: Union[bool, Tuple] = False,
        data_source: Literal["filesystem", "oncat"] = "filesystem",
        facility: Union[str, Tuple] = "",
        instrument: Union[str, Tuple] = "",
        experiment: Union[str, Tuple] = "",
        extensions: Union[List[str], Tuple, None] = None,
        projection: Union[List[str], Tuple, None] = None,
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
        allow_custom_directories : Union[bool, Tuple], optional
            Whether or not to allow users to provide their own directories to search for datafiles in. Ignored if the
            facility parameter is set.
        data_source : Literal["filesystem", "oncat"], optional
            The source from which to pull datafiles. Defaults to "filesystem". If using ONCat, you will need to set the
            following environment variables for local development: `ONCAT_CLIENT_ID` and `ONCAT_CLIENT_SECRET`. Note
            that this parameter does not supporting Trame bindings. If you need to swap between the options, please
            create two instances of this class and switch between them using a v_if or a v_show.
        facility : Union[str, Tuple], optional
            The facility to restrict data selection to. Options: HFIR, SNS
        instrument : Union[str, Tuple], optional
            The instrument to restrict data selection to. Please use the instrument acronym (e.g. CG-2).
        experiment : Union[str, Tuple], optional
            The experiment to restrict data selection to.
        extensions : Union[List[str], Tuple], optional
            A list of file extensions to restrict selection to. If unset, then all files will be shown.
        projection : Union[List[str], Tuple], optional
            Sets the projection argument when pulling data files via pyoncat. Please refer to the ONCat documentation
            for how to use this. This should only be used with `data_source="oncat"`.
        subdirectory : Union[str, Tuple], optional
            A subdirectory within the user's chosen experiment to show files. If not specified as a string, the user
            will be shown a folder browser and will be able to see all files in the experiment that they have access to.
        refresh_rate : Union[str, Tuple], optional
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
        if data_source == "oncat" and allow_custom_directories:
            warn("allow_custom_directories will be ignored since data will be pulled from ONCat.", stacklevel=1)

        if data_source == "oncat" and subdirectory:
            warn("subdirectory will be ignored since data will be pulled from ONCat.", stacklevel=1)

        if isinstance(facility, str) and facility and allow_custom_directories:
            warn("allow_custom_directories will be ignored since the facility parameter is fixed.", stacklevel=1)

        self._facility = facility
        self._instrument = instrument
        self._experiment = experiment
        self._allow_custom_directories = allow_custom_directories
        self._last_allow_custom_directories = self._allow_custom_directories
        self._data_source = data_source
        self._projection = projection

        self._state_name = f"nova__dataselector_{self._next_id}_state"
        self._facilities_name = f"nova__neutrondataselector_{self._next_id}_facilities"
        self._selected_facility_name = (
            self._facility[0] if isinstance(self._facility, tuple) else f"{self._state_name}.facility"
        )
        self._instruments_name = f"nova__neutrondataselector_{self._next_id}_instruments"
        self._selected_instrument_name = (
            self._instrument[0] if isinstance(self._instrument, tuple) else f"{self._state_name}.instrument"
        )
        self._experiments_name = f"nova__neutrondataselector_{self._next_id}_experiments"
        self._selected_experiment_name = (
            self._experiment[0] if isinstance(self._experiment, tuple) else f"{self._state_name}.experiment"
        )

        super().__init__(
            v_model,
            "",
            extensions=extensions,
            subdirectory=subdirectory if data_source == "filesystem" else "oncat",
            refresh_rate=refresh_rate,
            select_strategy=select_strategy,
            **kwargs,
        )

    def create_projection_column_title(self, key: str) -> str:
        return key.split(".")[-1].replace("_", " ").title()

    def create_ui(self, **kwargs: Any) -> None:
        if self._data_source == "oncat":
            columns = (
                "["
                "  {"
                "    cellTemplate: (createElement, props) =>"
                f"     window.grid_manager.get('{self._revogrid_id}').cellTemplate(createElement, props),"
                "    columnTemplate: (createElement) =>"
                f"     window.grid_manager.get('{self._revogrid_id}').columnTemplate(createElement),"
                "    name: 'Available Datafiles',"
                "    prop: 'title',"
                "    size: 150,"
                "  },"
            )
            if self._projection:
                for key in self._projection:
                    columns += f"{{name: '{self.create_projection_column_title(key)}', prop: '{key}', size: 150}},"
            columns += "]"

            super().create_ui(columns=(columns,), resize=True, **kwargs)
        else:
            super().create_ui(**kwargs)

        with self._layout.filter:
            with GridLayout(columns=3):
                column_span = 3
                if isinstance(self._facility, tuple) or not self._facility:
                    column_span -= 1
                    InputField(
                        v_model=self._selected_facility_name,
                        items=(self._facilities_name,),
                        type="autocomplete",
                        update_modelValue=(self.update_facility, "[$event]"),
                    )
                if isinstance(self._instrument, tuple) or not self._instrument:
                    column_span -= 1
                    InputField(
                        v_if=f"{self._selected_facility_name} !== '{CUSTOM_DIRECTORIES_LABEL}'",
                        v_model=self._selected_instrument_name,
                        items=(self._instruments_name,),
                        type="autocomplete",
                        update_modelValue=(self.update_instrument, "[$event]"),
                    )
                InputField(
                    v_if=f"{self._selected_facility_name} !== '{CUSTOM_DIRECTORIES_LABEL}'",
                    v_model=self._selected_experiment_name,
                    column_span=column_span,
                    items=(self._experiments_name,),
                    type="autocomplete",
                    update_modelValue=(self.update_experiment, "[$event]"),
                )
                InputField(v_else=True, v_model=f"{self._state_name}.custom_directory", column_span=2)

    def _create_model(self) -> None:
        self._model: NeutronDataSelectorModel
        if self._data_source == "oncat":
            self._model = ONCatDataSelectorModel(ONCatDataSelectorState())
        else:
            self._model = AnalysisDataSelectorModel(AnalysisDataSelectorState())

    def _create_viewmodel(self) -> None:
        server = get_server(None, client_type="vue3")
        binding = TrameBinding(server.state)

        self._vm: NeutronDataSelectorViewModel = NeutronDataSelectorViewModel(self._model, binding)
        self._vm.state_bind.connect(self._state_name)
        self._vm.facilities_bind.connect(self._facilities_name)
        self._vm.instruments_bind.connect(self._instruments_name)
        self._vm.experiments_bind.connect(self._experiments_name)
        self._vm.directories_bind.connect(self._directories_name)
        self._vm.datafiles_bind.connect(self._datafiles_name)
        self._vm.reset_bind.connect(self.reset)
        self._vm.reset_grid_bind.connect(self._reset_rv_grid)

        self._vm.update_view()

    # This method sets up Trame state change listeners for each binding parameter that can be changed directly by this
    # component. This allows us to communicate the changes to the developer's bindings without requiring our own. We
    # don't want bindings in the internal implementation as our callbacks could compete with the developer's.
    def _setup_bindings(self) -> None:
        # If the bindings were given initial values, write these to the state.
        set_state_param(self.state, self._facility)
        set_state_param(self.state, self._instrument)
        set_state_param(self.state, self._experiment)
        set_state_param(self.state, self._allow_custom_directories)
        set_state_param(self.state, self._projection)
        self._last_facility = get_state_param(self.state, self._facility)
        self._last_instrument = get_state_param(self.state, self._instrument)
        self._last_experiment = get_state_param(self.state, self._experiment)
        self._vm.set_binding_parameters(
            facility=get_state_param(self.state, self._facility),
            instrument=get_state_param(self.state, self._instrument),
            experiment=get_state_param(self.state, self._experiment),
            allow_custom_directories=get_state_param(self.state, self._allow_custom_directories),
            projection=get_state_param(self.state, self._projection),
        )

        # Now we set up the change listeners for all bound parameters. These are responsible for updating the component
        # when other portions of the application manipulate these parameters.
        if isinstance(self._facility, tuple):

            @self.state.change(self._facility[0].split(".")[0])
            def on_facility_change(**kwargs: Any) -> None:
                facility = rgetdictvalue(kwargs, self._facility[0])
                if facility != self._last_facility:
                    self._last_facility = facility
                    self._vm.set_binding_parameters(
                        facility=set_state_param(self.state, (self._selected_facility_name,), facility)
                    )
                    self._vm.reset()

        if isinstance(self._instrument, tuple):

            @self.state.change(self._instrument[0].split(".")[0])
            def on_instrument_change(**kwargs: Any) -> None:
                instrument = rgetdictvalue(kwargs, self._instrument[0])
                if instrument != self._last_instrument:
                    self._last_instrument = instrument
                    self._vm.set_binding_parameters(
                        instrument=set_state_param(self.state, (self._selected_instrument_name,), instrument)
                    )
                    self._vm.reset()

        if isinstance(self._experiment, tuple):

            @self.state.change(self._experiment[0].split(".")[0])
            def on_experiment_change(**kwargs: Any) -> None:
                experiment = rgetdictvalue(kwargs, self._experiment[0])
                if experiment and experiment != self._last_experiment:
                    self._last_experiment = experiment
                    # See the note in the update_experiment method for why we call this twice.
                    self._vm.set_binding_parameters(
                        experiment=set_state_param(self.state, (self._selected_experiment_name,), ""),
                    )
                    self._vm.set_binding_parameters(
                        experiment=set_state_param(self.state, (self._selected_experiment_name,), experiment)
                    )
                    self._vm.reset()

        if isinstance(self._allow_custom_directories, tuple):

            @self.state.change(self._allow_custom_directories[0].split(".")[0])
            def on_allow_custom_directories_change(**kwargs: Any) -> None:
                allow_custom_directories = rgetdictvalue(kwargs, self._allow_custom_directories[0])  # type: ignore
                if allow_custom_directories != self._last_allow_custom_directories:
                    self._last_allow_custom_directories = allow_custom_directories
                    self._vm.set_binding_parameters(
                        allow_custom_directories=set_state_param(
                            self.state, self._allow_custom_directories, allow_custom_directories
                        )
                    )

        if isinstance(self._projection, tuple):

            @self.state.change(self._projection[0].split(".")[0])
            def on_projection_change(**kwargs: Any) -> None:
                projection = rgetdictvalue(kwargs, self._projection[0])  # type: ignore
                if projection != self._projection:
                    self._projection = projection
                    self._vm.set_binding_parameters(
                        projection=set_state_param(self.state, self._projection, projection)
                    )

    # These update methods notify the rest of the application when the component changes bound parameters.
    def update_facility(self, facility: str) -> None:
        self._vm.set_binding_parameters(
            facility=set_state_param(self.state, (self._selected_facility_name,), facility),
            instrument=set_state_param(self.state, (self._selected_instrument_name,), ""),  # Reset the instrument
            experiment=set_state_param(self.state, (self._selected_experiment_name,), ""),  # Reset the experiment
        )
        self._vm.reset()

    def update_instrument(self, instrument: str) -> None:
        self._vm.set_binding_parameters(
            instrument=set_state_param(self.state, (self._selected_instrument_name,), instrument),
            experiment=set_state_param(self.state, (self._selected_experiment_name,), ""),  # Reset the experiment
        )
        self._vm.reset()

    def update_experiment(self, experiment: str) -> None:
        # Setting the experiment to an empty string forces the treeview to clear it's selection state.
        self._vm.set_binding_parameters(
            experiment=set_state_param(self.state, (self._selected_experiment_name,), ""),
        )
        self._vm.set_binding_parameters(
            experiment=set_state_param(self.state, (self._selected_experiment_name,), experiment),
        )
        self._vm.reset()

    def set_state(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError(
            "The set_state method has been removed. Please use update_facility, update_instrument, and "
            "update_experiment instead."
        )
