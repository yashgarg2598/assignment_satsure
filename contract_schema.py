"""FR-05 data contract as a JSON Schema.

Presence, types and formats are declared here and enforced by `jsonschema`, so the tests assert
against a single source of truth instead of hand-written per-field checks.
"""

# IETF BCP 47 language tag with a mandatory region subtag: language[-Script]-REGION (e.g. en-IN).
# FR-05 gives `en-IN` as the expected value for this environment, so a bare `en` is rejected.
BCP47_WITH_REGION = r"^[a-zA-Z]{2,3}(-[a-zA-Z]{4})?-([a-zA-Z]{2}|[0-9]{3})$"

RESPONSE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        # AMB-02: FR-05 does not specify a type for account_id, so both are accepted.
        "account_id": {"type": ["string", "integer"], "minLength": 1},
        "account_email": {"type": "string", "format": "email"},
        "start_date": {"type": "string", "format": "date-time"},
        "end_date": {"type": "string", "format": "date-time"},
        "locale": {"type": "string", "pattern": BCP47_WITH_REGION},
        "text": {"type": "string", "minLength": 1},
        "suggestion_list": {"type": "string"},
        "completed": {"type": "boolean"},
    },
    "required": [
        "account_id",
        "account_email",
        "start_date",
        "end_date",
        "locale",
        "text",
        "suggestion_list",
        "completed",
    ],
    "additionalProperties": False,
}
