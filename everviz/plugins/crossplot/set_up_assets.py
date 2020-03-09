import flask


def set_up_assets(app, ASSETS_DIR):
    # We do this because webwiz currently doesn't give a way to serve
    # css when running in non portable mode.
    route = "/static/<resource>"
    if _asset_routed(app, route):
        return

    app.css.config.serve_locally = False

    @app.server.route(route)
    def serve_static(resource):
        return flask.send_from_directory(ASSETS_DIR, resource)

    app.css.append_css(
        {"external_url": "/static/axis_customization.css",}
    )


def _asset_routed(app, route):
    for rule in app.server.url_map.iter_rules():
        if route in rule.rule:
            return True
    return False
