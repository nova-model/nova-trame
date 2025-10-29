### nova-trame, 1.1.1

* Passing an items parameter to InputField(type="radio") now generates a correct radio button group (thanks to John Duggan).

### nova-trame, 1.1.0

* Sort and filtering capabilities have been added to the DataSelector (thanks to John Duggan).
* Added a parameter to NeutronDataSelector to preserve selected files when changing the facility, instrument, or experiment (thanks to John Duggan).
* The v_show parameter should now be functional when used on GridLayout, HBoxLayout, and VBoxLayout (thanks to John Duggan).

### nova-trame, 1.0.1

* Exit button now attempts to close the browser tab and will be visually consistent across all themes now (thanks to John Duggan).

### nova-trame, 1.0.0

* Adds a stretch parameter to GridLayout, HBoxLayout, and VBoxLayout and overhauls how the main content slot works (thanks to John Duggan).
* This is tagged to version 1.0.0 as we are going to begin considering backwards compatibility with all future changes.

### nova-trame, 0.27.0

* DataSelector and NeutronDataSelector support range selection via Shift+Click (thanks to John Duggan).

### nova-trame, 0.26.2

* Improved the error message when a developer uses the removed NeutronDataSelector.set_state method (thanks to John Duggan).

### nova-trame, 0.26.1

* Added use_bytes parameter to FileUpload and RemoteFileInput for handling binary files that are not stored on the server (thanks to John Duggan).

### nova-trame, 0.26.0

* Added data_source and projection parameters to NeutronDataSelector to allow populating data files from ONCat (thanks to Andrew Ayres and John Duggan).

### nova-trame, 0.25.5

* NeutronDataSelector will no longer show duplicates of a file that matches multiple extensions (thanks to John Duggan).

### nova-trame, 0.25.4

* InputField, FileUpload, and RemoteFileInput should support parameter bindings now (thanks to John Duggan).

### nova-trame, 0.25.3

* Clearing NeutronDataSelector file selections will no longer send null/None values to the state (thanks to John Duggan).

### nova-trame, 0.25.2

* NeutronDataSelector should now reset its state properly when changing the instrument or experiment (thanks to John Duggan).

### nova-trame, 0.25.1

* ExecutionButtons now supports binding to stop_btn and download_btn parameters (thanks to John Duggan).

### nova-trame, 0.25.0

* FileUpload now supports a return_contents parameter (thanks to John Duggan).

### nova-trame, 0.24.1

* Fixed literalinclude paths in the documentation (thanks to John Duggan).

### nova-trame, 0.24.0

* Parameters to DataSelector and NeutronDataSelector should now support bindings (thanks to John Duggan).

### nova-trame, 0.23.1

* Added support for refreshing the file list in DataSelector and its subclasses (thanks to Yuanpeng Zhang and John Duggan).

### nova-trame, 0.23.0

* The existing DataSelector component has been renamed to NeutronDataSelector and moved to nova.trame.view.components.ornl.NeutronDataSelector (thanks to John Duggan).

### nova-trame, 0.22.1

* ThemedApp now has an Exit Button by default which closes the application and can stop any running jobs (thanks to Gregory Cage).

### nova-trame, 0.22.0

* DataSelector queries subdirectories on demand, which should improve performance for large directory trees (thanks to John Duggan).

### nova-trame, 0.21.0

* ProgressBar component now displays detailed job status (thanks to Sergey Yakubov).

### nova-trame, 0.20.5

* DataSelector should now properly display files at the root of the selected directory (thanks to John Duggan).

### nova-trame, 0.20.4

* The Tornado dependency is now pinned to >=6.5 to address a DoS vulnerability (thanks to John Duggan).

### nova-trame, 0.20.3

* Performance of the DataSelector for large numbers of files should be improved (thanks to John Duggan).

### nova-trame, 0.20.2

* Matplotlib figure will no longer raise a TypeError when running on Python >= 3.11 (thanks to John Duggan).

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
