from starlette.middleware import Middleware
from starlette.middleware import Middleware

def test_middleware_repr() -> None:
    middleware = Middleware(CustomMiddleware, "foo", bar=123)
    assert repr(middleware) == "Middleware(CustomMiddleware, 'foo', bar=123)"


def test_middleware_iter() -> None:
    cls, args, kwargs = Middleware(CustomMiddleware, "foo", bar=123)
    assert (cls, args, kwargs) == (CustomMiddleware, ("foo",), {"bar": 123})