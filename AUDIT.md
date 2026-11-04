# Repository audit — 4 November 2026

Source reviewed: `4c86e2840772c89d93248f9e1736e5a33ab99b67` on `main`. Changes are proposed on `audit/repository-improvements-2026-11-04`; nothing was merged or deployed.

## Changes

- Handle null asset IDs as missing values instead of crashing.
- Enable strict CSV parsing so unterminated quoted fields are rejected.
- Add regressions for both cases; preserve HTML escaping and input/output path guards.

## Verification

9 automated behavioral tests passed. All 4 recorded source/test checks passed. Local verification used Node.js 26.12.0 and Python 3.15.0; CI should also confirm the configured deployment versions.

- `python -m unittest discover -s tests -v`
- `Python AST parse for source files`

Local HTML asset references were compared with the complete GitHub file inventory. Real desktop/mobile visual verification was blocked in this environment: the in-app preview could not reach the local server and the desktop browser did not expose a usable window. No claim of browser/device acceptance is made. Automated DOM/canvas simulations, where present, do not replace that check.

## Remaining limits and rollout

- No authentication or database. CSV processing stays local.
- Reports are data-quality checks, not vulnerability assessments.
