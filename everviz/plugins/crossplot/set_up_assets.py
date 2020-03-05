import flask


def set_up_assets(app, ASSETS_DIR):
    # We do this because webwiz currently doesn't give a way to serve
    # css when running in non portable mode.
    app.css.config.serve_locally = False

    @app.server.route("/static/<resource>")
    def serve_static(resource):
        return flask.send_from_directory(ASSETS_DIR, resource)

    app.css.append_css(
        {"external_url": "/static/axis_customization.css",}
    )
