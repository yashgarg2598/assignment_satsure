"""Fixtures for the UI suite: a local static server for the test double and a stubbed submit API."""
import functools
import http.server
import threading

import pytest

from tests.ui.config import settings


@pytest.fixture(scope="session")
def fixture_server():
    """Serve the HTML test double over HTTP using the standard library only.

    Skipped entirely when BASE_URL points the suite at a real environment.
    """
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(settings.FIXTURE_DIR)
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture(scope="session")
def base_url(fixture_server):
    return settings.BASE_URL or fixture_server


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Match the documented test environment: English (India), IST."""
    return {**browser_context_args, "locale": settings.LOCALE, "timezone_id": settings.TIMEZONE}


@pytest.fixture(autouse=True)
def mock_submit_api(page, request):
    """Stub the REST call behind the Next button (FR-04).

    Defaults to HTTP 200; a test can ask for a failure with
    @pytest.mark.submit_status(500).
    """
    marker = request.node.get_closest_marker("submit_status")
    status = marker.args[0] if marker else 200
    page.route(
        settings.SUBMIT_ROUTE,
        lambda route: route.fulfill(status=status, json={"completed": status == 200}),
    )
    yield
