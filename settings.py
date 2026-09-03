"""Browser / environment configuration for the UI suite.

Everything environment-specific lives here so the tests and page objects stay declarative.
Set BASE_URL to run the same suite against the real application instead of the local test double.
"""
import os
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent
FORM_PATH = "/autocomplete-form.html"

# Real environment: https://test.com/autocomplete-form
BASE_URL = os.getenv("BASE_URL")

# Endpoint the Next button posts to; stubbed by the mock_submit_api fixture.
SUBMIT_ROUTE = "**/api/responses"

# Test environment details from the assignment.
LOGIN_USER = "test123@gmail.com"
LOCALE = "en-IN"
TIMEZONE = "Asia/Kolkata"

SEED_SUGGESTIONS = [
    "agile methodology",
    "agile methodology process",
    "agile methodology process testing",
]

SUCCESS_TEXT = "Success! Your response has been recorded."
ERROR_TEXT = "Error: Invalid input. Please select a valid suggestion."
