"""Module for the JobProgress ViewModel."""

import json
from typing import Any, Dict, Tuple

import blinker
from pydantic import BaseModel

from nova.common.job import WorkState
from nova.common.signals import Signal, get_signal_id
from nova.mvvm.interface import BindingInterface


def details_from_state(state: WorkState, details: Dict[str, Any]) -> Tuple[str, str]:
    work_state_map = {
        WorkState.NOT_STARTED: "job not started",
        WorkState.UPLOADING_DATA: "uploading data",
        WorkState.QUEUED: "job is queued",
        WorkState.RUNNING: "job is running",
        WorkState.FINISHED: "job finished",
        WorkState.ERROR: "job produced an error",
        WorkState.DELETED: "job deleted",
        WorkState.CANCELED: "job canceled",
        WorkState.STOPPING: "stopping job",
        WorkState.CANCELING: "canceling job",
    }
    if state in work_state_map:
        state_str = work_state_map[state]
    else:
        state_str = state.value

    full_details_dict = json.dumps(details.get("original_dict", {}), indent=4)
    return state_str, full_details_dict


class ProgressState(BaseModel):
    """Class that manages progress bars states."""

    progress: str = ""
    details: str = ""
    full_details: str = ""
    show_progress: bool = False
    show_full_details: bool = False
    show_failed: bool = False
    show_ok: bool = False

    def update_from_workstate(self, state: WorkState, details: Dict[str, Any]) -> None:
        progress = "0"
        match state:
            case WorkState.UPLOADING_DATA:
                progress = "10"
            case WorkState.QUEUED:
                progress = "20"
            case WorkState.RUNNING:
                progress = "50"

        self.show_progress = state in [
            WorkState.UPLOADING_DATA,
            WorkState.QUEUED,
            WorkState.RUNNING,
            WorkState.CANCELING,
            WorkState.STOPPING,
        ]
        self.show_failed = state == WorkState.ERROR
        self.show_ok = state == WorkState.FINISHED
        self.progress = progress
        self.details, self.full_details = details_from_state(state, details)
        self.show_full_details = self.full_details != "{}"


class ProgressBarViewModel:
    """A viewmodel responsible for progress bar."""

    def __init__(self, id: str, binding: BindingInterface):
        self.progress_state = ProgressState()
        self.progress_state_bind = binding.new_bind(self.progress_state)
        self.progress_signal = blinker.signal(get_signal_id(id, Signal.PROGRESS))
        self.progress_signal.connect(self.update_state, weak=False)

    async def update_state(self, _sender: Any, state: WorkState, details: Dict[str, Any]) -> None:
        self.progress_state.update_from_workstate(state, details)
        self.progress_state_bind.update_in_view(self.progress_state)
