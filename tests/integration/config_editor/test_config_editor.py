import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from everviz.plugins.config_editor.config_editor import ConfigEditor

everviz_config_1 = """title: Everest Optimization Report Test
pages:
- title: Page1
  content:
  - '## Testing config editor'
- title: Page2
  content:
  - '## Testing config editor'"""

everviz_config_2 = """title: Everest Optimization Report Test
pages:
- title: Page1
  content:
  - '## Testing config editor'"""


config_editor_page = """
- title: Config editor
  content:
  - ConfigEditor:
      data_path: everviz_config.yml"""


def write_text_area(driver, css_selector, text):
    """Simulate key press to clear the input."""
    elem = driver.find_element_by_css_selector(css_selector)
    (
        ActionChains(driver)
        .move_to_element(elem)
        .pause(0.2)
        .click(elem)
        .key_down(Keys.CONTROL)
        .send_keys(Keys.END)
        .key_down(Keys.SHIFT)
        .send_keys(Keys.HOME)
        .key_up(Keys.SHIFT)
        .key_up(Keys.CONTROL)
        .send_keys(Keys.DELETE)
        .send_keys(text)
    ).perform()


def test_config_editor_callback(app, dash_duo, caplog, tmpdir):
    with tmpdir.as_cwd():
        config_file = "everviz_config.yml"
        with open(config_file, "w") as f:
            f.write(everviz_config_1)

        plugin = ConfigEditor(app, config_file)
        app.layout = plugin.layout
        dash_duo.start_server(app)

        dash_duo.wait_for_text_to_equal(f"#{plugin.md_area}", everviz_config_1, 1)
        dash_duo.wait_for_contains_text(f"#{plugin.text_area}", everviz_config_1, 1)

        dash_duo.find_element(f"#{plugin.btn_edit}").click()
        time.sleep(1)
        write_text_area(dash_duo.driver, f"#{plugin.text_area}", "TEST")
        dash_duo.wait_for_contains_text(f"#{plugin.text_area}", "TEST", 1)
        dash_duo.find_element(f"#{plugin.btn_cancel}").click()
        dash_duo.wait_for_text_to_equal(f"#{plugin.md_area}", everviz_config_1, 1)
        dash_duo.wait_for_contains_text(f"#{plugin.text_area}", everviz_config_1, 1)

        dash_duo.find_element(f"#{plugin.btn_edit}").click()
        time.sleep(1)
        write_text_area(dash_duo.driver, f"#{plugin.text_area}", everviz_config_2)
        dash_duo.wait_for_contains_text(f"#{plugin.text_area}", everviz_config_2, 1)
        assert not plugin.default_conf_path.exists()

        dash_duo.find_element(f"#{plugin.btn_edit}").click()
        dash_duo.wait_for_text_to_equal(
            f"#{plugin.md_area}", everviz_config_2 + config_editor_page, 1
        )
        dash_duo.wait_for_contains_text(
            f"#{plugin.text_area}", everviz_config_2 + config_editor_page, 1
        )
        assert plugin.default_conf_path.exists()

        dash_duo.find_element(f"#{plugin.btn_edit}").click()
        time.sleep(1)
        write_text_area(dash_duo.driver, f"#{plugin.text_area}", "TEST")
        dash_duo.wait_for_contains_text(f"#{plugin.text_area}", "TEST", 1)
        dash_duo.find_element(f"#{plugin.btn_edit}").click()
        dash_duo.wait_for_text_to_equal(
            f"#{plugin.md_area}", everviz_config_2 + config_editor_page, 1
        )
        dash_duo.wait_for_contains_text(
            f"#{plugin.text_area}", everviz_config_2 + config_editor_page, 1
        )

        dash_duo.find_element(f"#{plugin.btn_reset}").click()
        dash_duo.wait_for_text_to_equal(f"#{plugin.md_area}", everviz_config_1, 1)
        dash_duo.wait_for_contains_text(f"#{plugin.text_area}", everviz_config_1, 1)

        for record in caplog.records:
            assert record.levelname != "ERROR"
