"""View implementation for Interactive2DPlot."""

from typing import Any, Optional

from altair import Chart
from trame.widgets import client, vega


class Interactive2DPlot(vega.Figure):
    """Creates an interactive 2D plot in Trame using Vega.

    Trame provides two primary mechanisms for composing 2D plots: `Plotly <https://github.com/Kitware/trame-plotly>`_
    and `Vega-Lite/Altair <https://github.com/Kitware/trame-vega>`_. If you only need static plots or basic browser
    event handling, then please use these libraries directly.

    If you need to capture complex front-end interactions, then you can
    use our provided Interactive2DPlot widget that is based on Vega-Lite. This uses the same API as Trame's vega.Figure,
    except that it will automatically sync Vega's signal states as the user interacts with the plot.

    The following allows the user to select a region of the plot and tracks the selected region in Python:

    .. literalinclude:: ../tests/test_interactive_2d_plot.py
        :start-after: setup 2d plot
        :end-before: setup 2d plot complete
        :dedent:
    """

    def __init__(self, figure: Optional[Chart] = None, **kwargs: Any) -> None:
        """Constructor for Interactive2DPlot.

        Parameters
        ----------
        figure : `altair.Chart <https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html#altair.Chart>`_
            Altair chart object
        kwargs
            Arguments to be passed to `AbstractElement <https://trame.readthedocs.io/en/latest/core.widget.html#trame_client.widgets.core.AbstractElement>`_

        Returns
        -------
        None
        """
        self._initialized = False

        super().__init__(figure=figure, **kwargs)
        self.ref = f"facade__vega_{self._id}"
        self.server.state[self.ref] = {}
        self._start_update_handlers = client.JSEval(
            exec=(
                "async () => {"
                f" let ref = window.trame.refs['{self.ref}'];"
                "  await ref.mountVis();"  # wait for the new  visualization to be rendered in the front-end
                "  if (ref.viz === undefined) { return; }"  # If the component is not mounted, do nothing
                "  for (const [key, value] of Object.entries(ref.viz.view._signals)) {"
                "    if (key === 'unit') { continue; }"  # this causes a JSError for some reason if not skipped
                "    ref.viz.view.addSignalListener(key, (name, value) => {"
                f"     window.trame.state.state['{self.ref}'][name] = value;"  # sync front-end state
                f"     flushState('{self.ref}');"  # sync back-end state
                "    })"
                "  }"
                "}"
            )
        ).exec

        client.ClientTriggers(mounted=self.update)

    def get_signal_state(self, name: str) -> Any:
        """Retrieves a Vega signal's state by name.

        Parameters
        ----------
        name : str
            The name of the signal to retrieve.

        Returns
        -------
        typing.Any
            The current value of the Vega signal.
        """
        return self.server.state[self.ref].get(name, None)

    def update(self, figure: Optional[Chart] = None, **kwargs: Any) -> None:
        super().update(figure=figure, **kwargs)

        if hasattr(self, "_start_update_handlers"):
            self._start_update_handlers()
