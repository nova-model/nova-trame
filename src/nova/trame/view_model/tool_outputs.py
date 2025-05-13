"""Module for the Tool ouputs ViewModel."""

from typing import Any

import blinker

from nova.common.job import ToolOutputs
from nova.common.signals import Signal, get_signal_id
from nova.mvvm.interface import BindingInterface


class ToolOutputsViewModel:
    """A viewmodel responsible for tool stdout and stderr."""

    def __init__(self, id: str, binding: BindingInterface):
        self.tool_outputs = ToolOutputs()
        self.tool_outputs_bind = binding.new_bind(self.tool_outputs)
        self.outputs_signal = blinker.signal(get_signal_id(id, Signal.OUTPUTS))
        self.outputs_signal.connect(self.on_outputs_update, weak=False)

    async def on_outputs_update(self, _sender: Any, outputs: ToolOutputs) -> None:
        self.tool_outputs = outputs
        self.tool_outputs_bind.update_in_view(self.tool_outputs)
