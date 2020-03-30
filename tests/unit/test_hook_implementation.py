import pytest

from everviz import everest_hooks


def test_everest_hooks_registered():
    hook_manager = pytest.importorskip("everest.plugins.hook_manager")

    pm = hook_manager.EverestPluginManager()
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
