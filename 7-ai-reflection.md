# 7. AI Reflection — Practical Exercise, Point 6

## a. Tools used

Claude Code (Anthropic, Opus 5) in a terminal session, run against this repository directory.
No other AI tool was used.

> `TODO(you)`: add any other tool you used (IDE autocomplete, ChatGPT, etc.) before submitting —
> only Claude Code is claimed here because that is all this session can attest to.

## b. Usage areas

| Area | What the AI did |
|---|---|
| Reading the assignment | Extracted the text of `_Practical Assignment_SDET.pdf`. No PDF tooling (`poppler`, `pypdf`) was installed, so it wrote a short script to inflate the PDF's content streams and decode the glyph ids. |
| Requirement analysis | Restated FR-01…FR-05 as testable assertions and listed the ambiguities in `docs/1-requirement-analysis.md`. |
| Scenarios and test cases | Drafted the 10 risk-ranked scenarios and the 8 test cases, with the traceability tables. |
| Defect analysis | Compared the sample GET response field by field against FR-05. |
| Automation | Wrote the Page Object, the UI suite, the FR-05 JSON Schema, the stub servers and the API suite; ran the suite until green. |
| This document | Drafted from the session's own history. |

## c. Modifications made

**1. The first PDF extraction produced garbage and had to be redone.**
The initial script decompressed every stream in the PDF and printed anything that looked like text,
which returned embedded font-subset data — output like `Iûý5B ... TMC` that reads as text but is
not. The fix was to restrict extraction to content streams (those containing `BT`/`ET` text
objects) and to map the glyph ids through the font's offset (`cid + 29`) instead of treating the
bytes as characters. Without that second pass every number in the assignment was silently missing —
"top 10 scenarios" read as "top scenarios", "minimum 8 test cases" as "minimum test cases" — which
would have produced a deliverable that quietly missed its own quantitative requirements. Lesson:
when an extraction step "mostly works", check what it dropped, not just what it produced.

**2. The `suggestion_list` finding was split into a defect and an ambiguity.**
The first analysis reported "returns all suggestions instead of matching ones" as a flat defect.
That is not watertight: under FR-02's prefix matching, all three seed suggestions genuinely *do*
start with the selected value `agile methodology`, so returning all three is defensible. Only point
5(d)'s explicit "not all suggestions" resolves it. The doc now records `DEF-05` against the 5(d)
reading and `AMB-01` as the competing interpretation needing product confirmation. Reporting a
contestable defect flatly is how a bug report gets closed as "works as designed"; naming the
assumption gets it answered instead.

**3. The negative API tests were asserting on the wrong failure.**
The three malformed payloads were first derived from the assignment's sample response — which
already violates the contract in four ways — so JSON Schema reported the `locale` error for all
three, and the "missing `account_email`" and "`completed` is a string" cases both failed for a
reason unrelated to what they were testing. They are now derived from a corrected
(`COMPLIANT_RESPONSE`) payload, so each has exactly one thing wrong, plus a control test proving
the corrected payload validates. A negative test that passes for the wrong reason is worse than no
test at all.

**4. Defect-encoding tests were made `xfail(strict=True)` rather than left failing.**
The tests that encode DEF-01…DEF-05 assert the *correct* behaviour against a payload known to be
wrong, so they fail by design. Left as plain failures the suite is permanently red and nobody reads
it; as strict `xfail`s the suite is green while the defect reproduces and breaks loudly the moment
it is fixed, which makes the defect list self-verifying.

## d. AI limitations observed

**1. It reported extracted text confidently while silently dropping every digit.** The
first-pass output was fluent, plausible English with the numbers missing, and nothing in the output
flagged the loss — the failure mode was not an error but a confident partial answer. Verifying
against the raw PDF byte stream was the only way to catch it.

**2. It initially flattened a genuine specification ambiguity into a definite defect.** Given
FR-02 and point 5(d), which pull in opposite directions on `suggestion_list`, the default behaviour
was to pick the reading that made a cleaner-looking bug report rather than to surface the conflict.
Requirement conflicts are exactly what a tester is paid to notice, and the AI needed to be pushed
to separate the two.

**3. It over-produced by default.** Left unconstrained it drafted more scenarios, test cases and
tests than the assignment asked for. The stated minimums (10 scenarios, 8 test cases, 2 negative
API cases) are what a reviewer grades against; scope had to be capped explicitly.
