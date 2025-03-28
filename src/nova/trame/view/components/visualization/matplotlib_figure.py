"""View implementation for MatplotlibFigure."""

import json
import os
import socketserver
from asyncio import FIRST_COMPLETED, new_event_loop, set_event_loop, wait
from io import BytesIO
from mimetypes import types_map
from pathlib import Path
from threading import Thread
from typing import Any, Optional

import tornado
from aiohttp import ClientSession, WSMsgType, web
from matplotlib import get_data_path
from matplotlib.backends.backend_webagg import FigureManagerWebAgg, new_figure_manager_given_figure  # type: ignore
from matplotlib.figure import Figure
from trame.app import get_server
from trame.widgets import client, html, matplotlib
from wslink.backends.aiohttp import WebAppServer


class _MPLApplication(tornado.web.Application):
    """Tornado application compatible with Matplotlib's WebAgg backend."""

    class WebSocket(tornado.websocket.WebSocketHandler):
        """Implements the WebSocket manager for WebAgg."""

        supports_binary = True

        def check_origin(self, origin: Any) -> bool:
            return True

        def open(self, *args: Any, **kwargs: Any) -> None:
            # Register the websocket with the FigureManager.
            manager = self.application.manager  # type: ignore
            manager.add_web_socket(self)
            if hasattr(self, "set_nodelay"):
                self.set_nodelay(True)

        def on_close(self) -> None:
            # When the socket is closed, deregister the websocket with
            # the FigureManager.
            manager = self.application.manager  # type: ignore
            manager.remove_web_socket(self)

        def on_message(self, message: Any) -> None:
            # The 'supports_binary' message is relevant to the
            # websocket itself.  The other messages get passed along
            # to matplotlib as-is.

            # Every message has a "type" and a "figure_id".
            message = json.loads(message)
            if message["type"] == "supports_binary":
                self.supports_binary = message["value"]
            else:
                manager = self.application.manager  # type: ignore
                manager.handle_json(message)

        def send_json(self, content: Any) -> None:
            set_event_loop(self.application.loop)  # type: ignore
            self.write_message(json.dumps(content))

        def send_binary(self, blob: Any) -> None:
            set_event_loop(self.application.loop)  # type: ignore
            if self.supports_binary:
                self.write_message(blob, binary=True)
            else:
                data_uri = "data:image/png;base64," + blob.encode("base64").replace("\n", "")
                self.write_message(data_uri)

    def __init__(self, figure: Figure) -> None:
        self.figure = figure
        self.manager = new_figure_manager_given_figure(id(figure), figure)
        self.loop = new_event_loop()

        super().__init__([("/ws", self.WebSocket)])


class MatplotlibFigure(matplotlib.Figure):
    """Creates an interactive Matplotlib Figure using the WebAgg backend.

    By default, this will leverage the built-in Trame widget for Matplotlib support. This built-in widget can display
    poor performance for detailed plots due to it being locked into using SVG rendering.

    If you experience this, then you can use the `webagg` parameter to enable the WebAgg backend for Matplotlib. This
    will switch to server-side rendering leveraging the Anti-Grain Geometry engine.

    .. code-block:: python

        my_figure = matplotlib.figure.Figure()
        MatplotlibFigure(my_figure)  # Display SVG-based plot in Trame
        MatplotlibFigure(my_figure, webagg=True)  # Display WebAgg-based plot in Trame
    """

    mpl_initialized = False
    mpl_instances: dict[int, "MatplotlibFigure"] = {}

    @classmethod
    def _get_free_port(cls) -> int:
        with socketserver.TCPServer(("localhost", 0), None) as s:  # type: ignore
            return s.server_address[1]

    @classmethod
    def _setup_mpl(cls) -> None:
        server = get_server(None, client_type="vue3")

        @server.controller.add("on_server_bind")
        def _add_routes(wslink_server: WebAppServer) -> None:
            # matplotlib WebAgg serves JS that will reference the base URL of the application, so we need to add
            # endpoints to the main server to handle these requests.
            wslink_server.app.add_routes(
                [
                    web.get("/_images/{image}", cls._mpl_image_endpoint),
                    web.get("/download/{port}/{format}", cls._mpl_download_endpoint),
                    web.get("/mpl/{port}", cls._mpl_ws_proxy_endpoint),
                ]
            )

        # The CSS and JS files, on the other hand, can be preloaded into the page which is simpler.
        css_path = Path(FigureManagerWebAgg.get_static_file_path(), "css")
        for fname in os.listdir(css_path):
            with open(Path(css_path, fname)) as css_file:
                content = css_file.read()
                client.Style(content)
        client.Script(FigureManagerWebAgg.get_javascript())

        MatplotlibFigure.mpl_initialized = True

    @classmethod
    async def _mpl_download_endpoint(cls, request: web.Request) -> web.Response:
        # We use the websocket port to differentiate between plots if there are multiple WebAgg figures.
        port = request.match_info.get("port", "")
        format = request.match_info.get("format", "png")

        if not port or int(port) not in MatplotlibFigure.mpl_instances:
            raise web.HTTPNotFound

        instance = MatplotlibFigure.mpl_instances[int(port)]

        buff = BytesIO()
        if instance._figure:
            instance._figure.savefig(buff, format=format)
        buff.seek(0)

        return web.Response(body=buff.read(), headers={"Content-Type": types_map.get(format, "binary")})

    @classmethod
    async def _mpl_image_endpoint(cls, request: web.Request) -> web.Response:
        image_name = request.match_info.get("image", None)

        if image_name:
            try:
                with open(Path(get_data_path(), "images", image_name), mode="rb") as image_file:
                    image_data = image_file.read()
                    return web.Response(body=image_data)
            except OSError as err:
                raise web.HTTPNotFound from err

        raise web.HTTPNotFound

    @classmethod
    async def _mpl_ws_proxy_endpoint(cls, request: web.Request) -> web.WebSocketResponse:
        # The WebAgg backend assumes a tornado-based WebSocket handler, so we need to proxy it to work with Trame's
        # aiohttp setup.
        port = request.match_info.get("port", "")

        # Initialize the proxy
        ws_server = web.WebSocketResponse()
        await ws_server.prepare(request)

        # Connect to the tornado WebSocket handler
        client_session = ClientSession(cookies=request.cookies)
        async with client_session.ws_connect(
            f"http://localhost:{port}/ws",
        ) as ws_client:

            async def ws_forward(ws_from: Any, ws_to: Any) -> None:
                # The browser will send text messages for rendering requests and the server will send bytes to transmit
                # rendered image data.
                async for msg in ws_from:
                    if msg.type == WSMsgType.TEXT:
                        await ws_to.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_to.send_bytes(msg.data)
                    else:
                        raise ValueError("unexpected message type: %s", print(msg))

            # Forward websocket data in both directions
            await wait(
                [ws_forward(ws_server, ws_client), ws_forward(ws_client, ws_server)], return_when=FIRST_COMPLETED
            )
            await client_session.close()  # Ensure the connection is cleaned up when the Trame client disconnects.

            return ws_server

    def __init__(self, figure: Optional[Figure] = None, webagg: bool = False, **kwargs: Any) -> None:
        """Creates a Matplotlib figure in the Trame UI.

        Parameters
        ----------
        figure : `altair.Chart <https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html#altair.Chart>`_
            Altair chart object
        webagg : bool
            If true, then the WebAgg backend for Matplotlib is used. If not, then the default Trame matplotlib plugin
            is used.
        kwargs
            Arguments to be passed to `AbstractElement <https://trame.readthedocs.io/en/latest/core.widget.html#trame_client.widgets.core.AbstractElement>`_

        Returns
        -------
        None
        """
        self._webagg = webagg
        if webagg:
            self._port = MatplotlibFigure._get_free_port()
            if "classes" in kwargs:
                kwargs["classes"] += " nova-mpl"
            else:
                kwargs["classes"] = "nova-mpl"

            html.Div(id=f"nova_mpl_{self._port}", **kwargs)

            self._server = get_server(None, client_type="vue3")

            self._figure = figure
            self._initialized = False

            if not MatplotlibFigure.mpl_initialized:
                MatplotlibFigure._setup_mpl()
            MatplotlibFigure.mpl_instances[self._port] = self

            self.update()
        else:
            super().__init__(figure, **kwargs)

    def update(self, figure: Optional[Figure] = None) -> None:
        if self._webagg:
            if figure:
                self._figure = figure

            if self._figure is not None and not self._initialized:
                self._setup_figure_websocket()
                self._setup_figure_javascript()

                self._initialized = True

            # Re-render the figure in the UI
            if self._figure is not None:
                self._figure.canvas.draw_idle()
                self._figure.canvas.flush_events()
        else:
            super().update(figure)

    def _setup_figure_websocket(self) -> None:
        thread = Thread(target=self._mpl_run_ws_server, daemon=True)
        thread.start()

    def _setup_figure_javascript(self) -> None:
        figure_js = """
            function ondownload_%(port)d(figure, format) {
                window.open('download/%(port)d/' + format, '_blank');
            };

            function ready_%(port)d(fn) {
                if (document.getElementById("nova_mpl_%(port)d") === null) {
                    setTimeout(() => {
                        ready_%(port)d(fn);
                    }, 100);
                } else {
                    fn();
                }
            }

            ready_%(port)d(
                function() {
                    var websocket_type = mpl.get_websocket_type();
                    var websocket = new websocket_type(`ws://${window.location.host}/mpl/%(port)d`);

                    var fig = new mpl.figure(
                        // A unique numeric identifier for the figure
                        %(port)d,
                        // A websocket object (or something that behaves like one)
                        websocket,
                        // A function called when a file type is selected for download
                        ondownload_%(port)d,
                        // The HTML element in which to place the figure
                        document.getElementById("nova_mpl_%(port)d")
                    );
                }
            );
        """

        client.Script(figure_js % {"port": self._port})  # TODO

    def _mpl_run_ws_server(self) -> None:
        if not self._figure:
            return

        application = _MPLApplication(self._figure)

        http_server = tornado.httpserver.HTTPServer(application)
        sockets = tornado.netutil.bind_sockets(self._port, "")
        http_server.add_sockets(sockets)

        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.start()
