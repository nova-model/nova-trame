"""View model for MVVM demo of DataSelector."""

from typing import Any, Dict

from nova.mvvm.interface import BindingInterface
from tests.gallery.models.neutron_data_selector import (
    AnalysisDataSelectorState,
    NeutronDataSelectorBindingTest,
    ONCatDataSelectorState,
)


class NeutronDataSelectorVM:
    """View model for MVVM demo of NeutronDataSelector."""

    def __init__(self, binding: BindingInterface) -> None:
        self.analysis_model = AnalysisDataSelectorState()
        self.oncat_model = ONCatDataSelectorState()
        self.binding_test = NeutronDataSelectorBindingTest()

        self.analysis_bind = binding.new_bind(self.analysis_model, callback_after_update=self.on_update)
        self.oncat_bind = binding.new_bind(self.oncat_model)
        self.parameter_bind = binding.new_bind(self.binding_test, callback_after_update=self.on_parameter_update)

    def on_update(self, data: Dict[str, Any]) -> None:
        print(data, self.analysis_model)

    def on_parameter_update(self, data: Dict[str, Any]) -> None:
        print(data, self.binding_test)
