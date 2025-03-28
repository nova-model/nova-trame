"""Unit tests for MatplotlibFigure."""

from matplotlib.figure import Figure

from nova.trame.view.components.visualization import MatplotlibFigure


def test_matplotlib() -> None:
    mpl_figure = Figure()

    svg_test = MatplotlibFigure()
    assert svg_test._webagg is False

    svg_test.update(None)
    svg_test.update(mpl_figure)

    webagg_test = MatplotlibFigure(webagg=True)
    assert webagg_test._webagg is True

    webagg_test.update(None)
    webagg_test.update(mpl_figure)
