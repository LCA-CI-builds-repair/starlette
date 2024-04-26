from starlette.applications import Starlette
import gzip
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

def homepage(test_client_factory=None):
    html_content = b"<!html><body><h1>Welcome to the homepage!</h1></body></html>"
    zipped_content = gzip.compress(html_content)
    return StreamingResponse(content=zipped_content, media_type="application/octet-stream")

def test_homepage():
    response = homepage()
    assert response.status_code == 200
    assert response.headers["content-encoding"] == "gzip"

    app = Starlette(
        routes=[Route("/", endpoint=homepage)],
        middleware=[Middleware(GZipMiddleware)],
    )

    client = test_client_factory(app)
    response = client.get("/", headers={"accept-encoding": "gzip"})
    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert response.headers["Content-Encoding"] == "gzip"
    assert int(response.headers["Content-Length"]) < 4000


def test_gzip_not_in_accept_encoding(test_client_factory):
    def homepage(request):
        return PlainTextResponse("x" * 4000, status_code=200)

    app = Starlette(
        routes=[Route("/", endpoint=homepage)],
        middleware=[Middleware(GZipMiddleware)],
    )

    client = test_client_factory(app)
    response = client.get("/", headers={"accept-encoding": "identity"})
    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert "Content-Encoding" not in response.headers
    assert int(response.headers["Content-Length"]) == 4000


def test_gzip_ignored_for_small_responses(test_client_factory):
    def homepage(request):
        return PlainTextResponse("OK", status_code=200)

    app = Starlette(
        routes=[Route("/", endpoint=homepage)],
        middleware=[Middleware(GZipMiddleware)],
    )

    client = test_client_factory(app)
    response = client.get("/", headers={"accept-encoding": "gzip"})
    assert response.status_code == 200
    assert response.text == "OK"
    assert "Content-Encoding" not in response.headers
    assert int(response.headers["Content-Length"]) == 2


def test_gzip_streaming_response(test_client_factory):
    def homepage(request):
        async def generator(bytes, count):
            for index in range(count):
                yield bytes

        streaming = generator(bytes=b"x" * 400, count=10)
        return StreamingResponse(streaming, status_code=200)

    app = Starlette(
        routes=[Route("/", endpoint=homepage)],
        middleware=[Middleware(GZipMiddleware)],
    )

    client = test_client_factory(app)
    response = client.get("/", headers={"accept-encoding": "gzip"})
    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert response.headers["Content-Encoding"] == "gzip"
    assert "Content-Length" not in response.headers


def test_gzip_ignored_for_responses_with_encoding_set(test_client_factory):
    def homepage(request):
        async def generator(bytes, count):
            for index in range(count):
                yield bytes

        streaming = generator(bytes=b"x" * 400, count=10)
        return StreamingResponse(
            streaming, status_code=200, headers={"Content-Encoding": "text"}
        )

    app = Starlette(
        routes=[Route("/", endpoint=homepage)],
        middleware=[Middleware(GZipMiddleware)],
    )

    client = test_client_factory(app)
    response = client.get("/", headers={"accept-encoding": "gzip, text"})
    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert response.headers["Content-Encoding"] == "text"
    assert "Content-Length" not in response.headers
