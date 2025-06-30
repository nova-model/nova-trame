"""View Implementation for DataSelector."""

from typing import Any, List, Optional
from warnings import warn

from trame.app import get_server
from trame.widgets import vuetify3 as vuetify

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.model.ornl.neutron_data_selector import (
    CUSTOM_DIRECTORIES_LABEL,
    NeutronDataSelectorModel,
    NeutronDataSelectorState,
)
from nova.trame.view.layouts import GridLayout
from nova.trame.view_model.ornl.neutron_data_selector import NeutronDataSelectorViewModel

from ..data_selector import DataSelector
from ..input_field import InputField

vuetify.enable_lab()


class NeutronDataSelector(DataSelector):
    """Allows the user to select datafiles from an IPTS experiment."""

    def __init__(
        self,
        v_model: str,
        allow_custom_directories: bool = False,
        facility: str = "",
        instrument: str = "",
        extensions: Optional[List[str]] = None,
        prefix: str = "",
        refresh_rate: int = 30,
        select_strategy: str = "all",
        **kwargs: Any,
    ) -> None:
        """Constructor for DataSelector.

        Parameters
        ----------
        v_model : str
            The name of the state variable to bind to this widget. The state variable will contain a list of the files
            selected by the user.
        allow_custom_directories : bool, optional
            Whether or not to allow users to provide their own directories to search for datafiles in. Ignored if the
            facility parameter is set.
        facility : str, optional
            The facility to restrict data selection to. Options: HFIR, SNS
        instrument : str, optional
            The instrument to restrict data selection to. Please use the instrument acronym (e.g. CG-2).
        extensions : List[str], optional
            A list of file extensions to restrict selection to. If unset, then all files will be shown.
        prefix : str, optional
            A subdirectory within the user's chosen experiment to show files. If not specified, the user will be shown a
            folder browser and will be able to see all files in the experiment that they have access to.
        refresh_rate : int, optional
            The number of seconds between attempts to automatically refresh the file list. Set to zero to disable this
            feature. Defaults to 30 seconds.
        select_strategy : str, optional
            The selection strategy to pass to the `VDataTable component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VDataTable>`__.
            If unset, the `all` strategy will be used.
        **kwargs
            All other arguments will be passed to the underlying
            `VDataTable component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VDataTable>`_.

        Returns
        -------
        None
        """
        if facility and allow_custom_directories:
            warn("allow_custom_directories will be ignored since the facility parameter is set.", stacklevel=1)

        self._facility = facility
        self._instrument = instrument
        self._allow_custom_directories = allow_custom_directories

        self._facilities_name = f"nova__neutrondataselector_{self._next_id}_facilities"
        self._instruments_name = f"nova__neutrondataselector_{self._next_id}_instruments"
        self._experiments_name = f"nova__neutrondataselector_{self._next_id}_experiments"

        super().__init__(v_model, "", extensions, prefix, refresh_rate, select_strategy, **kwargs)

    def create_ui(self, **kwargs: Any) -> None:
        super().create_ui(**kwargs)
        with self._layout.filter:
            with GridLayout(columns=3):
                columns = 3
                if self._facility == "":
                    columns -= 1
                    InputField(
                        v_model=f"{self._state_name}.facility", items=(self._facilities_name,), type="autocomplete"
                    )
                if self._instrument == "":
                    columns -= 1
                    InputField(
                        v_if=f"{self._state_name}.facility !== '{CUSTOM_DIRECTORIES_LABEL}'",
                        v_model=f"{self._state_name}.instrument",
                        items=(self._instruments_name,),
                        type="autocomplete",
                    )
                InputField(
                    v_if=f"{self._state_name}.facility !== '{CUSTOM_DIRECTORIES_LABEL}'",
                    v_model=f"{self._state_name}.experiment",
                    column_span=columns,
                    items=(self._experiments_name,),
                    type="autocomplete",
                )
                InputField(v_else=True, v_model=f"{self._state_name}.custom_directory", column_span=2)

    def create_model(self) -> None:
        state = NeutronDataSelectorState()
        self._model: NeutronDataSelectorModel = NeutronDataSelectorModel(
            state, self._facility, self._instrument, self._extensions, self._prefix, self._allow_custom_directories
        )

    def create_viewmodel(self) -> None:
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

        self._vm.update_view()

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
