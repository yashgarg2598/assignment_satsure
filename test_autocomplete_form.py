"""Point 4 — Playwright UI tests for the Autocomplete form.

One test per required coverage area: tab navigation, keyboard interaction, suggestion filtering,
suggestion selection, form submission (success and error). Assertions use Playwright's `expect`,
which auto-waits, so the suite contains no sleeps or polling.
"""
import pytest
from playwright.sync_api import expect

from tests.ui.config import settings
from tests.ui.pages.autocomplete_page import AutocompletePage

pytestmark = pytest.mark.ui

ALL_SUGGESTIONS = settings.SEED_SUGGESTIONS


@pytest.fixture
def form(page, base_url):
    return AutocompletePage(page)


def test_tab_navigation_reaches_input_then_next_button(form):
    """TC-05 / TS-09 — tab order follows visual order and leaves no element unreachable."""
    form.open()
    form.press("Tab")
    assert form.focused_id() == "input-field"
    form.press("Tab")
    assert form.focused_id() == "next-button"


def test_enter_submits_and_escape_clears_the_field(form):
    """TC-05 / TS-09 — Enter submits, Escape clears the input and closes the list."""
    form.open()
    form.type_value("agile methodology")
    form.press("Escape")
    expect(form.input).to_have_value("")
    assert form.visible_suggestions() == []

    form.type_value("agile methodology")
    form.press("Enter")
    expect(form.success_container).to_be_visible()


@pytest.mark.parametrize(
    "typed, expected",
    [
        ("agile", ALL_SUGGESTIONS),
        ("agile methodology p", ALL_SUGGESTIONS[1:]),
        ("process", []),  # contains, but does not start with — must disappear (FR-02)
        ("zzz", []),
    ],
)
def test_prefix_match_filtering(form, typed, expected):
    """TC-01 / TS-06 — FR-02 default prefix matching, both appear and disappear."""
    form.open()
    form.type_value(typed)
    assert form.visible_suggestions() == expected


@pytest.mark.parametrize(
    "typed, expected",
    [
        ("agile method", ALL_SUGGESTIONS),
        ("process", ALL_SUGGESTIONS[1:]),  # substring match keeps these visible (FR-03)
        ("zzz", []),
    ],
)
def test_match_anywhere_filtering_when_enabled(form, typed, expected):
    """TC-02 / TS-07 — FR-03 match-anywhere configuration."""
    form.open(match_anywhere=True)
    form.type_value(typed)
    assert form.visible_suggestions() == expected


def test_clicking_a_suggestion_populates_the_input(form):
    """TC-03 / TS-10 — FR-01 selection by click."""
    form.open()
    form.type_value("agile")
    form.select_suggestion("agile methodology process")
    expect(form.input).to_have_value("agile methodology process")
    assert form.visible_suggestions() == []


def test_submission_shows_success_message(form):
    """TC-04 / TS-03 — FR-04 happy path; the submit API is stubbed with HTTP 200."""
    form.open()
    form.select_suggestion("agile methodology")
    form.submit()
    expect(form.success_container).to_be_visible()
    expect(form.success_container).to_contain_text(settings.SUCCESS_TEXT)
    expect(form.error_message).to_be_hidden()


def test_invalid_input_shows_error_message(form):
    """TC-04 / TS-08 — FR-04 error path; free text matching no suggestion is rejected."""
    form.open()
    form.type_value("zzz")
    form.submit()
    expect(form.error_message).to_be_visible()
    expect(form.error_message).to_have_text(settings.ERROR_TEXT)
    expect(form.success_container).to_be_hidden()


@pytest.mark.submit_status(500)
def test_failed_submission_shows_error_message(form):
    """TC-04 / TS-03 — a non-200 from the persist call must not report success."""
    form.open()
    form.select_suggestion("agile methodology")
    form.submit()
    expect(form.error_message).to_be_visible()
    expect(form.success_container).to_be_hidden()
