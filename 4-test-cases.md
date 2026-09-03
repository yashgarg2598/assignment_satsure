# 4. Test Cases — Practical Exercise, Point 3

8 detailed test cases: 5 UI (TC-01…TC-05) and 3 API (TC-06…TC-08).

Common preconditions for all cases: the user is logged in as `test123@gmail.com`; Chrome on
Windows 10 with browser language English; machine timezone IST (UTC+05:30); the form at
`https://test.com/autocomplete-form` is seeded with the three suggestions
`agile methodology`, `agile methodology process`, `agile methodology process testing`.

---

## TC-01 — Prefix-match filtering keeps matching suggestions and hides non-matching ones

- **Covers:** TS-06 / FR-02
- **Preconditions:** Common preconditions. Backend filtering mode is the default (prefix match).
- **Steps:**
  1. Open the autocomplete form.
  2. Observe the suggestion list before typing.
  3. Type `agile` into `#input-field`.
  4. Observe the visible `ul.suggestions li` items.
  5. Clear the field and type `process`.
  6. Observe the visible `ul.suggestions li` items.
  7. Clear the field and type `zzz`.
- **Expected results:**
  1. Step 2: all three suggestions are visible.
  2. Step 4: all three suggestions remain visible — each starts with `agile`.
  3. Step 6: no suggestion is visible — none *starts* with `process`, even though two contain it.
  4. Step 7: no suggestion is visible.
- **Test data:** `agile`, `process`, `zzz`

---

## TC-02 — Match-anywhere filtering keeps substring matches visible when enabled

- **Covers:** TS-07 / FR-03
- **Preconditions:** Common preconditions. Match-anywhere filtering is **enabled** in backend configuration.
- **Steps:**
  1. Open the autocomplete form.
  2. Type `agile method` into `#input-field`.
  3. Observe the visible suggestions.
  4. Clear the field and type `process`.
  5. Observe the visible suggestions.
  6. Clear the field and type `testing`.
- **Expected results:**
  1. Step 3: all three suggestions are visible (all contain the substring).
  2. Step 5: `agile methodology process` and `agile methodology process testing` are visible;
     `agile methodology` is hidden.
  3. Step 6: only `agile methodology process testing` is visible.
- **Test data:** `agile method`, `process`, `testing`

---

## TC-03 — Clicking a suggestion populates the input field

- **Covers:** TS-10 / FR-01
- **Preconditions:** Common preconditions.
- **Steps:**
  1. Open the autocomplete form.
  2. Type `agile` into `#input-field`.
  3. Click the suggestion `agile methodology process`.
  4. Read the value of `#input-field`.
- **Expected results:**
  1. Step 4: `#input-field` contains exactly `agile methodology process` — no truncation, no
     concatenation with the typed prefix.
  2. The suggestion list closes after selection.
- **Test data:** typed `agile`; selected `agile methodology process`

---

## TC-04 — Successful submission shows the success message and error on invalid input

- **Covers:** TS-03, TS-08 / FR-04
- **Preconditions:** Common preconditions. Network capture or request interception available so the
  submit call can be observed and its response controlled.
- **Steps:**
  1. Open the autocomplete form.
  2. Select `agile methodology` from the suggestion list.
  3. Click `#next-button`.
  4. Observe the outgoing REST call and its status code.
  5. Observe the page.
  6. Reload the form, type `zzz` (matching no suggestion), and click `#next-button`.
  7. Observe the page.
- **Expected results:**
  1. Step 4: exactly one POST is sent to the submit endpoint, returning HTTP 200.
  2. Step 5: `div.success-container` is visible showing
     `Success! Your response has been recorded.`; `span.error-message` is not visible.
  3. Step 7: `span.error-message` is visible showing
     `Error: Invalid input. Please select a valid suggestion.`; the success block is not visible
     and no response is persisted.
- **Test data:** valid `agile methodology`; invalid `zzz`

---

## TC-05 — Keyboard-only completion: Tab, Enter and Escape

- **Covers:** TS-09 / FR-01, FR-04
- **Preconditions:** Common preconditions. No pointer input used at any step.
- **Steps:**
  1. Open the autocomplete form.
  2. Press Tab and read `document.activeElement`.
  3. Press Tab again and read `document.activeElement`.
  4. Focus `#input-field`, type `agile methodology`, and press Escape.
  5. Read the value of `#input-field` and the visibility of the suggestion list.
  6. Type `agile methodology` again and press Enter.
  7. Observe the page.
- **Expected results:**
  1. Step 2: focus is on `#input-field`.
  2. Step 3: focus moves to `#next-button` — tab order follows the visual order and no element is
     unreachable.
  3. Step 5: the input is cleared and the suggestion list is closed.
  4. Step 7: Enter submits the form; `div.success-container` becomes visible.
- **Test data:** `agile methodology`

---

## TC-06 — Persisted response matches the FR-05 data contract

- **Covers:** TS-01…TS-05 / FR-05
- **Preconditions:** Common preconditions. A form response has been submitted by selecting
  `agile methodology`. API base URL and auth for the GET endpoint are available.
- **Steps:**
  1. `GET` the persisted response for the submitted form.
  2. Validate the body against the FR-05 JSON Schema
     (`tests/api/tests/contract_schema.py`) with format checking enabled.
  3. Assert `completed` is a JSON boolean.
  4. Parse `start_date` and `end_date` and assert each carries a UTC+05:30 offset.
  5. Assert `locale` matches BCP 47 and includes a region subtag.
- **Expected results:**
  1. Status code 200 and a JSON object body.
  2. All 8 properties present; schema validation passes.
  3. `completed` is `true` (boolean) — **currently fails, DEF-01**.
  4. Offsets are `+05:30`, e.g. `2024-03-15T16:00:00+05:30` — **currently fails, DEF-02 / DEF-03**.
  5. `locale` is `en-IN` — **currently fails, DEF-04**.
- **Test data:** the sample payload in `docs/3-defect-identification.md`

---

## TC-07 — `suggestion_list` contains only the suggestions matching the selected value

- **Covers:** TS-05 / FR-05, point 5(d)
- **Preconditions:** Common preconditions. A form response has been submitted by selecting
  `agile methodology` (not typed free text).
- **Steps:**
  1. `GET` the persisted response.
  2. Split `suggestion_list` on `,` and strip surrounding whitespace from each entry.
  3. Compare the resulting set against the selected value.
- **Expected results:**
  1. Every entry matches the selected value; the list is not the full seed set of three.
  2. `text` equals the selected value `agile methodology`.
  3. **Currently fails, DEF-05** — all three suggestions are returned. See AMB-01 for the
     competing prefix-match reading.
- **Test data:** selected `agile methodology`

---

## TC-08 — Negative: malformed persisted responses are rejected by the contract

- **Covers:** TS-01, TS-03 / FR-05
- **Preconditions:** Common preconditions. Stub endpoints (or fixtures) able to return deliberately
  malformed payloads.
- **Steps:**
  1. `GET` a response with `account_email` removed and validate against the FR-05 schema.
  2. `GET` a response with `completed` as the string `"true"` and validate against the schema.
  3. `GET` a response with `locale` set to `english` and validate against the schema.
- **Expected results:**
  1. Step 1 fails validation, naming `account_email` as a missing required property.
  2. Step 2 fails validation on the type of `completed`.
  3. Step 3 fails validation on the `locale` pattern.
  4. No malformed payload is treated as a valid persisted response.
- **Test data:** the sample payload with (a) `account_email` deleted, (b) `completed: "true"`,
  (c) `locale: "english"`

---

## Traceability

| Test case | Scenario | Requirement | Defect |
|---|---|---|---|
| TC-01 | TS-06 | FR-02 | — |
| TC-02 | TS-07 | FR-03 | — |
| TC-03 | TS-10 | FR-01 | — |
| TC-04 | TS-03, TS-08 | FR-04 | — |
| TC-05 | TS-09 | FR-01, FR-04 | — |
| TC-06 | TS-01, TS-02, TS-04 | FR-05 | DEF-01…DEF-04 |
| TC-07 | TS-05 | FR-05 | DEF-05 |
| TC-08 | TS-01, TS-03 | FR-05 | — |
