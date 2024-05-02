from starlette.middleware import Middleware


class CustomMiddleware:
    def __repr__(self):
        return f"CustomMiddleware()"

def test_middleware_repr():
    middleware = Middleware(CustomMiddleware)
    assert repr(middleware) == "CustomMiddleware()"
    assert repr(middleware) == "Middleware(CustomMiddleware)"
