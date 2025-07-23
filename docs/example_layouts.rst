===============
Example Layouts
===============

.. _example_layouts:

----------
GridLayout
----------
By default, each item in a GridLayout will take up one row and one column. This can be changed by setting the row_span and column_span properties of the item.

.. literalinclude:: ../tests/gallery/views/app.py
    :start-after: grid row and column span example
    :end-before: grid row and column span example end
    :dedent:

Result:

.. image:: assets/example_layouts/spans.png
    :width: 400
    :alt: GridLayout containings cells that span multiple rows and columns.

--------------------------
GridLayout with whitespace
--------------------------
Trying this with HBoxLayout or VBoxLayout will produce unpredictable behavior.

.. literalinclude:: ../tests/gallery/views/app.py
    :start-after: whitespace example
    :end-before: whitespace example end
    :dedent:

Result:

.. image:: assets/example_layouts/whitespace.png
    :width: 400
    :alt: GridLayout containing cells that alternate between cells containing whitespace and content.

--------------------------------
HBoxLayout containing VBoxLayout
--------------------------------

.. literalinclude:: ../tests/gallery/views/app.py
    :start-after: mixed boxes example 1
    :end-before: mixed boxes example 1 end
    :dedent:

Result:

.. image:: assets/example_layouts/hbox_vbox.png
    :width: 400
    :alt: HBoxLayout containing VBoxLayouts.

--------------------------------
VBoxLayout containing HBoxLayout
--------------------------------

.. literalinclude:: ../tests/gallery/views/app.py
    :start-after: mixed boxes example 2
    :end-before: mixed boxes example 2 end
    :dedent:

Result:

.. image:: assets/example_layouts/vbox_hbox.png
    :width: 400
    :alt: VBoxLayout containing HBoxLayouts.

--------------------------------
GridLayout containing BoxLayouts
--------------------------------

.. literalinclude:: ../tests/gallery/views/app.py
    :start-after: mixed boxes example 3
    :end-before: mixed boxes example 3 end
    :dedent:

Result:

.. image:: assets/example_layouts/grid_boxes.png
    :width: 400
    :alt: GridLayout containing BoxLayouts.
