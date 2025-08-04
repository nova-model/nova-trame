"""Internal utilities for nova-trame."""

from typing import Any, Tuple, Union

from trame_server.core import State

from nova.mvvm._internal.utils import rgetdictvalue, rsetdictvalue


# Trame state handlers don't work on nested properties. When writing Trame state handlers (e.g. flushState, dirty, or
# change), we instead use the name of the top-level property. For example, "config.parameter_group_a.option_x" becomes
# "config".
def get_state_name(name: str) -> str:
    return name.split(".")[0]


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
            state.dirty(get_state_name(value[0]))

    return get_state_param(state, value)
