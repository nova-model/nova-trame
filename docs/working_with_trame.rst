==================
Working with Trame
==================

At it's core, Trame is going to do two things:

1. It will create and run a web server that hosts your application.
2. It will automatically generate a `Vue-based webpage <https://vuejs.org/>`_ that will connect to the web server.

++++++++++
Components
++++++++++

When building your UI, you will be working with Vue `components`. A component is a reusable block of code that implements some UI functionality. For example, in the new application from the previous section, :code:`vuetify.VBtn("Hello World")` is a component.

With Trame, you can use components both provided by Trame itself and by third-party libraries that Trame supports, such as `Vuetify <https://vuetifyjs.com/en/>`_. The full list of components available in Trame is available `here <https://trame.readthedocs.io/en/latest/trame.widgets.html>`_. We also provide a few custom components that are described in the :ref:`API <api_components>`.

To use a component, you can do the following:

.. code-block:: python

    with html.Div():
        with vuetify.VList():
            vuetify.VListItem("Item 1")
            vuetify.VListItem("Item 2")

The :code:`with` syntax will create a hierarchy of components that matches the structure of typical HTML elements. The above snippet would create an HTML div element, with a Vuetify list as a child, and two Vuetify list items as children of the list.

++++++++++++++++++
Binding Parameters
++++++++++++++++++

With Trame, and the components provided by this library, you can usually have a component parameter be set dynamically via a binding parameter.

For example, consider the following code:

.. code-block:: python

    vuetify.VBtn("Click Me!", disabled=True)

This button is not very useful, as there's no mechanism to enable the button in Python. We may also want to have the button text be set dynamically. If we use a binding, however, then both of these become possible with the following:

.. code-block:: python

    vuetify.VBtn("{{ button.label }}", disabled=("button.disabled", True))

.. note::

    In the above code, button is defined in the Trame state. In NOVA, it is added to the Trame state when you call connect() on the `nova-mvvm binding <https://nova-application-development.readthedocs.io/projects/mvvm-lib/en/latest/core_concepts/data_binding.html#how-to-use-tramebinding>`__.

When setting a component's text, we can use `handlebars syntax <https://handlebarsjs.com/guide/>`__ to reference Python variables. When setting named parameters, we use the following tuple syntax: `("variable_name", initial_value)`. The initial value can be omitted if it's not needed: `("variable_name",)`. Note that the trailing comma is necessary here for Trame to interpret this as a binding parameter due to how Python interprets tuples.

Vuetify directives, such as `v_model` and `v_if`, typically don't require using the tuple syntax.

.. code-block:: python

    vuetify.VBtn("Click Me!", v_if="button.visible")

+++++++++++++++
Layouts & Slots
+++++++++++++++

When you ran the example application, you also likely noticed that there was more content on the page than just the button component that was added. This is because of the `layout` that the button is a child of. A layout provides a
common structure for applications and defines sections of the page into which you can inject content. These sections are referred to as `slots`. In the example application, the button was added to the `content` slot of the layout, which happens to correspond to the main content area of the page.

If you want to customize a slot, you can either completely replace it or add child content to it. To replace it completely, you can do the following:

.. literalinclude:: ../src/nova/trame/view/theme/theme.py
    :start-after: slot override example
    :end-before: slot override example complete
    :dedent:

If you want to add children to a slot, you can do the following:

.. literalinclude:: ../tests/gallery/views/app.py
    :start-after: slot child example
    :end-before: slot child example complete
    :dedent:

Finally, if you want to remove a slot:

.. code-block python

    with super().create_ui() as layout:
        layout.toolbar = None  # Hide the toolbar
        layout.footer = None  # Hide the footer

The default slots that are available in our layout are shown in the image below.

.. image:: assets/layout.png
    :width: 800
    :alt: Diagram of the available slots in the default layout. The slots are: toolbar: the app bar at the top of the page, toolbar_title: the title of the app bar, actions: The right side of the app bar, pre_content: sticky content above the main content, content: the main content area, post_content: sticky content below the main content, footer: the app footer at the bottom of the page.

If within the :code:`layout.content` slot you want to build your own reusable layouts, we provide a few layout components based upon `Qt <https://doc.qt.io/qt-6/layout.html>`_ that you can use. These are described in the :ref:`API <api_layouts>`, and examples can be found :ref:`here <example_layouts>`.

Note that the :code:`layout.toolbar` and :code:`layout.footer` slots should only be completely replaced if you wish to customize them. Appending child content will likely break your page.

+++++++
Theming
+++++++

In order to give applications a consistent look and feel, all applications built with :code:`nova-trame` are based on the `Vuetify <https://vuetifyjs.com/en/>`_ framework. One of the most important features that Vuetify provides is the ability to theme your application. This allows you to easily change the colors, fonts, and other visual elements of your application. We provide two themes that we recommend you choose between depending on your needs, but you can modify or completely replace them if needed.

For details on manipulating the theming, see the :ref:`API <api_theme>`.

+++++++++++++++++++
Controlling Spacing
+++++++++++++++++++

Vuetify provides `helper classes <https://vuetifyjs.com/en/styles/spacing/#how-it-works>`_ that allow you to set the margin (space outside of your component) and padding (space inside of your component) for your component.

As an example, `ma-1` would produce a margin of 1 unit (or 4 pixels) on all sides of your component. `mb-2` would produce a margin of 2 units (or 8 pixels) below your component.

In order to use Vuetify helper classes in Trame, you can provide the `classes` argument that is available to all Trame components.

Example:

.. literalinclude:: ../tests/gallery/views/app.py
    :start-after: Vuetify class example start
    :end-before: Vuetify class example end
    :dedent:

Please note that `VTextField <https://nova-application-development.readthedocs.io/projects/nova-trame/en/latest/>`_ does not respect padding classes in Vuetify. If you need to reduce the padding of an input, you should instead switch to using a raw `Input <https://trame.readthedocs.io/en/latest/trame.widgets.html.html#trame.widgets.html.Input>`_ component.

If you want to learn more about controlling whitespace in web browsers, the `MDN page on the box model <https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model>`_ is a good reference.
