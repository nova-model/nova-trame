"""View model implementation for the DataSelector widget."""

import os
from typing import Any, Optional

from nova.mvvm.interface import BindingInterface
from nova.trame.model.data_selector import DataSelectorModel


class DataSelectorViewModel:
    """Manages the view state of the DataSelector widget."""

    def __init__(self, model: DataSelectorModel, binding: BindingInterface) -> None:
        self.model = model

        self.state_bind = binding.new_bind(self.model.state, callback_after_update=self.update_view)
        self.facilities_bind = binding.new_bind()
        self.instruments_bind = binding.new_bind()
        self.experiments_bind = binding.new_bind()
        self.datafiles_bind = binding.new_bind()

    def set_state(self, facility: Optional[str], instrument: Optional[str], experiment: Optional[str]) -> None:
        self.model.set_state(facility, instrument, experiment)
        self.update_view()

    def update_view(self, _: Any = None) -> None:
        self.state_bind.update_in_view(self.model.state)
        self.facilities_bind.update_in_view(self.model.get_facilities())
        self.instruments_bind.update_in_view(self.model.get_instruments())
        self.experiments_bind.update_in_view(self.model.get_experiments())

        datafile_paths = self.model.get_datafiles()
        datafile_options = [{"title": os.path.basename(datafile), "value": datafile} for datafile in datafile_paths]
        self.datafiles_bind.update_in_view(datafile_options)
