import base64
import json

import requests
# from pyramid.renderers import render_to_response
from pyramid.view import view_config


def factory(state_manager):
    return lambda request: state_manager


def add_ssr_application(config, name, renderer, *args, **kwargs):
    path = kwargs.pop('path')
    application = kwargs.pop("application")
    kwargs['pattern'] = f"{path}/*subpath"
    config.add_route(name, *args, factory=factory(application), **kwargs)
    config.add_view(ssr_view, route_name=name, renderer=renderer)
    application.configure(path)


def includeme(config):
    config.add_directive('add_ssr_application', add_ssr_application)


# @view_config(route_name="ssr", request_method="GET", renderer="index.jinja2")
def ssr_view(application, request):
    state = application.get_state(request)
    routes = [{"name": route["name"], "path": application.base_path + route["path"]} for route in application.routes]
    try:
        result = requests.post(
            "http://localhost:9009/render", json={"path": request.path, "state": state}
        ).content.decode("utf-8")
    except Exception:
        result = ""

    result = {
        "content": result,
        "state": base64.b64encode(json.dumps(state).encode("utf-8")).decode("utf-8"),
        "passr": {
            "routes": base64.b64encode(json.dumps(routes).encode("utf-8")).decode("utf-8")
        },
    }
    return result
    # return render_to_response(result)
# @view_config(route_name="ssr", request_method="GET", renderer="index.jinja2")
