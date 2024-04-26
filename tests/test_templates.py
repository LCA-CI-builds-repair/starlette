import os
from pathlib import Path
from unittest import mock

import jinja2
import pytest

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Route
from starlette.templating import Jinja2Templates


def test_templates(tmpdir, test_client_factory):
    path = os.path.join(tmpdir, "index.html")
    with open(path, "w") as file:
        file.write("<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>")

    async def homepage(request):
        return templates.TemplateResponse(request, "index.html")
import pytest
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from starlette.templating import Jinja2Templates

def homepage(request):
    return HTMLResponse("<html>Hello, <a href='http://testserver/'>world</a></html>")

def index_context_processor(request):
    return {"username": "Alice"}

def test_calls_context_processors(tmp_path, test_client_factory):
    path = tmp_path / "index.html"
    path.write_text("<html>Hello {{ username }}</html>")
    app = Starlette(debug=True, routes=[Route("/", endpoint=homepage)])
    templates = Jinja2Templates(directory=str(tmp_path))
    templates.env.globals.update(index_context_processor(request=None))
    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "<html>Hello Alice</html>"

    async def homepage(request):
import pytest
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from starlette.templating import Jinja2Templates

def homepage(request):
    return HTMLResponse("<html>Hello World</html>")

def hello_world_processor(request):
    return {"world": "World"}

def test_templates(tmp_path, test_client_factory):
    app = Starlette(debug=True, routes=[Route("/", endpoint=homepage)])
    templates = Jinja2Templates(directory=str(tmp_path), context_processors=[hello_world_processor])
    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "<html>Hello World</html>"
    )

    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "<html>Hello World</html>"
    assert response.template.name == "index.html"
    assert set(response.context.keys()) == {"request", "username"}


def test_template_with_middleware(tmpdir, test_client_factory):
    path = os.path.join(tmpdir, "index.html")
    with open(path, "w") as file:
        file.write("<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>")

    async def homepage(request):
        return templates.TemplateResponse(request, "index.html")

    class CustomMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)

    app = Starlette(
        debug=True,
        routes=[Route("/", endpoint=homepage)],
        middleware=[Middleware(CustomMiddleware)],
    )
    templates = Jinja2Templates(directory=str(tmpdir))

    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "<html>Hello, <a href='http://testserver/'>world</a></html>"
    assert response.template.name == "index.html"
    assert set(response.context.keys()) == {"request"}


def test_templates_with_directories(tmp_path: Path, test_client_factory):
import pytest
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from starlette.templating import Jinja2Templates

def page_a(request):
    return templates.TemplateResponse("template_a.html", {"request": request})

dir_a = "path_to_dir_a"
dir_b = "path_to_dir_b"

def test_template_pages(tmp_path, test_client_factory):
    template_a = dir_a / "template_a.html"
    template_a.write_text("<html><a href='{{ url_for('page_a') }}'></a> a</html>")

    template_b = dir_b / "template_b.html"
    template_b.write_text("<html><a href='{{ url_for('page_b') }}'></a> b</html>")

    app = Starlette(debug=True, routes=[Route("/a", endpoint=page_a), Route("/b", endpoint=page_b)])
    templates = Jinja2Templates(directory=str(dir_a))

    client = test_client_factory(app)
    response = client.get("/a")
    assert response.text == "<html><a href='http://testserver/a'></a> a</html>"
    assert response.template.name == "template_a.html"
    assert set(response.context.keys()) == {"request"}

    response = client.get("/b")
    assert response.text == "<html><a href='http://testserver/b'></a> b</html>"
    templates = Jinja2Templates(directory=[dir_a, dir_b])

    client = test_client_factory(app)
    response = client.get("/a")
    assert response.text == "<html><a href='http://testserver/a'></a> a</html>"
    assert response.template.name == "template_a.html"
    assert set(response.context.keys()) == {"request"}

    response = client.get("/b")
    assert response.text == "<html><a href='http://testserver/b'></a> b</html>"
    assert response.template.name == "template_b.html"
    assert set(response.context.keys()) == {"request"}


def test_templates_require_directory_or_environment():
    with pytest.raises(
        AssertionError, match="either 'directory' or 'env' arguments must be passed"
    ):
        Jinja2Templates()  # type: ignore[call-overload]


def test_templates_with_directory(tmpdir):
    path = os.path.join(tmpdir, "index.html")
    with open(path, "w") as file:
        file.write("Hello")

    templates = Jinja2Templates(directory=str(tmpdir))
    template = templates.get_template("index.html")
    assert template.render({}) == "Hello"


def test_templates_with_environment(tmpdir, test_client_factory):
    path = os.path.join(tmpdir, "index.html")
    with open(path, "w") as file:
        file.write("<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>")

    async def homepage(request):
        return templates.TemplateResponse(request, "index.html")

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(tmpdir)))
    app = Starlette(
        debug=True,
        routes=[Route("/", endpoint=homepage)],
    )
    templates = Jinja2Templates(env=env)
    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "<html>Hello, <a href='http://testserver/'>world</a></html>"
    assert response.template.name == "index.html"
    assert set(response.context.keys()) == {"request"}


def test_templates_with_environment_options_emit_warning(tmpdir):
import pytest
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from starlette.templating import Jinja2Templates

def page(request):
    return PlainTextResponse("value: b", status_code=201, headers={"x-key": "value"})

def test_templates_with_kwargs_only_requires_request_in_context(tmpdir):
    templates = Jinja2Templates(directory=str(tmpdir))
    with pytest.warns(DeprecationWarning, match="requires the `request` argument"):
        with pytest.raises(ValueError):
            templates.TemplateResponse(name="index.html", context={"a": "b"})

    assert response.text == "value: b"  # context was rendered
    assert response.status_code == 201
    assert response.headers["x-key"] == "value"
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    spy.assert_called()


def test_templates_with_kwargs_only_requires_request_in_context(tmpdir):
    # MAINTAINERS: remove after 1.0

    templates = Jinja2Templates(directory=str(tmpdir))
    with pytest.warns(
        DeprecationWarning,
        match="requires the `request` argument",
    ):
        with pytest.raises(ValueError):
            templates.TemplateResponse(name="index.html", context={"a": "b"})


def test_templates_with_kwargs_only_warns_when_no_request_keyword(
    tmpdir, test_client_factory
):
    # MAINTAINERS: remove after 1.0

    path = os.path.join(tmpdir, "index.html")
    with open(path, "w") as file:
        file.write("Hello")

    templates = Jinja2Templates(directory=str(tmpdir))

    def page(request):
        return templates.TemplateResponse(
            name="index.html", context={"request": request}
        )

    app = Starlette(routes=[Route("/", page)])
    client = test_client_factory(app)

    with pytest.warns(
        DeprecationWarning,
        match="requires the `request` argument",
    ):
        client.get("/")


def test_templates_with_requires_request_in_context(tmpdir):
    # MAINTAINERS: remove after 1.0
    templates = Jinja2Templates(directory=str(tmpdir))
    with pytest.warns(DeprecationWarning):
        with pytest.raises(ValueError):
            templates.TemplateResponse("index.html", context={})


def test_templates_warns_when_first_argument_isnot_request(tmpdir, test_client_factory):
import pytest
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

def page(request):
    return PlainTextResponse("value: b", status_code=201, headers={"x-key": "value"})

def test_templates(tmpdir, test_client_factory):
    app = Starlette(debug=True, routes=[Route("/", page)])
    client = test_client_factory(app)
    with pytest.warns(DeprecationWarning):
        response = client.get("/")

    assert response.text == "value: b"  # context was rendered
    assert response.status_code == 201
    assert response.headers["x-key"] == "value"
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
        response = client.get("/")

    assert response.text == "value: b"  # context was rendered
    assert response.status_code == 201
    assert response.headers["x-key"] == "value"
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    spy.assert_called()


def test_templates_when_first_argument_is_request(tmpdir, test_client_factory):
import pytest
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

def page(request):
    return PlainTextResponse("value: b", status_code=201, headers={"x-key": "value"})

def test_templates(tmpdir, test_client_factory):
    app = Starlette(debug=True, routes=[Route("/", page)])
    client = test_client_factory(app)
    response = client.get("/")

    assert response.text == "value: b"  # context was rendered
    assert response.status_code == 201
    assert response.headers["x-key"] == "value"
    assert response.headers["content-type"] == "text/plain; charset=utf-8"

    assert response.text == "value: b"  # context was rendered
    assert response.status_code == 201
    assert response.headers["x-key"] == "value"
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    spy.assert_called()
