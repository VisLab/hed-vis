![PyPI - Status](https://img.shields.io/pypi/v/hedvis) ![Python3](https://img.shields.io/badge/python-%3E=3.10-yellow.svg) [![Maintainability](https://qlty.sh/gh/hed-standard/projects/hed-vis/maintainability.svg)](https://qlty.sh/gh/hed-standard/projects/hed-vis) [![Code Coverage](https://qlty.sh/gh/hed-standard/projects/hed-vis/coverage.svg)](https://qlty.sh/gh/hed-standard/projects/hed-vis) [![Docs](https://img.shields.io/badge/docs-hed--vis-blue.svg)](https://www.hedtags.org/hed-vis)

# HED visualization

**hedvis** provides word cloud generation and visual summaries for HED-annotated data, making it easy to explore and present the semantic content of your experimental datasets.

## Features

- **Word Cloud Generation** - Create beautiful word clouds from HED tag frequencies
- **Flexible Configuration** - Extensive customization options for visualizations
- **Shaped Clouds** - Support for mask images to create custom-shaped word clouds
- **Multiple Formats** - Export to PNG and SVG formats
- **hedtools Integration** - Seamless integration with the HED Python tools ecosystem
- **Two APIs** - A modern configuration-based API (`VisualizationConfig`) and a simple legacy API for quick tasks

## Installation

### From PyPI (recommended)

Install the latest stable release:

```bash
pip install hedvis
```

This automatically installs hedtools and all required dependencies.

### Development installation

For development work, clone the repository and install in editable mode:

```bash
git clone https://github.com/hed-standard/hed-vis.git
cd hed-vis
pip install -e .
```

### Installing optional dependencies

**The project uses `pyproject.toml` as the single source of truth for all dependencies.** Install optional dependencies using pip extras.

**Important:** Installing with extras automatically includes all base dependencies (hedtools, numpy, pandas, etc.) plus the extra tools.

**Development tools** (code formatting, linting, testing):

```bash
# From PyPI (if you installed hedvis from PyPI)
pip install "hedvis[dev]"

# From local source (if you cloned the repository)
pip install ".[dev]"          # Regular install
pip install -e ".[dev]"       # Editable install (recommended for development)
```

**Documentation tools** (Sphinx, themes):

```bash
# From PyPI
pip install "hedvis[docs]"

# From local source
pip install ".[docs]"
```

**Both dev and docs dependencies**:

```bash
# From PyPI
pip install "hedvis[dev,docs]"

# From local source
pip install ".[dev,docs]"
```

### Installing from source without extras

To install from source with only the core dependencies:

```bash
git clone https://github.com/hed-standard/hed-vis.git
cd hed-vis
pip install .
```

If you need to install dependencies for development or documentation:

- Use `pip install ".[dev]"` instead of `pip install -r requirements-dev.txt`
- Use `pip install ".[docs]"` instead of `pip install -r docs/requirements.txt`
- Core dependencies are installed automatically with `pip install .` or `pip install hedvis`

## Quick start

### Simple word cloud

```python
from hedvis import create_wordcloud

# Create word cloud from frequency dictionary
word_freq = {"Event": 15, "Action": 10, "Sensory-event": 8, "Visual-presentation": 7}

wc = create_wordcloud(word_freq, width=800, height=600)
wc.to_file("wordcloud.png")
```

### Using the hedvis API

```python
from hedvis import HedTagVisualizer, WordCloudConfig, VisualizationConfig

# Configure visualization
wc_config = WordCloudConfig(width=1200, height=800, background_color="white", colormap="viridis")

viz_config = VisualizationConfig(word_cloud=wc_config, output_formats=["png", "svg"])

# Create visualizer
visualizer = HedTagVisualizer(viz_config)

# Generate from HED tag counts (from hedtools)
results = visualizer.visualize_from_counts(tag_counts)
```

### Integration with hedtools

```python
from hed import load_schema
from hed.models import TabularInput
from hedvis import HedTagVisualizer

# Load HED schema and data
schema = load_schema()
tabular = TabularInput("events.tsv", sidecar="events.json")

# Create visualizer
visualizer = HedTagVisualizer()

# Generate visualizations
results = visualizer.visualize_from_tabular(tabular, schema, output_basename="experiment_tags")

# Save word cloud
results["word_cloud"]["wordcloud_object"].to_file("tags.png")
```

All dependencies are managed in `pyproject.toml` and installed automatically with `pip install hedvis`.

For the complete list of dependencies with exact versions, see the `dependencies` section in [pyproject.toml](pyproject.toml).

## Development setup

### Prerequisites

- Python 3.10 or higher
- Git
- pip (Python package manager)

### Setting up your development environment

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/hed-vis.git
   cd hed-vis
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows PowerShell
   source .venv/bin/activate  # On Unix/MacOS
   ```

3. **Install in development mode:**

   All dependencies are managed in `pyproject.toml`. Install the package with development tools:

   ```bash
   pip install -e ".[dev]"
   ```

   This installs:

   - The hedvis package in editable mode
   - All required dependencies (hedtools, wordcloud, matplotlib, etc.)
   - Development tools (ruff, typos, mdformat)
   - Testing tools (coverage)

   To install additional optional dependencies:

   ```bash
   # Documentation tools
   pip install -e ".[docs]"

   # Both dev and docs
   pip install -e ".[dev,docs]"
   ```

   **Note:** Do not use legacy requirements files (`requirements.txt`, `requirements-dev.txt`). All dependencies are defined in `pyproject.toml`.

4. **Run tests to verify setup:**

   ```bash
   python -m unittest discover tests
   ```

## Related projects

- [hedtools](https://github.com/hed-standard/hed-python) - Core HED tools for validation and analysis
- [hed-schemas](https://github.com/hed-standard/hed-schemas) - Official HED schemas
- [hed-specification](https://github.com/hed-standard/hed-specification) - HED specification
- [table-remodeler](https://github.com/hed-standard/table-remodeler) - Sister project with table manipulation tools

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- HED homepage: [https://www.hedtags.org](https://www.hedtags.org)
- Repo docs: [https://www.hedtags.org/hed-vis](https://www.hedtags.org/hed-vis)
- GitHub issues: [https://github.com/hed-standard/hed-vis/issues](https://github.com/hed-standard/hed-vis/issues)
- Ideas or questions: [https://github.com/orgs/hed-standard/discussions](https://github.com/orgs/hed-standard/discussions)
- HED Homepage: [https://www.hedtags.org](https://www.hedtags.org)
- Contact: [hed-maintainers@gmail.com](mailto:hed-maintainers@gmail.com)

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use hedvis in your research, please cite:

If you use HEDTools in your research, please cite:

```bibtex
@software{hedtools,
  author = {Ian Callanan, Robbins, Kay and others},
  title = {HEDVis: Visualization tools for HED},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/hed-standard/hed-vis},
}
```
