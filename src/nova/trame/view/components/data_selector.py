"""View Implementation for DataSelector."""

from typing import Any

from trame.app import get_server
from trame.widgets import vuetify3 as vuetify

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.model.data_selector import DataSelectorModel
from nova.trame.view.layouts import HBoxLayout
from nova.trame.view_model.data_selector import DataSelectorViewModel

from .input_field import InputField


class DataSelector(vuetify.VAutocomplete):
    """Allows the user to select datafiles from an IPTS experiment."""

    def __init__(self, facility: str = "", instrument: str = "", **kwargs: Any) -> None:
        if "items" in kwargs:
            raise AttributeError("The items parameter is not allowed on DataSelector widget.")

        self._state_name = f"nova__dataselector_{self._next_id}_state"
        self._facilities_name = f"nova__dataselector_{self._next_id}_facilities"
        self._instruments_name = f"nova__dataselector_{self._next_id}_instruments"
        self._experiments_name = f"nova__dataselector_{self._next_id}_experiments"
        self._datafiles_name = f"nova__dataselector_{self._next_id}_datafiles"

        self.create_model(facility, instrument)
        self.create_viewmodel()

        self.create_ui(facility, instrument, **kwargs)

    def create_ui(self, facility: str, instrument: str, **kwargs: Any) -> None:
        with HBoxLayout(width="100%"):
            if facility == "":
                InputField(v_model=f"{self._state_name}.facility", items=(self._facilities_name,), type="autocomplete")
            if instrument == "":
                InputField(
                    v_model=f"{self._state_name}.instrument", items=(self._instruments_name,), type="autocomplete"
                )
            InputField(v_model=f"{self._state_name}.experiment", items=(self._experiments_name,), type="autocomplete")

            super().__init__(**kwargs)
            self.items = (self._datafiles_name,)

    def create_model(self, facility: str, instrument: str) -> None:
        self._model = DataSelectorModel(facility, instrument)

    def create_viewmodel(self) -> None:
        server = get_server(None, client_type="vue3")
        binding = TrameBinding(server.state)

        self._vm = DataSelectorViewModel(self._model, binding)
        self._vm.state_bind.connect(self._state_name)
        self._vm.facilities_bind.connect(self._facilities_name)
        self._vm.instruments_bind.connect(self._instruments_name)
        self._vm.experiments_bind.connect(self._experiments_name)
        self._vm.datafiles_bind.connect(self._datafiles_name)

        self._vm.update_view()
