"""View Implementation for InputField."""

from typing import Any

from trame.app import get_server
from trame.widgets import vuetify3 as vuetify
from trame_client.widgets.core import AbstractElement
from trame_server.controller import Controller


class InputField:
    """Factory class for generating Vuetify input components."""

    def __new__(cls, required: bool = False, type: str = "text", **kwargs: Any) -> AbstractElement:
        """Constructor for InputField.

        Parameters
        ----------
        required : bool
            If true, the input will be visually marked as required and a required rule will be added to the end of the
            rules list.
        type : str
            The type of input to create. This can be any of the following:

            - autocomplete
            - checkbox
            - combobox
            - file
            - input
            - otp
            - radio
            - range-slider
            - select
            - slider
            - switch
            - textarea

            Any other value will produce a text field with your type used as an HTML input type attribute.

        Returns
        -------
        `trame_client.widgets.core.AbstractElement <https://trame.readthedocs.io/en/latest/core.widget.html#trame_client.widgets.core.AbstractElement>`_
            The Vuetify input component.
        """
        if "__events" not in kwargs or kwargs["__events"] is None:
            kwargs["__events"] = []

        if isinstance(kwargs["__events"], list) and "change" not in kwargs["__events"]:
            kwargs["__events"].append(
                "change"
            )  # This must be present before each input is created or change events won't be triggered.

        match type:
            case "autocomplete":
                input = vuetify.VAutocomplete(**kwargs)
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

        cls._setup_help(input, **kwargs)

        cls._check_rules(input)
        if required:
            cls._setup_required_label(input)
            cls._setup_required_rule(input)

        cls._setup_ref(input)
        server = get_server(None, client_type="vue3")
        cls._setup_change_listener(server.controller, input)

        return input

    @staticmethod
    def _check_rules(input: AbstractElement) -> None:
        if "rules" in input._py_attr and input.rules and not isinstance(input.rules, tuple):
            raise ValueError(f"Rules for '{input.label}' must be a tuple")

    @staticmethod
    def _setup_help(_input: AbstractElement, **kwargs: Any) -> None:
        help = kwargs.get("help", None)
        if help and isinstance(help, dict):
            _input.hint = help.get("hint", None)
            _input.placeholder = help.get("placeholder", None)

    @staticmethod
    def _setup_required_label(input: AbstractElement) -> None:
        if input.label:
            input.label = f"{input.label}*"
        else:
            input.label = "*"

    @staticmethod
    def _setup_ref(input: AbstractElement) -> None:
        if "ref" not in input._py_attr or input.ref is None:
            input.ref = f"facade__{input._id}"

    @staticmethod
    def _setup_required_rule(input: AbstractElement) -> None:
        required_rule = "(value) => value?.length > 0 || 'Field is required'"
        if "rules" in input._py_attr and input.rules:
            # Existing rules will be in format ("[rule1, rule2]",) and we need to append to this list
            rule_end_index = input.rules[0].rindex("]")
            input.rules = (f"{input.rules[0][:rule_end_index]}, {required_rule}{input.rules[0][rule_end_index:]}",)
        else:
            input.rules = (f"[{required_rule}]",)

    @staticmethod
    def _setup_change_listener(ctrl: Controller, input: AbstractElement) -> None:
        base_handler = None
        if "change" in input._py_attr and input.change is not None:
            base_handler = input.change

        # Iterate over all saved refs and perform validation if there is a value that can be validated.
        change_handler = (
            "Object.values(window.trame.refs).map("
            "  (ref) => typeof ref.validate === 'function' && ref.value ? ref.validate() : null"
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
                f"{base_handler[2] if len(base_handler) > 2 else {}}"
                f"); {change_handler}"
            )  # Call the developer's provided change method via a trigger, then call ours.
        elif isinstance(base_handler, str):
            # Call the developer's provided change JS expression, then call ours.
            change_handler = f"{base_handler}; {change_handler}"

        input.change = change_handler
