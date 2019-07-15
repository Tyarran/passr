import functools
import types


def if_configured(func):

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, 'is_configured'):
            raise Exception("Application not configured")
        return func(self, *args, **kwargs)

    return wrapper


class Application(object):
    routes = []

    def __init__(self, route_resolver, state_factory):
        self.route_resolver = route_resolver()
        self.state_factory = state_factory

    def configure(self, base_path):
        self.base_path = base_path
        self.is_configured = True

    @if_configured
    def get_state(self, request):
        state = self.state_factory(request, self)
        for view_obj, matchdict in self.route_resolver(request, self):
            if not isinstance(view_obj, types.FunctionType):
                state = view_obj(request=request, state=state)(**matchdict)
            else:
                state = view_obj(request=request, state=state, **matchdict)
        return state

    def route(self, name, path):
        def wrapper(func):
            self.routes.append({"name": name, "path": path, "func": func})

            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                pass

            return wrapped

        return wrapper
