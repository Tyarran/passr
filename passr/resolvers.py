import os
import re
import logging

from pyramid.urldispatch import Route as PyramidRoute


logger = logging.getLogger(__name__)


class ReactRouterRouteResolver(object):

    def pattern_info(self, path_part):
        if not path_part.startswith(":"):
            return {"name": None, "value": path_part}
        elif path_part[-1] == "*":
            return {"name": path_part[1:-1], "value": path_part, "quantifier": "*"}
        elif path_part[-1] == "?":
            return {"name": path_part[1:-1], "value": path_part, "quantifier": "?"}
        elif path_part[-1] == "+":
            return {"name": path_part[1:-1], "value": path_part, "quantifier": "+"}
        else:
            return {"name": path_part[1:], "value": path_part, "quantifier": None}

    def convert_to_regex(self, path_info):
        if not path_info["name"]:
            return f"{path_info['value']}"
        else:
            quantifier = path_info["quantifier"] or ""
            return f"(?P<{path_info['name']}>[a-zA-Z0-9\%\-\_]+){quantifier}"

    def path_to_regex(self, path):
        result = (self.pattern_info(pattern) for pattern in path.split("/")[1:])
        converted = [self.convert_to_regex(path_info) for path_info in result]
        regex = re.compile("^\/" + "\/".join(converted) + "$")
        return regex

    def __call__(self, request, application):
        current_path = request.path
        regex = self.path_to_regex(current_path)
        for route in application.routes:
            match = regex.match(application.base_path + route["path"])
            if match:
                logger.error("Match !!! {}".format(route))
                yield route['func'], match.groupdict()
            else:
                logger.error("No Match !!!! {}".format(route))
