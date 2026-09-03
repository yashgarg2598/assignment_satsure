# 1. Requirement Analysis

## System under test

Autocomplete web form at `https://test.com/autocomplete-form`, reached after login. Contains a
label, a text input (`#input-field`), a static suggestion list (`ul.suggestions` with three `li`),
a Next button (`#next-button`), an error message (`span.error-message`) and a success block
(`div.success-container`). Admin configuration of the form is out of scope.

Seed suggestions: `agile methodology`, `agile methodology process`, `agile methodology process testing`.

## Functional requirements

| ID | Requirement | Testable assertion |
|---|---|---|
| FR-01 | Free text input OR click/tap a suggestion | Input accepts arbitrary text; clicking an `li` populates the input |
| FR-02 | Prefix match filtering (default) | Suggestions whose start matches the typed characters stay visible; non-matching ones disappear |
| FR-03 | Match-anywhere filtering (configurable) | When enabled, a suggestion stays visible if it contains the typed text anywhere (`"agile method"` keeps all three) |
| FR-04 | Form submission | Next issues a REST call; success returns HTTP 200 and shows the success message; invalid input shows the error message |
| FR-05 | Backend data contract | 8 properties persisted: `account_id`, `account_email`, `start_date`, `end_date`, `locale`, `text`, `suggestion_list`, `completed` |

## FR-05 field expectations

| Property | Expectation |
|---|---|
| `account_id` | ID of the account that completed the form (type unspecified in the spec) |
| `account_email` | Email of that account — `test123@gmail.com` in this environment |
| `start_date` | Timestamp **in the user's local time** when the form was reached |
| `end_date` | Timestamp **in the user's local time** when Next was selected |
| `locale` | IETF BCP 47 — `en-IN` for the stated environment |
| `text` | Text given by the user in the input field |
| `suggestion_list` | Comma-separated string of suggestions matching the value entered/selected |
| `completed` | **Boolean** upload status of the form response |

## Test environment

Chrome on Windows 10, browser language English, login `test123@gmail.com`, user in India
(IST, UTC+05:30).

## Open questions carried into testing

1. **FR-02 vs point 5(d).** Under prefix match, all three suggestions match the selected value
   `agile methodology`, so a `suggestion_list` of all three is arguably correct — yet point 5(d)
   requires the list to contain "only matching suggestions (not all suggestions)". Selection is
   treated as an exact-value match in `docs/3-defect-identification.md`; needs product confirmation.
2. **`account_id` type.** String vs integer is unspecified; asserted as "present and non-empty" only.
3. **`suggestion_list` separator.** `,` vs `, ` (comma + space) is unspecified; parsing tolerates both.
4. **Local time representation.** Whether "user's local time" means an offset-carrying timestamp
   (`+05:30`) or a naive local string. Offset-carrying is assumed, as it is the only unambiguous form.
5. **Which filtering mode is live** in the environment under test (FR-02 default vs FR-03 enabled)
   is a backend configuration, so both modes are covered separately.
