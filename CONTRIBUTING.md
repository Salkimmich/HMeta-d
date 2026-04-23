# Contributing

Thanks for improving HMeta-d Translation Lab.

## Workflow

1. Create a branch from `master`.
2. Keep changes focused to one concern (feature, bugfix, docs, or tests).
3. Run the full local validation gate before opening a PR:
   - Windows: `powershell -ExecutionPolicy Bypass -File .\scripts\validate.ps1`
   - macOS/Linux: `bash ./scripts/validate.sh`
4. Open a PR with:
   - clear problem statement
   - what changed and why
   - evidence (test output or reasoning)
5. Wait for CI to pass before merge.

## Code and Docs Expectations

- Prefer small, composable functions and immutable data structures.
- Keep MATLAB -> Python -> Clojure teaching annotations where they add value.
- Keep docs aligned with executable behavior (commands, phases, and CI job names).
- Do not commit generated artifacts (`__pycache__`, `.pytest_cache`, `.Rhistory`, build output).

## Testing Expectations

- Python changes should include or update pytest coverage in `python/`.
- Clojure changes should include or update tests in `test/hmeta_d/`.
- Cross-language behavior claims should reference tolerances in `docs/math_chain.md`.
- Keep dependency changes synchronized in:
  - `python/requirements.txt` (minimums)
  - `python/requirements-lock.txt` (pinned validation baseline)
