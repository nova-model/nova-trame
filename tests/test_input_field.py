"""Unit tests for InputField."""

from typing import cast

from trame.widgets import vuetify3 as vuetify

from trame_facade.components import InputField


def test_input_field() -> None:
    input_field = InputField(type="autocomplete")
    assert isinstance(input_field, vuetify.VAutocomplete)

    input_field = InputField(type="checkbox")
    assert isinstance(input_field, vuetify.VCheckbox)

    input_field = InputField(type="combobox")
    assert isinstance(input_field, vuetify.VCombobox)

    input_field = InputField(type="file")
    assert isinstance(input_field, vuetify.VFileInput)

    input_field = InputField(type="input")
    assert isinstance(input_field, vuetify.VInput)

    input_field = InputField(type="otp")
    assert isinstance(input_field, vuetify.VOtpInput)

    input_field = InputField(type="radio")
    assert isinstance(input_field, vuetify.VRadioGroup)

    input_field = InputField(type="range-slider")
    assert isinstance(input_field, vuetify.VRangeSlider)

    input_field = InputField(type="select")
    assert isinstance(input_field, vuetify.VSelect)

    input_field = InputField(type="slider")
    assert isinstance(input_field, vuetify.VSlider)

    input_field = InputField(type="switch")
    assert isinstance(input_field, vuetify.VSwitch)

    input_field = InputField(type="textarea")
    assert isinstance(input_field, vuetify.VTextarea)

    input_field = InputField(type="number")
    assert isinstance(input_field, vuetify.VTextField)


def test_invalid_rules() -> None:
    try:
        InputField(rules=42)
        raise AssertionError("Expected ValueError from invalid rules list")
    except ValueError:
        pass


def test_help() -> None:
    input_field = cast(
        vuetify.VTextField, InputField(help={"hint": "This is a hint.", "placeholder": "This is a placeholder."})
    )
    assert input_field.hint == "This is a hint."
    assert input_field.placeholder == "This is a placeholder."


def test_required() -> None:
    input_field = cast(vuetify.VTextField, InputField(required=True))
    assert input_field.label == "*"


def test_change_handlers() -> None:
    input_field = cast(vuetify.VTextField, InputField(change=lambda: print("hi")))
    assert input_field.change.startswith(f"trigger('{input_field.ref}__trigger', [], {{}});")

    input_field = cast(vuetify.VTextField, InputField(change="console.log('hi');"))
    assert input_field.change.startswith("console.log('hi');")
