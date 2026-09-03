# 2. Test Scenarios — Practical Exercise, Point 1

Top 10 scenarios, ranked highest to lowest risk. Risk = (impact of failure on persisted data or on
the user's ability to complete the form) x (likelihood, weighted by defects already observed in the
sample API response in `3-defect-identification.md`).

| # | ID | One-line summary | Risk | Ranking rationale |
|---|---|---|---|---|
| 1 | TS-01 | `completed` is persisted as a JSON boolean, not the string `"true"` | Critical | The sample response already violates this, and a string silently passes truthiness checks downstream, so every consumer of the upload status can mis-read a failed submission as successful. |
| 2 | TS-02 | `start_date` / `end_date` are persisted in the user's local time (IST, UTC+05:30), not UTC | Critical | The sample response returns `Z` timestamps, which shifts every recorded form session by 5.5 hours and corrupts any duration or date-bucketed reporting built on it. |
| 3 | TS-03 | Next submits the response and the backend persists all 8 FR-05 properties | Critical | If submission or persistence fails, the user's entire response is lost and no other requirement can be satisfied. |
| 4 | TS-04 | `locale` is a full IETF BCP 47 tag including region (`en-IN`) | High | The sample returns bare `en`, losing the region subtag that drives number, date and currency formatting for an Indian user. |
| 5 | TS-05 | `suggestion_list` contains only the suggestions matching the entered/selected value | High | The sample returns all three suggestions after a single selection, so the field cannot be trusted to reconstruct what the user was actually offered. |
| 6 | TS-06 | Prefix-match filtering (FR-02) shows matching suggestions and hides non-matching ones | High | This is the form's core interaction and the default configuration; broken filtering either hides valid choices or offers invalid ones, driving wrong submissions. |
| 7 | TS-07 | Match-anywhere filtering (FR-03) keeps substring matches visible when enabled | High | A configurable code path is the one least likely to be exercised in manual testing, and `"agile method"` must keep all three suggestions — an easy regression to ship unnoticed. |
| 8 | TS-08 | Invalid input shows the error message and is not persisted | Medium | Contained blast radius — the user is told and can retry — but a missing guard lets unvalidated free text reach the backend. |
| 9 | TS-09 | Keyboard-only completion: Tab between elements, Enter to submit, Escape to clear/close | Medium | Blocks keyboard and assistive-technology users entirely, but does not corrupt data for users on a pointer. |
| 10 | TS-10 | Clicking a suggestion populates the input field with that exact value | Low | Visible and immediately obvious if broken, and users retain the free-text path (FR-01) as a workaround. |

## Coverage map

| Requirement | Scenarios |
|---|---|
| FR-01 | TS-10, TS-09 |
| FR-02 | TS-06 |
| FR-03 | TS-07 |
| FR-04 | TS-03, TS-08, TS-09 |
| FR-05 | TS-01, TS-02, TS-04, TS-05, TS-03 |
