import abc
from importlib.resources import files

from webviz_config import WebvizPluginABC
from webviz_config.webviz_assets import WEBVIZ_ASSETS


class EvervizPluginABC(WebvizPluginABC):
    """Subclass of the WebvizPluginABC base class
    All everviz-webviz plugins should be subclasses of this base class
    e.g.
    ```python
    class MyPlugin(EvervizPluginABC):

        def __init__(self):
            super().__init__()

    ```
    """

    def __init__(self):
        super().__init__()
        self._screenshot_filename = f"{self.plugin_name()}.png"
        ASSETS_DIR = files("everviz").joinpath("assets")
        WEBVIZ_ASSETS.add(ASSETS_DIR / "axis_customization.css")

    def plugin_name(self):
        name = (f"_{c.lower()}" if c.isupper() else c for c in type(self).__name__)
        return "everviz" + "".join(name)

    @property
    @abc.abstractmethod
    def layout(self):
        """This is the only required function of a Webviz plugin.
        It returns a Dash layout which by webviz-config is added to
        the main Webviz application.
        """
