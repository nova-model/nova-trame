"""Unit tests for InputField."""

from time import sleep
from typing import cast

from pydantic import BaseModel, Field
from selenium.webdriver import Firefox
from trame.app import get_server
from trame.widgets import vuetify3 as vuetify
from trame_server import Server

from nova.mvvm.trame_binding import TrameBinding
from nova.trame import ThemedApp
from nova.trame.view.components import InputField


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


def test_pydantic() -> None:
    class User(BaseModel):
        username: str = Field(
            default="test_name", min_length=1, title="User Name", description="hint", examples=["user"]
        )

    obj = User()

    class MyTrameApp(ThemedApp):
        def __init__(self, server: Server = None) -> None:
            server = get_server(None, client_type="vue3")
            super().__init__(server=server)
            binding = TrameBinding(server.state).new_bind(obj)
            binding.connect("obj")
            self.create_ui()

        def create_ui(self) -> None:
            with super().create_ui() as layout:
                with layout.content:
                    input_field = cast(vuetify.VTextField, InputField(v_model="obj.username"))
                    assert input_field.hint == "hint"
                    assert input_field.label == "User Name"
                    assert input_field.placeholder == "user"

    MyTrameApp()


def test_pydantic_validation(driver: Firefox) -> None:
    sleep(1)
    driver.execute_script("window.trame.refs['pydantic-field'].validate();")
    sleep(1)
    error_message = driver.execute_script("""
        const messages_content = document.getElementById("pydantic-field-messages");

        return messages_content.textContent;
    """)

    assert error_message.startswith("Input should be a valid integer")


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
