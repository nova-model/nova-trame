"""View definition for the Interactive2DPlot component."""

from typing import Any, Optional

from altair import Chart
from trame.widgets import client, vega


class Interactive2DPlot(vega.Figure):
    """Creates an interactive 2D plot in Trame using Vega.

    The resulting figure's signal state will automatically be synced with Trame.
    """

    def __init__(self, figure: Optional[Chart] = None, **kwargs: Any) -> None:
        """Constructor for Interactive2DPlot."""
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
        return self.server.state[self.ref].get(name, None)

    def update(self, figure: Optional[Chart] = None, **kwargs: Any) -> None:
        super().update(figure=figure, **kwargs)

        if hasattr(self, "_start_update_handlers"):
            self._start_update_handlers()
