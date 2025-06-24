"""ONCat backend for NeutronDataSelector."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .neutron_data_selector import NeutronDataSelectorModel, NeutronDataSelectorState


class ONCatDataSelectorState(NeutronDataSelectorState):
    """Selection state for identifying datafiles."""

    def get_facilities(self) -> List[str]:
        return []

    def get_instruments(self) -> List[str]:
        return []


class ONCatDataSelectorModel(NeutronDataSelectorModel):
    """ONCat backend for NeutronDataSelector."""

    def get_experiments(self) -> List[str]:
        return []

    def get_directories(self, _: Optional[Path] = None) -> List[Dict[str, Any]]:
        return []

    def get_datafiles(self) -> List[str]:
        return []
