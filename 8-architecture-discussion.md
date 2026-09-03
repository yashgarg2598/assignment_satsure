# 8. Architecture Discussion

## Layering

```
tests/ui/tests/     assertions only — reads as the test case it implements
tests/ui/pages/     Page Objects: locators + interactions, no assertions
tests/ui/config/    environment (URLs, locale, timezone, seed data) + HTML test double
tests/api/tests/    contract tests + the FR-05 JSON Schema + stub API
```

Three rules keep the layers honest: tests never contain a selector, page objects never contain an
assertion, and neither contains a URL or a credential. A selector change touches one page object;
an environment change touches `config/settings.py` only.

## Choices worth defending

**Page Object over raw locators.** Required by the assignment, but it also earns its place here:
`#input-field` and `ul.suggestions li` appear once each, so the day the form is rebuilt the suite is
a one-file change.

**JSON Schema as the single contract source.** `tests/api/tests/contract_schema.py` declares
presence, types and formats; the tests validate against it instead of restating each field. Adding
a property to FR-05 is one line, and the schema doubles as documentation a backend engineer can
read.

**Built-in libraries over frameworks.** `pytest` fixtures for lifecycle, Playwright's `expect` for
auto-waiting, `page.route` for network stubbing, `jsonschema` for validation, `http.server` for the
stubs. There is no bespoke wait helper, HTTP client wrapper or assertion library to maintain — the
things most likely to rot in a test suite.

**Environment-driven, not environment-coupled.** `BASE_URL` / `API_BASE_URL` repoint the identical
suite at local doubles, staging or production. The doubles exist so the suite is executable today,
not as a permanent fixture.

**Strict `xfail` for known defects.** Documented defects are encoded as executable assertions that
are green while the defect reproduces and red the moment it is fixed, so `3-defect-identification.md`
cannot drift out of date silently.

## Scaling this out

- **Test data.** Seed suggestions live in `config/settings.py`; a real suite would move to
  API-driven setup (create the account, configure the form, submit a response) so tests do not
  depend on pre-seeded state, with each test owning its own data.
- **Parallelism.** `pytest-xdist` gives near-linear scaling once tests are data-independent — the
  reason for the point above. Playwright's browser context per test already isolates browser state.
- **Cross-browser / cross-locale.** `--browser chromium --browser firefox --browser webkit`, and
  parametrising `browser_context_args` over locale/timezone, would turn FR-05's locale and local-time
  requirements into a matrix rather than the single IST case the assignment specifies.
- **CI.** One GitHub Actions job: install, `playwright install --with-deps chromium`, `pytest`,
  publish the JUnit XML plus Playwright traces on failure (`--tracing retain-on-failure`).
- **Reporting.** `pytest --junitxml` for the CI gate; the scenario/defect IDs already carried in
  test names and `xfail` reasons give traceability from a failed run back to a requirement.

## What is deliberately not here

Login automation (out of scope — the user arrives logged in), admin configuration of the form
(explicitly out of scope), visual regression, and performance/load coverage. FR-03's match-anywhere
mode is covered against the test double via a query parameter because the real toggle is backend
configuration that the assignment places out of scope.
