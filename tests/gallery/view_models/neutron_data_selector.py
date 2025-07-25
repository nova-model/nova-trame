"""View model for MVVM demo of DataSelector."""

from typing import Any, Dict

from nova.mvvm.interface import BindingInterface
from tests.gallery.models.neutron_data_selector import NeutronDataSelectorBindingTest, NeutronDataSelectorState


class NeutronDataSelectorVM:
    """View model for MVVM demo of NeutronDataSelector."""

    def __init__(self, binding: BindingInterface) -> None:
        self.model = NeutronDataSelectorState()
        self.binding_test = NeutronDataSelectorBindingTest()

        self.model_bind = binding.new_bind(self.model, callback_after_update=self.on_update)
        self.parameter_bind = binding.new_bind(self.binding_test, callback_after_update=self.on_parameter_update)

    def on_update(self, data: Dict[str, Any]) -> None:
        print(data, self.model)

    def on_parameter_update(self, data: Dict[str, Any]) -> None:
        print(data, self.binding_test)
