<!--
  COMMITTED AND PUBLIC, and the single source of instructions for every AI
  assistant working in this repo. Claude Code reads it through the @AGENTS.md
  import in CLAUDE.md; Copilot is pointed here by .github/copilot-instructions.md.

  Write only what a reader needs going forward. No history: no dates, no "this
  was changed", no rationale about superseded designs. If a fact is only
  interesting because of how the code got here, it belongs in
  .status/decisions.md, which is gitignored and is the place for that.

  Every line must be true on any machine and on Linux CI: no drive letters, no
  absolute paths, no secrets. Machine facts go in .status/local-environment.md.
  Do not restate anything that changes on its own - test counts, version pins.
  Point at the file that owns the fact. Target: under 200 lines.
-->

# hed-vis

Visualization library for HED (Hierarchical Event Descriptors) annotated data: word clouds and visual summaries of HED tags. Published to PyPI as `hedvis`. This is a companion to the core `hedtools` package (the hed-python repository), which it depends on for all HED functionality.

**This repo is visualization only.** Schema loading, validation, BIDS handling, and analysis live in hedtools. Import HED core from `hed.*`; never reimplement or copy it here.

## Commands

Test framework: unittest. Never convert the suite from one style to the other as a side effect of other work.

Run from the repo root. `python` must be an interpreter with this package installed (`pip install -e ".[dev]"`).

| Task                  | Command                                                                               |
| --------------------- | ------------------------------------------------------------------------------------- |
| Tests (the gate)      | `python -m unittest discover tests -v`                                                |
| One test file         | `python -m unittest tests.test_tag_word_cloud -v`                                     |
| One test              | `python -m unittest tests.test_tag_word_cloud.TestTagWordCloud.test_create_wordcloud` |
| Lint                  | `ruff check .`                                                                        |
| Format check          | `ruff format --check .`                                                               |
| Spell check           | `typos`                                                                               |
| Markdown format check | `mdformat --check --wrap no --number *.md` and the same for `docs/*.md`               |
| Docs build            | `sphinx-build -b html . _build/html` run from `docs/` (needs the `docs` extra)        |

CI (`.github/workflows/`) runs the tests on Ubuntu across Python 3.10-3.14 on `main` (3.10 and 3.13 on feature branches), on Windows for 3.10-3.12 (`main` and PRs to `main` only), plus coverage, ruff, typos, mdformat, a lychee link check (`lychee.toml`), and the docs build, which deploys to GitHub Pages on push to `main`. If the commands above pass locally, CI passes.

Never quote pass or skip counts in a committed file: they change with every commit, and a stale count reads as a target.

## Layout

- `hedvis/` - the package (flat layout; import as `hedvis`)
  - `core/` - the main API
    - `tag_visualizer.py` - `HedTagVisualizer`: builds visualizations from `HedTagCounts`, `TabularInput`, or a pandas DataFrame
    - `visualization_config.py` - `VisualizationConfig` and `WordCloudConfig` dataclasses, with `from_dict()` / `to_dict()`
    - `sequence_map.py` - sequence mapping utilities
  - `generators/` - `word_cloud.py` (`create_wordcloud`, `word_cloud_to_svg`) and `word_cloud_util.py` (color functions, contours, PIL/matplotlib helpers)
  - `tools/` - **legacy pre-reorganization API.** Not exported by `hedvis/__init__.py`, kept for transition, due for deprecation. Do not add code here.
- `hedvis/__init__.py` - the public API: `HedTagVisualizer`, `VisualizationConfig`, `WordCloudConfig`, `create_wordcloud`, `word_cloud_to_svg`
- `tests/` - **unittest, not pytest**: `TestCase` classes, run by `python -m unittest discover tests`
- `scripts/` - `visualize_hed_tags.py`, a runnable end-to-end example
- `examples/` - demos and experiments, not shipped with the package
- `docs/` - Sphinx sources (furo theme, myst-parser); `docs/_build/` is generated
- `qlty.toml` - complexity and maintainability thresholds
- `RELEASE_GUIDE.md` - the release procedure; the version lives in `pyproject.toml`
- `.status/` - working notes. **Gitignored; local to each machine.**

Dependencies and the extras `dev` and `docs` are declared in `pyproject.toml`; there are no requirements files, and there is no `[project.scripts]` entry - the package is a library.

## Conventions that differ from defaults

- **Google-style docstrings, but the section header is `Parameters:`, not `Args:`.**
- **Markdown headers are sentence case** - capitalize the first word only, plus proper nouns and acronyms.
- **ASCII only** in prose, comments, docstrings, and filenames: `-` not em/en dashes, `->` not arrows, `...` not an ellipsis character, straight quotes. Author names and recorded data keep whatever characters they contain.
- **Absolute imports from `hedvis`**, never relative imports across packages.
- **Committed files carry no project history.** No dates, no "this was changed", no phase or session labels. Rationale about how the code got here goes in `.status/decisions.md`.
- **Nothing that ships may reference `.status/`.** It is gitignored, so such a pointer is a dead link for every reader but its author. The exception is the files whose job is to orient a tool - this file, `CLAUDE.md`, `.github/copilot-instructions.md`, `.gitignore`, and `.claude/settings.json`.
- **No committed file contains a local path or a drive letter.** Those go in `.status/local-environment.md`.
- `ruff format` is the authority on Python formatting: `line-length = 120`, `E501` disabled. Root and `docs/` markdown is formatted by `mdformat --wrap no --number` and is CI-checked; files under `.github/` are not.
- The repo is LF-only: `.gitattributes` sets `* text=auto eol=lf`, and every text-mode write passes `newline="\n"` (or `newline=""` when the content already carries `\n`) so Windows does not write CRLF.

## Rules that are easy to get wrong

- **Word cloud generation is non-deterministic** - word placement is random. Tests assert structural properties (dimensions, format, presence of words), never pixel-perfect output. Do not "fix" a flaky-looking image comparison by pinning pixels.
- **Import HED core from hedtools.** Tag counting is `hed.tools.analysis` (`HedTagCounts`, `TabularSummary`); file errors raise `HedFileError` from `hed.errors.exceptions`. If a HED operation seems missing, it is in hedtools, not something to write here.
- **JPEG output needs the RGBA-to-RGB conversion** that `HedTagVisualizer` already does; PNG keeps transparency. Mask images are RGBA.
- Validate word-frequency dictionaries, font paths, and mask paths before use; keep dimensions user-configurable rather than hardcoded.
- `typos` is configured in `pyproject.toml` with domain-specific exceptions (`hed`, `parms`, ...). Add to `[tool.typos.default.extend-words]` rather than "fixing" a false positive in code.

## Related repositories

Referred to by name, never by path.

- `hed-python` - the `hedtools` package, this library's core dependency.
- `hed-schemas` - the HED vocabularies; loaded through hedtools, never directly.
- `hed-specification` - the formal annotation rules.
- `hed-examples` - example datasets and use cases.

## Where the thinking lives

`.status/` is gitignored, so it exists only on the machine that wrote it and never in a fresh clone or worktree.

- `.status/README.md` - the index. Read this first; it lists what is active.
- `.status/decisions.md` - why things are the way they are, and the home for anything historical. Read before proposing structural changes. Append entries; never rewrite one.
- `.status/plans/*.md` - active plans. Check the `Status:` header and the `[ ]` / `[x]` markers before starting work.
- `.status/notes/*.md` - dated records of what happened. Write-once reference material, not instructions.
- `.status/local-environment.md` - this machine's paths, interpreter, and quirks. Tool-agnostic, because more than one assistant works here. Never copy its contents into a committed file.
- IMPORTANT: do not read `.status/archive/` unless a file is named for you. Nothing new is created at the `.status/` root - new material goes in `plans/`, `prompts/`, `notes/`, or `scratch/`.

## Working agreements

- **IMPORTANT: every file written to `.status/` opens with a `For humans:` summary.** Three or four sentences, at the very top, before any other heading: what this file is, and the one or two things a person needs to take away from it. Write it plainly - no throat-clearing, no restating the title. The same applies to a long answer in a session: lead with the conclusion.
- IMPORTANT: never delete or rewrite a file under `.status/` without asking first. Appending is fine.
- IMPORTANT: temporary scripts, experiments, and one-off test files go in `.status/scratch/` - never the repository root. Anything in `scratch/` may be deleted unread.
- Show evidence, not assertions: the command you ran and its actual output.
- For a change spanning more than three files, write a plan to `.status/plans/` and stop for review before editing.
- Do not commit, push, or create branches unless asked.
