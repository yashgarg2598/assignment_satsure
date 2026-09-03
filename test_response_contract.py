"""Point 5 — API automation against the FR-05 data contract.

The payload under test is the response given in the assignment, so the tests that encode the
defects from docs/3-defect-identification.md are marked xfail(strict=True): the suite is green
while a documented defect still reproduces and fails loudly once it is fixed (at which point the
marker is removed). Negative tests are ordinary passing tests.
"""
import re
from datetime import datetime, timedelta

import jsonschema
import pytest
import requests

from tests.api.tests.conftest import SELECTED_VALUE
from tests.api.tests.contract_schema import BCP47_WITH_REGION, RESPONSE_SCHEMA

pytestmark = pytest.mark.api

IST_OFFSET = timedelta(hours=5, minutes=30)

validate = jsonschema.Draft202012Validator(
    RESPONSE_SCHEMA, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
).validate


@pytest.mark.xfail(strict=True, reason="DEF-01/DEF-04: completed is a string and locale lacks region")
def test_response_matches_data_contract_schema(form_response):
    """(a) Whole-payload validation against FR-05: presence, types and formats."""
    validate(form_response)


def test_compliant_response_passes_contract(api_base_url):
    """(a) Control case: the corrected payload validates, proving the schema is satisfiable."""
    payload = requests.get(f"{api_base_url}/api/responses/compliant", timeout=10).json()
    validate(payload)


def test_all_contract_properties_are_present(form_response):
    """(a) Presence alone, independent of the type defects, to prove nothing is missing."""
    assert set(form_response) == set(RESPONSE_SCHEMA["properties"])


@pytest.mark.xfail(strict=True, reason="DEF-01: completed is the string 'true', not a boolean")
def test_completed_is_boolean(form_response):
    """(b) FR-05 requires a Boolean upload status."""
    assert isinstance(form_response["completed"], bool)


@pytest.mark.xfail(strict=True, reason="DEF-02/DEF-03: timestamps are UTC, not the user's local time")
@pytest.mark.parametrize("field", ["start_date", "end_date"])
def test_timestamps_are_in_user_local_time(form_response, field):
    """(b) FR-05 requires the user's local time; the user is in IST (UTC+05:30)."""
    parsed = datetime.fromisoformat(form_response[field].replace("Z", "+00:00"))
    assert parsed.utcoffset() == IST_OFFSET


@pytest.mark.xfail(strict=True, reason="DEF-04: locale is 'en', missing the -IN region subtag")
def test_locale_is_bcp47_with_region(form_response):
    """(c) IETF BCP 47 format, region subtag included (en-IN for this environment)."""
    assert re.match(BCP47_WITH_REGION, form_response["locale"])


@pytest.mark.xfail(strict=True, reason="DEF-05: all three suggestions are returned, not just the selected one")
def test_suggestion_list_contains_only_matching_suggestions(form_response):
    """(d) Only suggestions matching the entered/selected value. See AMB-01."""
    suggestions = [s.strip() for s in form_response["suggestion_list"].split(",")]
    assert form_response["text"] == SELECTED_VALUE
    assert suggestions == [SELECTED_VALUE]


@pytest.mark.parametrize(
    "path, invalid_property",
    [
        ("missing-field", "account_email"),  # required property removed
        ("wrong-type", "completed"),  # boolean sent as a string
        ("invalid-locale", "locale"),  # not a BCP 47 tag at all
    ],
)
def test_malformed_response_fails_contract_validation(api_base_url, path, invalid_property):
    """(e) Negative cases: each malformed payload must be rejected by the contract."""
    payload = requests.get(f"{api_base_url}/api/responses/{path}", timeout=10).json()
    with pytest.raises(jsonschema.ValidationError) as failure:
        validate(payload)
    assert invalid_property in str(failure.value)
