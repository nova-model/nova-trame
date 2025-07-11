"""Internal utilities for nova-trame."""

from typing import Any, Tuple, Union

from trame_server.core import State

from nova.mvvm._internal.utils import rgetdictvalue, rsetdictvalue


# Reads a state parameter from Trame. For internal use only, if you're using this in your application you're violating
# the MVVM framework. :)
def get_state_param(state: State, value: Union[Any, Tuple]) -> Any:
    if isinstance(value, tuple):
        return rgetdictvalue(state, value[0])

    return value


# Writes a state parameter to Trame. For internal use only, if you're using this in your application you're violating
# the MVVM framework. :)
def set_state_param(state: State, value: Union[Any, Tuple], new_value: Any = None) -> Any:
    with state:
        if isinstance(value, tuple):
            if new_value is not None:
                rsetdictvalue(state, value[0], new_value)
            elif len(value) > 1:
                rsetdictvalue(state, value[0], value[1])
            state.dirty(value[0].split(".")[0])

    return get_state_param(state, value)
