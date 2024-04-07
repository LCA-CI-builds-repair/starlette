```python
from starlette.middleware import Middleware as StarletteMiddleware

class CustomMiddleware(StarletteMiddleware):
    def __init__(self, app: Starlette, arg1: int, arg2: float):
        self.arg1 = arg1
        self.arg2 = arg2
        super().__init__(app)

    async def __call__(self, request: Request) -> Response:
        response = Response()
        response.headers["X-Custom-Header"] = f"{self.arg1}, {self.arg2}"
        return response
```

