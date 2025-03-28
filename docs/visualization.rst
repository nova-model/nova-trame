=============
Visualization
=============

Trame provides integrations with several libraries for 2D and 3D visualization. Below we provide recommendations for which libraries to use and examples for using each of them.

++++++++++++++++
1D & 2D Plotting
++++++++++++++++

For most use cases, we recommend that you use `Plotly <https://plotly.com/python/>`_. Kitware provides examples of how to integrate with Trame on `GitHub <https://github.com/Kitware/trame-plotly>`_.

If you have existing Matplotlib code, then we recommend you use `our MatplotlibFigure component <https://nova-application-development.readthedocs.io/projects/nova-trame/en/latest/api.html#nova.trame.view.components.visualization.MatplotlibFigure>`_. Kitware provides a direct `Matplotlib integration <https://github.com/Kitware/trame-matplotlib>`_ with Trame, but it is restricted to performing client-side rendering via SVG. Our component allows you to opt into using the `WebAgg backend <https://matplotlib.org/stable/users/explain/figure/backends.html#interactive-backends>`_ for Matplotlib.

If you need to capture complex interactions with your 2D plot, then you can use `Vega-Altair <https://altair-viz.github.io/>`_ along with our :ref:`Interactive2DPlot <api_interactive2dplot>` component.

++++++++++++++++
3D Visualization
++++++++++++++++

We recommend using `PyVista <https://pyvista.org/>`_ if you are building an app that needs 3D visualization. PyVista provides a `Tutorial <https://tutorial.pyvista.org/tutorial/09_trame/index.html>`_ that should be sufficient to get a working setup.

PyVista effectively serves as a wrapper around VTK. When working with PyVista, please ensure that you are using version 9.4 or newer of VTK. If you use an older version, your Trame app may not be able to leverage hardware acceleration while running on NOVA.

If needed, you can also use VTK directly within Trame, though we only recommend this your visualization can't be written in PyVista. If you need to do this, Kitware provides a `Trame Tutorial <https://kitware.github.io/trame/guide/tutorial/vtk.html>`_ that can help you get started.
