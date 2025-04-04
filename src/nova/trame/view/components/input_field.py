"""View Implementation for InputField."""

import logging
import os
import re
from enum import Enum
from typing import Any, Dict, Optional, Union

from trame.app import get_server
from trame.widgets import client
from trame.widgets import vuetify3 as vuetify
from trame_client.widgets.core import AbstractElement
from trame_server.controller import Controller
from trame_server.state import State

from nova.mvvm.pydantic_utils import get_field_info

logger = logging.getLogger(__name__)


class InputField:
    """Factory class for generating Vuetify input components."""

    @staticmethod
    def create_boilerplate_properties(
        v_model: Optional[Union[tuple[str, Any], str]], field_type: str, debounce: int, throttle: int
    ) -> dict:
        if debounce == -1:
            debounce = int(os.environ.get("NOVA_TRAME_DEFAULT_DEBOUNCE", 0))
        if throttle == -1:
            throttle = int(os.environ.get("NOVA_TRAME_DEFAULT_THROTTLE", 0))

        if not v_model:
            return {}
        if isinstance(v_model, tuple):
            field = v_model[0]
        else:
            field = v_model
        object_name_in_state = field.split(".")[0]
        field_info = None
        try:
            field_name = ".".join(field.split(".")[1:])
            if "[" in field_name:
                index_field_name = re.sub(r"\[.*?\]", "[0]", field_name)
                field_info = get_field_info(f"{object_name_in_state}.{index_field_name}")
                if "[" in field_name and "[index]" not in field_name:
                    field_info = None
                    logger.warning(
                        f"{field}: validation ignored. We currently only "
                        f"support single loop with index variable that should be called 'index'"
                    )
            else:
                field_info = get_field_info(field)
        except Exception as _:
            pass
        label = ""
        help_dict: dict = {}
        placeholder = None
        if field_info:
            label = field_info.title
            if field_info.examples and len(field_info.examples) > 0:
                placeholder = field_info.examples[0]
            help_dict = {"hint": field_info.description, "placeholder": placeholder}

        args: Dict[str, Any] = {}
        if v_model:
            args |= {"v_model": v_model, "label": label, "help": help_dict}
            if field_info:
                args |= {
                    "rules": (f"[(v) => trigger('validate_pydantic_field', ['{field}', v, index])]",),
                }

                if field_type in ["autocomplete", "combobox", "select"] and issubclass(field_info.annotation, Enum):
                    args |= {"items": str([option.value for option in field_info.annotation])}

            if debounce > 0 and throttle > 0:
                raise ValueError("debounce and throttle cannot be used together")

            if debounce > 0:
                args |= {
                    "update_modelValue": (
                        "window.delay_manager.debounce("
                        f"  '{v_model}',"
                        f"  () => flushState('{object_name_in_state}'),"
                        f"  {debounce}"
                        ")"
                    )
                }
            elif throttle > 0:
                args |= {
                    "update_modelValue": (
                        "window.delay_manager.throttle("
                        f"  '{v_model}',"
                        f"  () => flushState('{object_name_in_state}'),"
                        f"  {throttle}"
                        ")"
                    )
                }
            else:
                args |= {"update_modelValue": f"flushState('{object_name_in_state}')"}
        return args

    def __new__(
        cls,
        v_model: Optional[Union[tuple[str, Any], str]] = None,
        required: bool = False,
        debounce: int = -1,
        throttle: int = -1,
        type: str = "text",
        **kwargs: Any,
    ) -> AbstractElement:
        """Constructor for InputField.

        Parameters
        ----------
        v_model : tuple[str, Any] or str, optional
            The v-model for this component. If this references a Pydantic configuration variable, then this component
            will attempt to load a label, hint, and validation rules from the configuration for you automatically.
        required : bool
            If true, the input will be visually marked as required and a required rule will be added to the end of the
            rules list.
        debounce : int
            Number of milliseconds to wait after the last user interaction with this field before attempting to update
            the Trame state. If set to 0, then no debouncing will occur. If set to -1, then the environment variable
            `NOVA_TRAME_DEFAULT_DEBOUNCE` will be used to set this (defaults to 0). See the `Lodash Docs
            <https://lodash.com/docs/4.17.15#debounce>`__ for details.
        throttle : int
            Number of milliseconds to wait between updates to the Trame state when the user is interacting with this
            field. If set to 0, then no throttling will occur. If set to -1, then the environment variable
            `NOVA_TRAME_DEFAULT_THROTTLE` will be used to set this (defaults to 0). See the `Lodash Docs
            <https://lodash.com/docs/4.17.15#throttle>`__ for details.
        type : str
            The type of input to create. This can be any of the following:

            - autocomplete - Produces a dropdown menu that supports autocompletion as the user types. Items can be \
                automatically populated (see select option for details).
            - autoscroll - Produces a textarea that automatically scrolls to the bottom as new content is added.
            - checkbox
            - combobox - Produces a dropdown menu that supports autocompletion as the user types and allows users to \
                add new items. Items can be automatically populated (see select option for details).
            - file
            - input
            - otp
            - radio
            - range-slider
            - select - Produces a dropdown menu. This menu can have items automatically populated if the v_model is \
                connected to a Pydantic field that uses an Enum type. Otherwise, you must specify the items parameter \
                to `InputField`.

                .. literalinclude:: ../tests/test_input_field.py
                    :start-after: items autopopulation start
                    :end-before: items autopopulation end
                    :dedent:

                .. code-block:: python

                    InputField(v_model="dropdown.enum_field", type="select")

            - slider
            - switch
            - textarea

            Any other value will produce a text field with your type used as an HTML input type attribute.
        **kwargs
            All other arguments will be passed to the underlying
            `Trame Vuetify component <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html>`_.
            The following example would set the auto_grow and label attributes on
            `VTextarea <https://trame.readthedocs.io/en/latest/trame.widgets.vuetify3.html#trame.widgets.vuetify3.VTextarea>`_:

            .. literalinclude:: ../tests/gallery/app.py
                :start-after: InputField kwargs example start
                :end-before: InputField kwargs example end
                :dedent:

        Returns
        -------
        `trame_client.widgets.core.AbstractElement <https://trame.readthedocs.io/en/latest/core.widget.html#trame_client.widgets.core.AbstractElement>`_
            The Vuetify input component.
        """
        server = get_server(None, client_type="vue3")

        kwargs = {**cls.create_boilerplate_properties(v_model, type, debounce, throttle), **kwargs}

        if "__events" not in kwargs or kwargs["__events"] is None:
            kwargs["__events"] = []

        # This must be present before each input is created or change events won't be triggered.
        if isinstance(kwargs["__events"], list):
            if "blur" not in kwargs["__events"]:
                kwargs["__events"].append("blur")
            if "change" not in kwargs["__events"]:
                kwargs["__events"].append("change")
            if "scroll" not in kwargs["__events"]:
                kwargs["__events"].append("scroll")

        match type:
            case "autocomplete":
                input = vuetify.VAutocomplete(**kwargs)
            case "autoscroll":
                input = vuetify.VTextarea(**kwargs)
                cls._setup_autoscroll(server.state, input)
            case "checkbox":
                input = vuetify.VCheckbox(**kwargs)
            case "combobox":
                input = vuetify.VCombobox(**kwargs)
            case "file":
                input = vuetify.VFileInput(**kwargs)
            case "input":
                input = vuetify.VInput(**kwargs)
            case "otp":
                input = vuetify.VOtpInput(**kwargs)
            case "radio":
                input = vuetify.VRadioGroup(**kwargs)
            case "range-slider":
                input = vuetify.VRangeSlider(**kwargs)
            case "select":
                items = kwargs.pop("items", None)
                if isinstance(items, str):
                    items = (items,)
                input = vuetify.VSelect(items=items, **kwargs)
            case "slider":
                input = vuetify.VSlider(**kwargs)
            case "switch":
                input = vuetify.VSwitch(**kwargs)
            case "textarea":
                input = vuetify.VTextarea(**kwargs)
            case _:
                input = vuetify.VTextField(type=type, **kwargs)

        cls._setup_ref(input)
        cls._setup_help(input, **kwargs)

        cls._check_rules(input)
        if required:
            cls._setup_required_label(input)
            cls._setup_required_rule(input)

        cls._setup_event_listeners(server.controller, input)

        return input

    @staticmethod
    def _check_rules(input: AbstractElement) -> None:
        if "rules" in input._py_attr and input.rules and not isinstance(input.rules, tuple):
            raise ValueError(f"Rules for '{input.label}' must be a tuple")

    @staticmethod
    def _setup_autoscroll(state: State, input: AbstractElement) -> None:
        if input.v_model:
            if "id" not in input._py_attr or input.id is None:
                input.id = f"nova__{input._id}"
                input.scroll = f"window.nova__autoscroll('{input.id}');"

            with state:
                if state["nova_scroll_position"] is None:
                    state["nova_scroll_position"] = {}
                state.nova_scroll_position[input.id] = 0

            autoscroll = client.JSEval(
                exec=(
                    "if (window.nova__autoscroll !== undefined) {"
                    # If the autoscroll function already exists, call it.
                    "  window.nova__autoscroll($event);"
                    "} else {"
                    # Save the JS so it can be called from outside of this script (ie during a scroll event).
                    "  window.nova__autoscroll = function(id) {"
                    # Get the element in the browser by ID
                    "    const element = window.document.querySelector(`#${id}`);"
                    # If the user is at the bottom of the textarea, then we should autoscroll.
                    "    if (element.scrollTop === window.trame.state.state.nova_scroll_position[id]) {"
                    # Scroll to the bottom
                    "      element.scrollTop = element.scrollHeight;"
                    # Save the new scroll position
                    "      window.trame.state.state.nova_scroll_position[id] = element.scrollTop;"
                    "      flushState('nova_scroll_position');"
                    # If the user has scrolled back to the bottom, then we should reenable scrolling.
                    "    } else if (element.scrollTop === element.scrollHeight - element.clientHeight) {"
                    # Save the new scroll position
                    "      window.trame.state.state.nova_scroll_position[id] = element.scrollTop;"
                    "      flushState('nova_scroll_position');"
                    "    }"
                    "  };"
                    "  window.nova__autoscroll($event);"
                    "}"
                )
            ).exec

            @state.change(input.v_model)
            def _autoscroll(**kwargs: Any) -> None:
                autoscroll(input.id)

    @staticmethod
    def _setup_help(_input: AbstractElement, **kwargs: Any) -> None:
        help = kwargs.get("help", None)
        if help and isinstance(help, dict):
            _input.placeholder = help.get("placeholder", None)
            _input.title = help.get("hint", None)

    @staticmethod
    def _setup_required_label(input: AbstractElement) -> None:
        if input.label:
            input.label = f"{input.label}*"
        else:
            input.label = "*"

    @staticmethod
    def _setup_ref(input: AbstractElement) -> None:
        if "ref" not in input._py_attr or input.ref is None:
            input.ref = f"nova__{input._id}"

    @staticmethod
    def _setup_required_rule(input: AbstractElement) -> None:
        # The rule needs to check that 1. the input has been touched by the user, and 2. the input is not empty.
        required_rule = (
            f"(value) => (!window.trame.refs['{input.ref}'].touched || value?.length > 0) || 'Field is required'"
        )
        if "rules" in input._py_attr and input.rules:
            # Existing rules will be in format ("[rule1, rule2]",) and we need to append to this list
            rule_end_index = input.rules[0].rindex("]")
            input.rules = (f"{input.rules[0][:rule_end_index]}, {required_rule}{input.rules[0][rule_end_index:]}",)
        else:
            input.rules = (f"[{required_rule}]",)

    @staticmethod
    def _setup_event_listeners(ctrl: Controller, input: AbstractElement) -> None:
        base_handler = None
        if "change" in input._py_attr and input.change is not None:
            base_handler = input.change

        # Iterate over all saved refs and perform validation if there is a value that can be validated.
        change_handler = (
            "Object.values(window.trame.refs).map("
            "  (ref) => ref && typeof ref.validate === 'function' && ref.value ? ref.validate() : null"
            ");"
        )

        # We need to coerce the developer's change handler, which could be a string, callable, or tuple containing a
        # callable, to a single string to be compatible with our change handler.
        if callable(base_handler):
            base_handler = (base_handler,)
        if isinstance(base_handler, tuple):

            @ctrl.trigger(f"{input.ref}__trigger")
            def _(*args: str, **kwargs: Any) -> None:
                base_handler[0](*args, **kwargs)

            change_handler = (
                "trigger("
                f"'{input.ref}__trigger', "
                f"{base_handler[1] if len(base_handler) > 1 else []}, "
                f"{base_handler[2] if len(base_handler) > 2 else {} }"
                f"); {change_handler}"
            )  # Call the developer's provided change method via a trigger, then call ours.
        elif isinstance(base_handler, str):
            # Call the developer's provided change JS expression, then call ours.
            change_handler = f"{base_handler}; {change_handler}"

        # The user touched the input, so we can enable the required rule.
        input.blur = f"window.trame.refs['{input.ref}'].touched = true"
        input.change = change_handler
