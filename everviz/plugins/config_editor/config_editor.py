import base64
import io
import os
from pathlib import Path
from uuid import uuid4
import yaml
from dash import callback_context
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
from everviz.plugins.plugin_abc import EvervizPluginABC


class ConfigEditor(EvervizPluginABC):
    """
    Webviz plugin designed to allow the user to edit a everviz config file.
     Plugin supports the following functionality, allow the user to:
     * Edit the content of the config file and save the changes
       only if the result is a valid everviz config file
     * Rest to the initial version of the config file.
     * Upload content from a local file.
    """

    def __init__(self, app, data_path, title="Configuration"):
        super().__init__()
        self.title = title
        self.data_path = data_path
        self.text_area = f"txt_area-{uuid4()}"
        self.md_area = f"md_area-{uuid4()}"
        self.editor_buttons = f"editor_buttons-{uuid4()}"
        self.btn_edit = f"btn_edit-{uuid4()}"
        self.btn_cancel = f"btn_cancel-{uuid4()}"
        self.btn_upload = f"btn_upload-{uuid4()}"
        self.btn_reset = f"btn_reset-{uuid4()}"
        self.config_component = f"config_component-{uuid4()}"
        self.editing = False
        self.default_conf_path = Path(self.data_path).parent / "default"
        self.default_conf = yaml.safe_load(self.get_config_str())
        self.set_callbacks(app)

    def get_config_str(self):
        with open(self.data_path, "r") as f:
            return f.read()

    @staticmethod
    def write_config(config, path):
        with open(path, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

    def update_everviz_config(self, new_config_text):
        new_config = yaml.safe_load(new_config_text)
        old_config = yaml.safe_load(self.get_config_str())
        if isinstance(new_config, dict) and old_config != new_config:
            pages = new_config.get("pages", [])
            if len(pages) > 0:
                # Ensure the config editor page is always part of the config
                conf_ed_content = {
                    "ConfigEditor": {
                        "data_path": self.data_path,
                    },
                }
                # Check if the ConfigEditor plugin is part of the configuration
                found = next(
                    (page for page in pages if page["content"] == [conf_ed_content]),
                    None,
                )
                if not found:
                    pages.append(
                        {"title": "Config editor", "content": [conf_ed_content]}
                    )
                if not self.default_conf_path.exists():
                    self.write_config(self.default_conf, self.default_conf_path)
                self.write_config(new_config, self.data_path)

    def render_text_component(self):
        config_str = self.get_config_str()
        if self.editing:
            style = {"width": "100%", "height": 800}
            return [
                dcc.Textarea(
                    id=self.text_area,
                    value=config_str,
                    style=style,
                )
            ]

        md_content = f"""```
{config_str}
```
"""
        return [
            dcc.Textarea(
                id=self.text_area,
                value=config_str,
                hidden=not self.editing,
            ),
            dcc.Markdown(
                id=self.md_area,
                children=md_content,
            ),
        ]

    def render_buttons(self):
        if not self.editing:
            return [
                html.Button("Edit", id=self.btn_edit),
                # Had to wrap the button in a div because the hidden option was not
                # working on the button element
                html.Div(
                    [
                        html.Button("Cancel", id=self.btn_cancel),
                    ],
                    hidden=True,
                ),
                html.Div(
                    dcc.Upload(html.Button("Upload File"), id=self.btn_upload),
                    style={
                        "display": "inline-block",
                    },
                ),
                html.Div(
                    [
                        html.Button("Reset", id=self.btn_reset),
                    ],
                    hidden=not self.default_conf_path.exists(),
                ),
            ]
        return [
            html.Button("Save", id=self.btn_edit),
            html.Button("Cancel", id=self.btn_cancel),
            html.Div(
                html.Button(
                    "Reset",
                    id=self.btn_reset,
                ),
                hidden=True,
            ),
            dcc.Upload(children=None, id=self.btn_upload),
        ]

    @property
    def layout(self):
        return html.Div(
            [
                html.H1(
                    children=self.title,
                    style={"textAlign": "center"},
                ),
                html.Div(
                    [
                        html.Div(
                            id=self.config_component,
                            children=self.render_text_component(),
                            style={
                                "width": "100%",
                                "height": "100%",
                                "display": "inline-block",
                            },
                        ),
                        html.Div(
                            id=self.editor_buttons,
                            children=self.render_buttons(),
                            style={"textAlign": "center"},
                        ),
                    ]
                ),
            ]
        )

    def set_callbacks(self, app):
        @app.callback(
            [
                Output(self.config_component, "children"),
                Output(self.editor_buttons, "children"),
            ],
            [
                Input(self.btn_cancel, "n_clicks"),
                Input(self.btn_edit, "n_clicks"),
                Input(self.btn_reset, "n_clicks"),
                Input(self.btn_upload, "contents"),
            ],
            [State(self.text_area, "value")],
        )
        def update_layout(
            cancel_clicks, edit_clicks, reset_clicks, upload_content, value
        ):
            changed_id = [p["prop_id"] for p in callback_context.triggered][0]
            if edit_clicks and self.btn_edit in changed_id:
                if self.editing:
                    self.update_everviz_config(value)
                self.editing = not self.editing
            elif cancel_clicks and self.btn_cancel in changed_id:
                if self.editing:
                    self.editing = not self.editing
            elif reset_clicks and self.btn_reset in changed_id:
                os.rename(self.default_conf_path, self.data_path)

            elif upload_content is not None:
                content_type, content_string = upload_content.split(",")
                decoded = base64.b64decode(content_string).decode("utf-8")
                new_config = "".join(io.StringIO(decoded).readlines())

                self.update_everviz_config(new_config)

            return self.render_text_component(), self.render_buttons()
