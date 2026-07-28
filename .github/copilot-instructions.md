# HED-Vis developer instructions

Use Google format for docstrings (`Parameters:` not `Args:`).
When you create summaries of what you did, put them in the `./status` directory at the root of the repository.

> **Local environment**: If `status/local-environment.md` exists, read it first for machine-specific setup (OS, shell syntax, virtual environment activation).

## Markdown style

- Only capitalize the first letter of each heading (sentence case).
  - Correct: `## Project overview`
  - Wrong: `## Project Overview`

## Project overview

HED (Hierarchical Event Descriptors) is a framework for systematically describing events and experimental metadata. This Python repository (`hed-vis`) provides the **hedvis** package for visualization tools to create word clouds and visual summaries of HED-annotated datasets. This is a companion library to the core **hedtools** package.

### Related repositories

- **[hed-python](https://github.com/hed-standard/hed-python)**: Core HED tools package (hedtools) - this library's main dependency
- **[hed-schemas](https://github.com/hed-standard/hed-schemas)**: Standardized vocabularies (HED schemas) in XML/MediaWiki/OWL formats
- **[hed-specification](https://github.com/hed-standard/hed-specification)**: Formal specification defining HED annotation rules
- **[hed-examples](https://github.com/hed-standard/hed-examples)**: Example datasets and use cases

### Package distribution

- **PyPI package**: `hedvis` (install via `pip install hedvis`)
- **Core dependency**: `hedtools` (automatically installed)
- **Python version**: 3.10+ required
- **Online tools**: [hedtools.org](https://hedtools.org) for web-based HED tools

## Architecture & core components

### Package structure

The `hedvis` package provides visualization utilities for HED data:

- **`core/tag_visualizer.py`**: `HedTagVisualizer` — main class for generating visualizations from HED tag data
- **`core/visualization_config.py`**: `VisualizationConfig`, `WordCloudConfig` — configuration dataclasses
- **`core/sequence_map.py`**: Sequence mapping utilities
- **`generators/word_cloud.py`**: `create_wordcloud()`, `word_cloud_to_svg()` — word cloud generation functions
- **`generators/word_cloud_util.py`**: Color functions, contour generation, PIL/matplotlib helpers

### Key dependencies

- **hedtools**: Core HED functionality (schema loading, validation, analysis)
- **wordcloud**: Word cloud generation engine
- **matplotlib**: Colormap support for visualizations
- **PIL (Pillow)**: Image processing for masks and output
- **numpy**: Array operations for image manipulation

### Data flow patterns

**Basic word cloud generation**:

```python
from hedvis import create_wordcloud, word_cloud_to_svg

word_freq = {"Event": 10, "Action": 5, "Sensory": 8}
wc = create_wordcloud(word_freq, width=800, height=600)
wc.to_file("output.png")

svg_string = word_cloud_to_svg(wc)
```

**Integration with HED tools**:

```python
from hed.tools.analysis import TabularSummary
from hedvis import create_wordcloud

tag_counts = summary.get_tag_counts()
wc = create_wordcloud(tag_counts)
```

## Development environment

### Setup

**Always install in editable mode** for active development:

```bash
pip install -e .
```

This ensures code changes are immediately reflected without reinstalling.

### Key files

- Entry point: `hedvis/__init__.py` — exports public API (`HedTagVisualizer`, `VisualizationConfig`, `WordCloudConfig`, `create_wordcloud`, `word_cloud_to_svg`)
- Configuration: `pyproject.toml` — project metadata, dependencies, and tool configs (ruff)
- Code quality: `qlty.toml` — complexity and maintainability thresholds
- CI workflows: `.github/workflows/` — automated testing and quality checks

### Dependencies & compatibility

- Python 3.10+ required
- Core visualization: wordcloud, matplotlib, PIL (Pillow)
- Data processing: numpy, pandas
- HED integration: hedtools (provides all HED core functionality)
- Full dependency list in `pyproject.toml` under `[project.dependencies]`

## Line endings configuration

This repository is configured to use Unix-style line endings (`\n`, LF) across all platforms.

### Git configuration

- **`.gitattributes`**: Explicitly sets `* text=auto eol=lf` to normalize all text files to LF line endings on commit
- **Global Git config**: `core.autocrlf=false` and `core.eol=lf` (prevents automatic CRLF conversion on Windows)

### VS Code settings

The `.vscode/settings.json` is configured with:

```json
{
    "files.eol": "\n",
    "files.insertFinalNewline": true,
    "files.trimTrailingWhitespace": true
}
```

This ensures:
- New files created in VS Code use LF line endings
- Files always end with a newline (required by CI checks)
- Trailing whitespace is automatically cleaned up

### Python file I/O

Python scripts that write text files explicitly use `newline="\n"` to ensure LF line endings regardless of platform:

```python
# Correct: explicitly set LF line endings
with open(output_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

# Correct: use newline parameter with Path.write_text()
Path(path).write_text(content, encoding="utf-8", newline="\n")
```

## Development workflows

### Testing

- Use `unittest` framework exclusively (not pytest)
- Tests are in `tests/` directory, test data in `tests/data/`
- Run all tests: `python -m unittest discover tests -v`
- Run a single test: `python -m unittest tests.test_tag_word_cloud.TestTagWordCloud.test_create_wordcloud`
- Word cloud tests should test structural properties, not pixel-perfect output (placement is random)

### Linting & code quality

Always run these before pushing — they are checked in CI:

```bash
# Ruff linter and formatter (configured in pyproject.toml)
ruff check .
ruff format --check .

# Spell checking (configured in pyproject.toml)
typos

# Markdown formatting (docs and root .md files)
mdformat --check --wrap no --number docs/*.md
mdformat --check --wrap no --number *.md
```

Auto-fix: `ruff check --fix .` and `ruff format .`

### CI/CD pipeline

GitHub Actions in `.github/workflows/`:

- **`ci.yaml`**: Tests on Python 3.10–3.14 (Ubuntu); 3.10 and 3.13 on feature branches
- **`ci_windows.yaml`**: Windows tests on Python 3.10–3.12 (main/PRs to main only)
- **`ci_cov.yaml`**: Coverage reporting
- **`ruff.yaml`**: Ruff linter and formatter check
- **`typos.yaml`**: Spell checking
- **`mdformat.yaml`**: Markdown formatting check
- **`links.yaml`**: Dead link checking (lychee)
- **`docs.yml`**: Documentation build

### Validation checklist

Before pushing, run these to replicate CI locally:

1. `python -m unittest discover tests -v` — all tests pass
2. `ruff check .` — no lint errors
3. `ruff format --check .` — code is formatted
4. `typos` — no spelling errors

## Integration with hedtools

- Always import HED core functionality from `hedtools` package
- Use `hed.tools.analysis` for generating tag frequency data
- hedvis focuses solely on visualization of already-processed HED data
- Raise `HedFileError` from `hed.errors.exceptions` for file-related issues

## Visualization best practices

- Validate input word frequency dictionaries before processing
- Provide reasonable default dimensions for word clouds (minimum 100×100)
- Support both PNG and SVG output formats
- Handle transparency properly in mask images (RGBA mode)
- Use contour overlays for masked word clouds to enhance visibility

## Common pitfalls to avoid

- Don't assume word cloud generation is deterministic — it has random placement
- Don't mix pytest and unittest — this project uses unittest exclusively
- Always use absolute imports from `hedvis` package, not relative imports
- Import HED core functionality from `hedtools`, not from this package
- Always validate font paths and mask image paths before use
- Don't hardcode image dimensions — allow user customization
