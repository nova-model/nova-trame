================
nova-trame API
================

---------------
View Components
---------------

.. _api_layouts:

.. autoclass:: nova.trame.view.layouts.GridLayout
    :members:
    :special-members: __init__

.. autoclass:: nova.trame.view.layouts.HBoxLayout
    :members:
    :special-members: __init__

.. autoclass:: nova.trame.view.layouts.VBoxLayout
    :members:
    :special-members: __init__

.. _api_theme:

.. autoclass:: nova.trame.ThemedApp
    :members:
    :special-members: __init__

.. _api_components:

.. autoclass:: nova.trame.view.components.InputField
    :members:
    :special-members: __new__

.. autoclass:: nova.trame.view.components.RemoteFileInput
    :members:
    :special-members: __init__

.. autoclass:: nova.trame.view.components.visualization.Interactive2DPlot
    :members:
    :special-members: __init__

Future: 2D plotting class that takes 2D data and plots it. Replaces Interactive2DPlot which forces the user to build the full plot in altair.

Future: 3D plotting class that takes 3D data and plots it.

Future: Validation class that allows one to add front-end validation rules via Python.

.. autoclass:: nova.trame.view.utilities.local_storage.LocalStorageManager
    :members:
    :special-members: __init__

-------
Models
-------

Future: Class that allows loading and saving of Mantid workspaces.

Future: Validation class that allows one to manage back-end validation rules via Python.
