"""Module for the JobProgress ViewModel."""

import asyncio
from typing import Any, Optional

import blinker
from pydantic import BaseModel

from nova.common.job import WorkState
from nova.common.signals import Signal, ToolCommand, get_signal_id
from nova.mvvm.interface import BindingInterface


def job_running(status: WorkState) -> bool:
    """A helper function to check if job is doing something in Galaxy."""
    return status in [
        WorkState.UPLOADING_DATA,
        WorkState.QUEUED,
        WorkState.RUNNING,
        WorkState.STOPPING,
        WorkState.CANCELING,
    ]


class ButtonsState(BaseModel):
    """Class that manages start/stop/cancel button states."""

    run_disabled: bool = False
    cancel_disabled: bool = True
    stop_disabled: bool = True
    download_disabled: bool = True

    stop_in_progress: bool = False
    cancel_in_progress: bool = False
    download_in_progress: bool = False

    def update_from_workstate(self, status: WorkState) -> None:
        running = job_running(status)
        self.run_disabled = running
        self.cancel_disabled = not running
        self.stop_disabled = status not in [WorkState.RUNNING, WorkState.STOPPING]
        self.stop_in_progress = status == WorkState.STOPPING
        self.cancel_in_progress = status == WorkState.CANCELING
        self.download_disabled = status != WorkState.FINISHED


class ExecutionButtonsViewModel:
    """A viewmodel responsible for execution buttons."""

    def __init__(self, id: str, binding: BindingInterface):
        self.sender_id = f"ExecutionButtonsViewModel_{id}"
        self.button_states = ButtonsState()
        self.buttons_state_bind = binding.new_bind(self.button_states)
        self.execution_signal = blinker.signal(get_signal_id(id, Signal.TOOL_COMMAND))
        self.progress_signal = blinker.signal(get_signal_id(id, Signal.PROGRESS))
        self.progress_signal.connect(self.update_state, weak=False)

    async def update_state(self, _sender: Any, state: WorkState, details: str) -> None:
        self.button_states.update_from_workstate(state)
        self.buttons_state_bind.update_in_view(self.button_states)

    async def run(self) -> None:
        # disable run now since it might take some time before the client updates the status
        self.button_states.run_disabled = True
        self.buttons_state_bind.update_in_view(self.button_states)
        await self.execution_signal.send_async(self.sender_id, command=ToolCommand.START)

    async def cancel(self) -> None:
        await self.execution_signal.send_async(self.sender_id, command=ToolCommand.CANCEL)

    async def stop(self) -> None:
        await self.execution_signal.send_async(self.sender_id, command=ToolCommand.CANCEL)

    async def prepare_results(self) -> Optional[bytes]:
        self.button_states.download_in_progress = True
        self.buttons_state_bind.update_in_view(self.button_states)
        await asyncio.sleep(0.5)  # to give Trame time to update view
        responses = await self.execution_signal.send_async(self.sender_id, command=ToolCommand.GET_RESULTS)
        res = None
        for response in responses:  # responses can come from multiple places
            if response[1] is None:
                continue
            if response[1]["sender"] == self.sender_id and response[1]["command"] == ToolCommand.GET_RESULTS:
                res = response[1]["results"]
        self.button_states.download_in_progress = False
        self.buttons_state_bind.update_in_view(self.button_states)
        return res
