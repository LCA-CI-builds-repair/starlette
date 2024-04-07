from starlette.middleware import Middleware, MiddlewareStack
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware:
async def __aenter__(self):
return self

async def __aexit__(self, exc_type, exc, tb):
pass

class CustomMiddlewareWrapper(Middleware):
async def __init__(self, app: MiddlewareStack, **options):
self.app = app
self.custom_middleware = CustomMiddleware()
self.options = options

async def __call__(self, scope, receive, send_back):
await self.custom_middleware.__aenter__()
await self.app(scope, receive, send_back)
await self.custom_middleware.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_middleware_repr():
middleware = Middleware(CustomMiddlewareWrapper)
assert repr(middleware) == "Middleware(<class '__main__.CustomMiddlewareWrapper'>, CustomMiddleware)"
