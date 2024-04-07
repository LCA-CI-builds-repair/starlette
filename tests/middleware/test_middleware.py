from starlette.middleware import Middleware


class CustomMiddleware:
    def __init__(self, app: Any, **options: typing.Any) -> None:
        self.app = app
        self.options = options

    def __iter__(self) -> typing.Iterator[typing.Any]:
        as_tuple = (self.app, self.options)
        return iter(as_tuple)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        option_strings = [f"{key}={value!r}" for key, value in self.options.items()]
        args_repr = ", ".join([self.app.__class__.__name__] + option_strings)
        return f"{class_name}({args_repr})"
