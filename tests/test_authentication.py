import base64
import binascii
from urllib.parse import urlencode

import pytest

from starlette.applications import Starlette
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
    requires,
)
from starlette.endpoints import HTTPEndpoint
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocketDisconnect

async def test_authentication_middleware_request():
    class CustomAuthenticationMiddleware:
        def __init__(self, app: Callable) -> None:
            self.app = app

        async def __call__(self, request: Request) -> None:
            # Do something with the request
            assert request.headers.get("Authorization") == "123456"

            response = JSONResponse({"message": "Hello, world!"})
            return response

    class CustomRoute:
        path = "/test"

        def __init__(self, app: Callable) -> None:
            self.app = app

        async def __call__(self, request: Request) -> JSONResponse:
            # Do something with the request
            assert request.headers.get("Authorization") == "123456"

            return JSONResponse({"message": "Hello, world!"})

    app = Starlette(on_startup=[AuthenticationMiddleware(HTTPEndpoint)])
    app.add_route(CustomRoute, "/")
    app.add_websocket_route(CustomRoute, "/ws")

    client = TestClient(app)

    response = await client.get("/test", headers={"Authorization": "123456"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}

    response = await client.get("/test", headers={"Authorization": "7890"})
    assert response.status_code == 403

    response = await client.get("/test", headers={"Authorization": None})
    assert response.status_code == 403

    response = await client.get("/test")
    assert response.status_code == 403

    response = await client.ws_connect("/ws", headers={"Authorization": "123456"})
    assert response.extra["headers"]["authorization"] == "123456"

    response = await client.ws_connect("/ws", headers={"Authorization": "7890"})
    assert response.extra["headers"]["authorization"] == "7890"

    response = await client.ws_connect("/ws", headers={"Authorization": None})
    assert response.extra["headers"]["authorization"] == "None"

    response = await client.ws_connect("/ws")
    assert response.extra["headers"]["authorization"] == "None"


class BasicAuth(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials")

        username, _, password = decoded.partition(":")
        return AuthCredentials(["authenticated"]), SimpleUser(username)


def homepage(request):
    return JSONResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.display_name,
        }
    )


@requires("authenticated")
async def dashboard(request):
    return JSONResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.display_name,
        }
    )


@requires("authenticated", redirect="homepage")
async def admin(request):
    return JSONResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.display_name,
        }
    )


@requires("authenticated")
def dashboard_sync(request):
    return JSONResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.display_name,
        }
    )


class Dashboard(HTTPEndpoint):
    @requires("authenticated")
    def get(self, request):
        return JSONResponse(
            {
                "authenticated": request.user.is_authenticated,
                "user": request.user.display_name,
            }
        )


@requires("authenticated", redirect="homepage")
def admin_sync(request):
    return JSONResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.display_name,
        }
    )


@requires("authenticated")
async def websocket_endpoint(websocket):
    await websocket.accept()
    await websocket.send_json(
        {
            "authenticated": websocket.user.is_authenticated,
            "user": websocket.user.display_name,
        }
    )


def async_inject_decorator(**kwargs):
    def wrapper(endpoint):
        async def app(request):
            return await endpoint(request=request, **kwargs)

        return app

    return wrapper


@async_inject_decorator(additional="payload")
@requires("authenticated")
async def decorated_async(request, additional):
    return JSONResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.display_name,
            "additional": additional,
        }
    )


def sync_inject_decorator(**kwargs):
    def wrapper(endpoint):
        def app(request):
            return endpoint(request=request, **kwargs)

        return app

    return wrapper


@sync_inject_decorator(additional="payload")
@requires("authenticated")
def decorated_sync(request, additional):
    return JSONResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.display_name,
            "additional": additional,
        }
    )


def ws_inject_decorator(**kwargs):
    def wrapper(endpoint):
        def app(websocket):
            return endpoint(websocket=websocket, **kwargs)

        return app

    return wrapper


@ws_inject_decorator(additional="payload")
@requires("authenticated")
async def websocket_endpoint_decorated(websocket, additional):
    await websocket.accept()
    await websocket.send_json(
        {
            "authenticated": websocket.user.is_authenticated,
            "user": websocket.user.display_name,
            "additional": additional,
        }
    )


app = Starlette(
    middleware=[Middleware(AuthenticationMiddleware, backend=BasicAuth())],
    routes=[
        Route("/", endpoint=homepage),
        Route("/dashboard", endpoint=dashboard),
        Route("/admin", endpoint=admin),
        Route("/dashboard/sync", endpoint=dashboard_sync),
        Route("/dashboard/class", endpoint=Dashboard),
        Route("/admin/sync", endpoint=admin_sync),
        Route("/dashboard/decorated", endpoint=decorated_async),
        Route("/dashboard/decorated/sync", endpoint=decorated_sync),
        WebSocketRoute("/ws", endpoint=websocket_endpoint),
        WebSocketRoute("/ws/decorated", endpoint=websocket_endpoint_decorated),
    ],
)


def test_invalid_decorator_usage():
    with pytest.raises(Exception):

        @requires("authenticated")
        def foo():
            pass  # pragma: nocover


def test_user_interface(test_client_factory):
    with test_client_factory(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"authenticated": False, "user": ""}

        response = client.get("/", auth=("tomchristie", "example"))
        assert response.status_code == 200
        assert response.json() == {"authenticated": True, "user": "tomchristie"}


def test_authentication_required(test_client_factory):
    with test_client_factory(app) as client:
        response = client.get("/dashboard")
        assert response.status_code == 403

        response = client.get("/dashboard", auth=("tomchristie", "example"))
        assert response.status_code == 200
        assert response.json() == {"authenticated": True, "user": "tomchristie"}

        response = client.get("/dashboard/sync")
        assert response.status_code == 403

        response = client.get("/dashboard/sync", auth=("tomchristie", "example"))
        assert response.status_code == 200
        assert response.json() == {"authenticated": True, "user": "tomchristie"}

        response = client.get("/dashboard/class")
        assert response.status_code == 403

        response = client.get("/dashboard/class", auth=("tomchristie", "example"))
        assert response.status_code == 200
        assert response.json() == {"authenticated": True, "user": "tomchristie"}

        response = client.get("/dashboard/decorated", auth=("tomchristie", "example"))
        assert response.status_code == 200
        assert response.json() == {
            "authenticated": True,
            "user": "tomchristie",
            "additional": "payload",
        }

        response = client.get("/dashboard/decorated")
        assert response.status_code == 403

        response = client.get(
            "/dashboard/decorated/sync", auth=("tomchristie", "example")
        )
        assert response.status_code == 200
        assert response.json() == {
            "authenticated": True,
            "user": "tomchristie",
            "additional": "payload",
        }

        response = client.get("/dashboard/decorated/sync")
        assert response.status_code == 403

        response = client.get("/dashboard", headers={"Authorization": "basic foobar"})
        assert response.status_code == 400
        assert response.text == "Invalid basic auth credentials"


def test_websocket_authentication_required(test_client_factory):
    with test_client_factory(app) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws"):
                pass  # pragma: nocover

        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(
                "/ws", headers={"Authorization": "basic foobar"}
            ):
                pass  # pragma: nocover

        with client.websocket_connect(
            "/ws", auth=("tomchristie", "example")
        ) as websocket:
            data = websocket.receive_json()
            assert data == {"authenticated": True, "user": "tomchristie"}

        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws/decorated"):
                pass  # pragma: nocover

        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(
                "/ws/decorated", headers={"Authorization": "basic foobar"}
            ):
                pass  # pragma: nocover

        with client.websocket_connect(
            "/ws/decorated", auth=("tomchristie", "example")
        ) as websocket:
            data = websocket.receive_json()
            assert data == {
                "authenticated": True,
                "user": "tomchristie",
                "additional": "payload",
            }


def test_authentication_redirect(test_client_factory):
    with test_client_factory(app) as client:
        response = client.get("/admin")
        assert response.status_code == 200
        url = "{}?{}".format(
            "http://testserver/", urlencode({"next": "http://testserver/admin"})
        )
        assert response.url == url

        response = client.get("/admin", auth=("tomchristie", "example"))
        assert response.status_code == 200
        assert response.json() == {"authenticated": True, "user": "tomchristie"}

        response = client.get("/admin/sync")
        assert response.status_code == 200
        url = "{}?{}".format(
            "http://testserver/", urlencode({"next": "http://testserver/admin/sync"})
        )
        assert response.url == url

        response = client.get("/admin/sync", auth=("tomchristie", "example"))
        assert response.status_code == 200
        assert response.json() == {"authenticated": True, "user": "tomchristie"}


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)


@requires("authenticated")
def control_panel(request):
    return JSONResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.display_name,
        }
    )


other_app = Starlette(
    routes=[Route("/control-panel", control_panel)],
    middleware=[
        Middleware(
            AuthenticationMiddleware, backend=BasicAuth(), on_error=on_auth_error
        )
    ],
)


def test_custom_on_error(test_client_factory):
    with test_client_factory(other_app) as client:
        response = client.get("/control-panel", auth=("tomchristie", "example"))
        assert response.status_code == 200
        assert response.json() == {"authenticated": True, "user": "tomchristie"}

        response = client.get(
            "/control-panel", headers={"Authorization": "basic foobar"}
        )
        assert response.status_code == 401
        assert response.json() == {"error": "Invalid basic auth credentials"}
