import pluggy
from everviz import everest_hooks


class TestSpec:  # pylint: disable=too-few-public-methods
    """A hook specification namespace."""

    hookspec = pluggy.HookspecMarker("test")

    @hookspec(firstresult=True)
    def visualize_data(self, api):
        """
        :param :EverestAPI instance
        """


class TestManager(pluggy.PluginManager):
    """A testing plugin manager"""

    def __init__(self):
        super().__init__("test")
        self.add_hookspecs(TestSpec)


def test_everest_hooks_registered():
    pm = TestManager()
    try:
        pm.register(everest_hooks)
    except ValueError as err:
        if not str(err).startswith("Plugin already registered"):
            raise err
    assert any(
        [
            hook.plugin_name.startswith("everviz")
            for hook in pm.hook.visualize_data.get_hookimpls()
        ]
    )
