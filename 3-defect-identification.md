# 3. Defect Identification — Practical Exercise, Point 2

## Response under review

Form completed by selecting `agile methodology` from the suggestion list; subsequent `GET` returned:

```json
{
  "account_id": "98765",
  "account_email": "test123@gmail.com",
  "start_date": "2024-03-15T10:30:00Z",
  "end_date": "2024-03-15T10:32:00Z",
  "locale": "en",
  "text": "agile methodology",
  "suggestion_list": "agile methodology, agile methodology process, agile methodology process testing",
  "completed": "true"
}
```

All 8 properties required by FR-05 are present — there are no missing or extra fields. Every
discrepancy below is therefore a value, type or format defect.

## Defects

| ID | Property | Expected (FR-05) | Actual | Severity | Why it is a defect |
|---|---|---|---|---|---|
| DEF-01 | `completed` | Boolean representing upload status | `"true"` — a JSON string | Critical | FR-05 explicitly says Boolean. `"false"` would also be truthy in JavaScript and in most schema-less consumers, so a failed upload can be read as a success. |
| DEF-02 | `start_date` | Timestamp in the **user's local time** when the form was reached | `2024-03-15T10:30:00Z` — UTC | Critical | The user is in India (IST, UTC+05:30); local time is `2024-03-15T16:00:00+05:30`. The value is off by 5h30m and carries a UTC designator. |
| DEF-03 | `end_date` | Timestamp in the **user's local time** when Next was selected | `2024-03-15T10:32:00Z` — UTC | Critical | Same as DEF-02; local time is `2024-03-15T16:02:00+05:30`. The 2-minute duration survives, but the absolute timestamps and their calendar date bucket do not. |
| DEF-04 | `locale` | IETF BCP 47 tag for the user's locale, e.g. `en-IN` | `en` | High | `en` is a valid BCP 47 language tag but not the user's locale: the environment is English in India, so the region subtag `-IN` is missing and locale-sensitive formatting will fall back to the wrong region. |
| DEF-05 | `suggestion_list` | Comma-separated string of suggestions **matching the value entered/selected** | All three seed suggestions | High | The user selected exactly `agile methodology`; under the exact-selection reading required by point 5(d) the field must contain only `agile methodology`. See the ambiguity note below. |

## Ambiguities (raised, not counted as defects)

| ID | Property | Observation | Why it is not called a defect |
|---|---|---|---|
| AMB-01 | `suggestion_list` | Under FR-02 prefix matching, all three suggestions genuinely start with `agile methodology`, so returning all three is defensible — the field is only wrong if a suggestion *selection* is treated as an exact-value match. | FR-05 says "matching the value entered/selected" without defining match semantics for a selection. Point 5(d) resolves it in favour of "not all suggestions", which is the reading DEF-05 and the automated tests assert; product confirmation is still needed. |
| AMB-02 | `account_id` | Returned as the string `"98765"` rather than a number. | FR-05 specifies no type for `account_id`, so the tests assert only presence and non-emptiness. |
| AMB-03 | `suggestion_list` | Separator is `, ` (comma + space), not a bare `,`. | FR-05 says "comma-separated" without specifying whitespace; parsing is whitespace-tolerant. Worth pinning in the contract to avoid consumer-side drift. |

## Automation mapping

`tests/api/tests/test_response_contract.py` encodes each defect above as an `xfail(strict=True)`
assertion against this exact payload, so the suite passes only while the defects still reproduce and
fails loudly the moment one is fixed — at which point the `xfail` marker is removed.

| Defect | Test |
|---|---|
| DEF-01 | `test_completed_is_boolean` |
| DEF-02, DEF-03 | `test_timestamps_are_in_user_local_time` |
| DEF-04 | `test_locale_is_bcp47_with_region` |
| DEF-05 | `test_suggestion_list_contains_only_matching_suggestions` |
| all | `test_response_matches_data_contract_schema` |
