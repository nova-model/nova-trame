"""Unit tests for InputField."""

from nova.trame.view.components import RemoteFileInput


def test_remote_file_input() -> None:
    file_input = RemoteFileInput(v_model="test")
    assert file_input.allow_files
    assert not file_input.allow_folders


def test_open_dialog() -> None:
    file_input = RemoteFileInput(v_model="test")
    file_input.vm.open_dialog()
    assert file_input.vm.previous_value == ""
    assert file_input.vm.value == ""


def test_close_dialog() -> None:
    file_input = RemoteFileInput(v_model="test")
    file_input.vm.open_dialog()

    file_input.vm.set_value("test")
    file_input.vm.close_dialog(cancel=True)
    assert file_input.vm.previous_value == ""
    assert file_input.vm.value == file_input.vm.previous_value

    file_input.vm.set_value("test")
    file_input.vm.close_dialog()
    assert file_input.vm.previous_value == ""
    assert file_input.vm.value == "test"


def test_toggle_show_all() -> None:
    file_input = RemoteFileInput(v_model="test")
    assert not file_input.vm.showing_all_files
    file_input.vm.toggle_showing_all_files()
    assert file_input.vm.showing_all_files
    file_input.vm.toggle_showing_all_files()
    assert not file_input.vm.showing_all_files


def test_select_file() -> None:
    file_input = RemoteFileInput(v_model="test")
    file_input.vm.select_file("")
    assert file_input.vm.value == ""
    file_input.vm.select_file("/")
    assert file_input.vm.value == "/"
    assert not file_input.vm.model.valid_selection("/")
    file_input.vm.select_file("usr")
    assert file_input.vm.value == "/usr"
    file_input.vm.select_file({"path": "local"})
    assert file_input.vm.value == "/usr/local"
    file_input.vm.select_file("..")
    file_input.vm.select_file("..")
    file_input.vm.select_file("..")
    assert file_input.vm.value == ""
    file_input.vm.select_file("bogus_path")
    assert file_input.vm.value == "bogus_path"
