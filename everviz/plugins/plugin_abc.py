from pathlib import Path
import abc
import pkg_resources
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
        ASSETS_DIR = Path(pkg_resources.resource_filename("everviz", "assets"))
        WEBVIZ_ASSETS.add(ASSETS_DIR / "axis_customization.css")

    def plugin_name(self):
        name = map(lambda c: f"_{c.lower()}" if c.isupper() else c, type(self).__name__)
        return "everviz" + "".join(name)

    @property
    @abc.abstractmethod
    def layout(self):
        """This is the only required function of a Webviz plugin.
        It returns a Dash layout which by webviz-config is added to
        the main Webviz application.
        """
