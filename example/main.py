import sys

from example import App


def main(server=None, **kwargs):
    app = App(server)
    for arg in sys.argv[1:]:
        try:
            key, value = arg.split("=")
            kwargs[key] = int(value)
        except:
            pass
    app.server.start(**kwargs)
