
import pytest

from everviz import everest_hooks

def test_everest_hooks_registered():
    hook_manager = pytest.importorskip("everest.plugins.hook_manager")

    pm = hook_manager.EverestPluginManager()
    pm.register(everest_hooks)

    last_registered = pm.hook.visualize_data.get_hookimpls()[-1]
    assert last_registered.plugin_name == 'everviz.everest_hooks'
