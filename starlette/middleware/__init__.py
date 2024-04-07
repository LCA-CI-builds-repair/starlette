import typing

class Middleware:
def __init__(self, app: MiddlewareStack, cls: type, **options: typing.Any) -> None:
self.app = app
self.cls = cls
self.options = options

def __repr__(self) -> str:
class_name = self.__class__.__name__
option_strings = [f"{key}={value!r}" for key, value in self.options.items()]
args_repr = ", ".join([self.cls.__name__, 'app=self.app'])
return f"{class_name}({args_repr})"
