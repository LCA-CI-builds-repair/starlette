from starlette.applications import Starlette
- Import missing modules: Add missing imports for functions used in the code snippet.
- Fix class instantiation: Ensure that the `Starlette` class is properly instantiated before defining the routes and middleware.
- Correct function definitions: Make sure that the functions used as endpoints have the correct parameters and return types.
- Update streaming response test: Adjust the test_gzip_streaming_response function to match the expected behavior of the StreamingResponse.
    assert response.headers["Content-Encoding"] == "text"
    assert "Content-Length" not in response.headers
