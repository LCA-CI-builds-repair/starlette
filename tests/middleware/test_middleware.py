from starlette.middleware import Middleware
def test_middleware_repr():
    middleware = Middleware(CustomMiddleware)
    assert repr(middleware) == "Middleware(CustomMiddleware)"
