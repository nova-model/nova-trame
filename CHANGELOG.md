### nova-trame, 0.20.1

* DataSelector now supports a `show_user_directories` flag that will allow users to choose datafiles from user directories (thanks to John Duggan).

### nova-trame, 0.20.0

* Three new components are available: ExecutionButtons, ProgressBar, and ToolOutputWindows. These components allow you to quickly add widgets to your UI for running and monitoring jobs (thanks to Sergey Yakubov).

### nova-trame, 0.19.2

* InputFields using type=autoscroll now work with nested state variables (thanks to John Duggan).

### nova-trame, 0.19.1

* DataSelector now has an additional parameter `extensions` for restricting the selectable datafiles to a list of file extensions (thanks to John Duggan).

### nova-trame, 0.19.0

* You can now use `nova.trame.view.components.DataSelector` to allow the user to select a list of data files from the analysis cluster (thanks to John Duggan).

### nova-trame, 0.18.2

* Passing a string to the style parameter to GridLayout, HBoxLayout, and VBoxLayout will no longer cause Trame to crash (thanks to John Duggan).
* WebAgg-based Matplotlib figures are no longer automatically scrolled to on page load (thanks to John Duggan).
* RemoteFileInput will no longer attempt to navigate to another directory after the filtering text field loses focus. The compact UI for this widget has also been updated (thanks to John Duggan).

### nova-trame, 0.18.1

* The `CompactTheme` has been overhauled and should produce denser UIs (thanks to Kristin Maroun).

### nova-trame, 0.18.0

* You can now use `nova.trame.view.components.FileUpload` to allow the user to upload a file from their computer or pick a file off of the analysis cluster (thanks to John Duggan).
* Content placed in the `post_content` slot will now stick to the bottom of the main `content` slot instead of sticking to the bottom of the page (thanks to John Duggan).
