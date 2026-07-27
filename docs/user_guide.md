---
myst:
  html_meta:
    description: HED visualization user guide - Comprehensive guide for creating visualizations from HED-annotated data
    keywords: HED visualization, word cloud tutorial, hedvis guide, HED tools, configuration API
---

```{index} user guide
```

```{index} tutorial
```

# HED visualization guide

**hedvis** (HED Visualization Tools) is a Python package that provides visualization utilities for {index}`HED (Hierarchical Event Descriptors)` annotated datasets. It focuses on creating {index}`word clouds <word cloud>` and {index}`visual summaries <visualization>` from HED tag data.

This package is a companion library to [hedtools](https://github.com/hed-standard/hed-python), the core HED Python tools package. While hedtools handles HED schema management, validation, and data processing, hedvis provides specialized visualization capabilities.

```{index} tag frequency
```

```{index} patterns; visualization
```

## Why use hedvis?

{index}`HED-annotated datasets <dataset; HED-annotated>` contain rich semantic information about events and experimental conditions. hedvis makes it easy to:

- **Visualize tag frequency** - Create word clouds showing which {index}`HED tags <tag; HED>` are most commonly used
- **Identify patterns** - Quickly spot dominant tags and {index}`event types <event>` in your data
- **Generate reports** - Produce {index}`publication-ready visualizations <visualization; publication-ready>`
- **Explore datasets** - Get a quick visual overview of what's in your data

```{index} mask image
```

```{index} colormap
```

```{index} PNG format
```

```{index} SVG format
```

## Key features

### Word cloud generation

- Create customizable word clouds from {index}`HED tag frequencies <tag frequency>`
- Support for {index}`shaped clouds <word cloud; shaped>` using {index}`mask images <mask image>`
- Flexible {index}`color schemes <colormap>` and layouts
- Export to {index}`PNG <PNG format>` and {index}`SVG <SVG format>` formats

```{index} hedtools
```

```{index} BIDS dataset
```

```{index} tag template
```

```{index} HedTagVisualizer
```

### Integration with hedtools

- Works seamlessly with {index}`hedtools` data structures
- Process data from {index}`BIDS datasets <BIDS dataset>`, {index}`spreadsheets <tabular data>`, or {index}`dataframes <pandas DataFrame>`
- Automatic {index}`tag frequency counting <tag frequency>`
- Support for {index}`tag templates <tag template>` and {index}`filtering <tag; filtering>`

### Two APIs for flexibility

- **New API** - Modern, {index}`configuration-based interface <VisualizationConfig>` using {index}`HedTagVisualizer`
- **Legacy API** - Simple {index}`functional interface <API; legacy>` for quick word cloud generation

## Quick start

```{index} quick start
```

```python
from hedvis import HedTagVisualizer

# Create visualizer with default configuration
visualizer = HedTagVisualizer()

# Visualize from pre-computed tag counts (from hedtools)
results = visualizer.visualize_from_counts(tag_counts)

# Save word cloud
results["word_cloud"]["wordcloud_object"].to_file("output.png")
```

## Getting started with hedvis

```{index} getting started
```

### Installation

```{index} installation
```

Install hedvis from PyPI:

```bash
pip install hedvis
```

This automatically installs hedtools and all required dependencies.

#### Installing with Optional Dependencies

```{index} dependencies; optional
```

```{index} pip extras
```

```{index} pyproject.toml
```

**All dependencies are managed in `pyproject.toml`, which is the single source of truth.** Install optional extras as needed.

**Important:** When you install with extras (e.g., `[dev]` or `[docs]`), pip automatically installs all base dependencies (hedtools, numpy, pandas, matplotlib, etc.) plus the specified extra tools. You don't need a separate installation step for base dependencies.

**Key distinction:**

- Use `"hedvis[extra]"` when installing from **PyPI** (the published package)
- Use `".[extra]"` when installing from **local source** (after cloning the repository)

**Development tools** (formatting, linting, testing):

```bash
# From PyPI
pip install "hedvis[dev]"

# From local source (after cloning)
pip install ".[dev]"          # Regular install

# Editable local source install for active development
pip install -e ".[dev]"       # Editable install 
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

**For development** (editable installation from source):

```bash
git clone https://github.com/hed-standard/hed-vis.git
cd hed-vis
pip install -e ".[dev]"
```

#### Installing from Source (Core Dependencies Only)

To install from source without optional dependencies:

```bash
git clone https://github.com/hed-standard/hed-vis.git
cd hed-vis
pip install .
```

#### Installing from GitHub

Install directly from the GitHub repository:

```bash
pip install git+https://github.com/hed-standard/hed-vis.git
```

#### Legacy Requirements Files

```{index} requirements files; deprecated
```

```{index} migration; dependencies
```

**Important:** Legacy requirements files (`requirements.txt`, `requirements-dev.txt`, `docs/requirements.txt`) are deprecated and will be removed in a future release. All dependencies are now managed exclusively in `pyproject.toml`.

Do not use:

- ~~`pip install -r requirements.txt`~~ → Use `pip install .` or `pip install hedvis`
- ~~`pip install -r requirements-dev.txt`~~ → Use `pip install ".[dev]"`
- ~~`pip install -r docs/requirements.txt`~~ → Use `pip install ".[docs]"`

### Basic imports

```{index} imports; basic
```

```{index} API; new
```

```python
# New API (recommended)
from hedvis import HedTagVisualizer, VisualizationConfig, WordCloudConfig

# Legacy API (simple word clouds)
from hedvis import create_wordcloud, word_cloud_to_svg
```

```{index} create_wordcloud
```

```{index} word frequency
```

## Basic word clouds

### Simple word cloud from dictionary

The easiest way to create a {index}`word cloud` is from a {index}`dictionary` of {index}`word frequencies <word frequency>`:

```python
from hedvis import create_wordcloud

# Define word frequencies
word_freq = {"Event": 15, "Action": 10, "Sensory-event": 8, "Visual-presentation": 7, "Agent-action": 5}

# Create word cloud
wc = create_wordcloud(word_freq, width=800, height=600)

# Save as image
wc.to_file("my_wordcloud.png")
```

```{index} word_cloud_to_svg
```

### Converting to SVG

{index}`SVG format <SVG format>` is useful for {index}`publications <visualization; publication-ready>` and web display:

```python
from hedvis import create_wordcloud, word_cloud_to_svg

wc = create_wordcloud(word_freq)
svg_string = word_cloud_to_svg(wc)

# Save SVG to file
with open("wordcloud.svg", "w") as f:
    f.write(svg_string)
```

```{index} mask_path
```

### Using a mask image

Create {index}`shaped word clouds <word cloud; shaped>` using a {index}`mask image`:

```python
# Use a PNG image as mask (white areas = text, black = empty)
wc = create_wordcloud(word_freq, mask_path="brain_mask.png", background_color="white")
wc.to_file("shaped_wordcloud.png")
```

```{index} background_color
```

```{index} font size
```

```{index} colormap; viridis
```

### Customizing appearance

```python
wc = create_wordcloud(
    word_freq,
    width=1200,
    height=800,
    background_color="white",
    prefer_horizontal=0.9,  # 90% horizontal text
    min_font_size=10,
    max_font_size=100,
    colormap="viridis",
)
```

```{index} VisualizationConfig
```

```{index} WordCloudConfig
```

```{index} configuration; dictionary
```

## Configuration-based API

```{index} configuration; API
```

```{index} HedTagVisualizer
```

The new {index}`API` provides a more structured approach using {index}`configuration objects <configuration>`.

### Using configuration dictionaries

```python
from hedvis import HedTagVisualizer

# Define configuration as dictionary
config = {
    "word_cloud": {"width": 1000, "height": 700, "background_color": "white", "colormap": "plasma"},
    "output_formats": ["png", "svg"],
    "save_directory": "./visualizations",
}

# Create visualizer
visualizer = HedTagVisualizer(config)
```

### Using configuration classes

For better type safety and IDE support:

```python
from hedvis import HedTagVisualizer, VisualizationConfig, WordCloudConfig

# Configure word cloud
wc_config = WordCloudConfig(
    width=1200,
    height=800,
    background_color="white",
    colormap="viridis",
    prefer_horizontal=0.8,
    min_font_size=12,
    max_font_size=120,
)

# Configure visualizer
viz_config = VisualizationConfig(
    word_cloud=wc_config, output_formats=["png", "svg"], save_directory="./output", save_files=True
)

# Create visualizer
visualizer = HedTagVisualizer(viz_config)
```

### Masked word clouds with configuration

```python
wc_config = WordCloudConfig(
    width=1000,
    height=1000,
    use_mask=True,
    mask_path="brain_outline.png",
    background_color="white",
    contour_width=3,
    contour_color="navy",
)

viz_config = VisualizationConfig(word_cloud=wc_config)
visualizer = HedTagVisualizer(viz_config)
```

```{index} HedTagCounts
```

```{index} tag counts
```

## Working with HED data

### From pre-computed tag counts

If you've already computed {index}`tag frequencies <tag frequency>` using {index}`hedtools`:

```python
from hed.tools.analysis.hed_tag_counts import HedTagCounts
from hedvis import HedTagVisualizer

# Assume you have tag_counts from hedtools analysis
# tag_counts = HedTagCounts(...)

visualizer = HedTagVisualizer()
results = visualizer.visualize_from_counts(tag_counts)

# Access the word cloud
wc = results["word_cloud"]["wordcloud_object"]
wc.to_file("hed_tags.png")
```

```{index} TabularInput
```

```{index} sidecar file
```

```{index} events file
```

### From tabular data

Visualize directly from {index}`BIDS-style <BIDS dataset>` {index}`tabular data`:

```python
from hed import load_schema
from hed.models import TabularInput
from hedvis import HedTagVisualizer

# Load HED schema
schema = load_schema()

# Load your data
events_file = "sub-01_events.tsv"
sidecar_file = "task-experiment_events.json"
tabular = TabularInput(events_file, sidecar=sidecar_file)

# Create visualizer
visualizer = HedTagVisualizer()

# Generate visualizations
results = visualizer.visualize_from_tabular(
    tabular, schema, output_basename="experiment_tags", include_context=True, replace_defs=True
)

# Save outputs
wc = results["word_cloud"]["wordcloud_object"]
wc.to_file("experiment_wordcloud.png")
```

```{index} pandas DataFrame
```

```{index} visualize_from_dataframe
```

### From pandas DataFrame

Work directly with {index}`pandas DataFrames <pandas DataFrame>`:

```python
import pandas as pd
from hed import load_schema
from hedvis import HedTagVisualizer

# Load your data
df = pd.read_csv("events.tsv", sep="\t")

# Load schema
schema = load_schema()

# Create visualizer with config
config = {"word_cloud": {"width": 1000, "height": 600}, "output_formats": ["svg"], "save_directory": "./output"}
visualizer = HedTagVisualizer(config)

# Generate visualizations
results = visualizer.visualize_from_dataframe(df, schema, name="my_dataset")
```

### Using tag templates

Organize tags by category using templates:

```python
# Define which tags to include by category
tag_template = {
    "sensory": ["Sensory-event", "Visual-presentation", "Auditory-presentation"],
    "actions": ["Agent-action", "Action"],
    "timing": ["Onset", "Offset", "Duration"],
}

results = visualizer.visualize_from_counts(tag_counts, tag_template=tag_template, output_basename="categorized_tags")
```

```{index} customization
```

```{index} colormap; plasma
```

```{index} colormap; matplotlib
```

```{index} color_range
```

## Advanced customization

### Custom color schemes

```python
from hedvis import WordCloudConfig

# Use built-in matplotlib colormaps
config = WordCloudConfig(
    colormap="plasma",  # Options: viridis, plasma, inferno, magma, etc.
    color_range=(0.2, 0.8),  # Use middle 60% of colormap
)

# Or use color names
config = WordCloudConfig(background_color="navy", contour_color="gold")
```

```{index} font_path
```

```{index} font; custom
```

```{index} prefer_horizontal
```

### Font customization

```python
config = WordCloudConfig(
    font_path="/path/to/custom-font.ttf",
    min_font_size=10,
    max_font_size=150,
    prefer_horizontal=0.95,  # Nearly all horizontal text
)
```

### Scaling and layout

```python
config = WordCloudConfig(
    relative_scaling=0.8,  # Word size scaling factor
    scale_adjustment=1.5,  # Frequency scaling
    prefer_horizontal=0.75,  # 75% horizontal orientation
)
```

### Processing multiple datasets

```python
visualizer = HedTagVisualizer()

datasets = [("baseline", baseline_counts), ("task", task_counts), ("rest", rest_counts)]

for name, counts in datasets:
    results = visualizer.visualize_from_counts(counts, output_basename=f"{name}_tags")
    results["word_cloud"]["wordcloud_object"].to_file(f"{name}_cloud.png")
```

## Output formats

### PNG output

Raster image format, good for presentations and papers:

```python
wc = create_wordcloud(word_freq)
wc.to_file("output.png")
```

### SVG output

Vector format, scalable and editable:

```python
from hedvis import word_cloud_to_svg

wc = create_wordcloud(word_freq)
svg = word_cloud_to_svg(wc)

with open("output.svg", "w") as f:
    f.write(svg)
```

### Automatic output management

Let the visualizer handle file saving:

```python
config = VisualizationConfig(output_formats=["png", "svg"], save_directory="./results", save_files=True)

visualizer = HedTagVisualizer(config)
results = visualizer.visualize_from_counts(tag_counts)

# Files automatically saved to ./results/
```

```{index} best practices
```

```{index} data preparation
```

```{index} tag; filtering
```

## Best practices

### 1. Data preparation

- Use {index}`hedtools` to compute {index}`tag frequencies <tag frequency>` before visualization
- {index}`Filter <tag; filtering>` out unwanted tag types (e.g., `Condition-variable`, `Task`)
- Consider using {index}`tag templates <tag template>` to organize visualizations by category

### 2. Visual design

- Choose dimensions appropriate for your output medium:
  - Presentations: 1920x1080 or 1600x900
  - Papers: 1200x800 or 1000x600
  - Web: 800x600 or flexible SVG
- Use transparent backgrounds for flexibility
- Select colormaps appropriate for your audience (colorblind-friendly when possible)

### 3. Mask images

- Use high-contrast black/white images for masks
- PNG format recommended for masks
- Ensure mask resolution matches desired output size
- Test mask shape before applying to real data

### 4. Performance

- For large datasets, compute tag counts once and reuse
- Save intermediate results (tag counts) for reproducibility
- Use appropriate image dimensions - larger isn't always better

### 5. Reproducibility

- Save configuration dictionaries alongside outputs
- Document HED schema versions used
- Include tag templates in documentation
- Version control visualization scripts

```{index} troubleshooting
```

```{index} errors; empty word cloud
```

## Troubleshooting

### Word cloud appears empty

**Problem**: {index}`Word cloud` generates but shows no words.

**Solutions**:

- Check that word_freq dictionary is not empty
- Verify frequencies are positive numbers
- Ensure dimensions are large enough (minimum 100x100)
- Check if mask is blocking all text placement

```{index} errors; font not found
```

### Font not found error

**Problem**: Custom {index}`font path <font_path>` raises an error.

**Solutions**:

- Verify font file exists at specified path
- Ensure font is .ttf, .otf, or .ttc format
- Try with `font_path=None` (uses default)
- Check file permissions

```{index} errors; mask not applied
```

### Mask not applied

**Problem**: {index}`Mask image` specified but word cloud is rectangular.

**Solutions**:

- Verify mask path is correct
- Check mask is high-contrast (black/white)
- Ensure mask is PNG or JPEG format
- Try converting mask to pure black/white

```{index} errors; import
```

```{index} installation
```

### Import errors

**Problem**: Cannot import {index}`hedvis` modules.

**Solutions**:

- Ensure installation: `pip install hedvis`
- For development: install in editable mode `pip install -e .`
- Activate virtual environment if using one
- Check Python version (3.10+ required)

### Colors look wrong

**Problem**: Word cloud colors don't match expectations.

**Solutions**:

- Check colormap name spelling
- Try standard colormaps: 'viridis', 'plasma', 'rainbow'
- Adjust `color_range` parameter
- Set `background_color` explicitly

```{index} performance
```

```{index} optimization
```

### Performance issues

**Problem**: Word cloud generation is slow.

**Solutions**:

- Reduce image dimensions
- Simplify mask if using one
- Reduce number of words (filter low-frequency tags)
- Check available RAM

## Examples gallery

### Example 1: Publication-ready word cloud

```python
from hedvis import HedTagVisualizer, WordCloudConfig, VisualizationConfig

# High-quality configuration
wc_config = WordCloudConfig(
    width=1600,
    height=900,
    background_color="white",
    colormap="viridis",
    prefer_horizontal=0.85,
    min_font_size=12,
    max_font_size=100,
)

viz_config = VisualizationConfig(word_cloud=wc_config, output_formats=["png", "svg"])

visualizer = HedTagVisualizer(viz_config)
results = visualizer.visualize_from_counts(tag_counts)
```

### Example 2: Brain-shaped word cloud

```python
config = WordCloudConfig(
    use_mask=True,
    mask_path="brain_outline.png",
    background_color="white",
    contour_width=4,
    contour_color="darkblue",
    colormap="cool",
)

visualizer = HedTagVisualizer(VisualizationConfig(word_cloud=config))
results = visualizer.visualize_from_counts(tag_counts)
```

### Example 3: Dark theme word cloud

```python
config = WordCloudConfig(background_color="black", colormap="plasma", color_range=(0.3, 0.9), prefer_horizontal=0.7)

visualizer = HedTagVisualizer(VisualizationConfig(word_cloud=config))
results = visualizer.visualize_from_counts(tag_counts)
```

## Next steps

- Explore the [API reference](api/index.rst) for complete function documentation
- Check out example scripts in the `examples/` directory
- Visit [HED resources](https://www.hedtags.org/hed-resources) for more HED tutorials
- Join discussions in the [HED forum](https://github.com/orgs/hed-standard/discussions)

```{index} related projects
```

```{index} hed-python
```

```{index} hed-schemas
```

## Related projects

- **[hed-python](https://github.com/hed-standard/hed-python)**: Core HED Python tools for validation, schema management, and analysis
- **[hed-schemas](https://github.com/hed-standard/hed-schemas)**: Official HED schemas in multiple formats
- **[table-remodeler](https://github.com/hed-standard/table-remodeler)**: Python tools for manipulating and restructuring tables

```{index} help
```

```{index} support
```

## Finding help

```{index} documentation
```

### Documentation

- See this documentation for detailed usage guides and API reference
- Visit [HED resources](https://www.hedtags.org/hed-resources) for general HED documentation
- Check the [Python hedtools documentation](https://www.hedtags.org/hed-python) for core HED functionality

```{index} issues
```

```{index} bug reports
```

### Issues and problems

If you encounter bugs or have feature requests:

- **hedvis issues**: [open an issue](https://github.com/hed-standard/hed-vis/issues) in the hed-vis repository
- **hedtools issues**: [open an issue](https://github.com/hed-standard/hed-python/issues) in the hed-python repository
- **Questions or ideas**: [HED organization discussions](https://github.com/orgs/hed-standard/discussions)
- **Contact**: [hed.maintainers@gmail.com](mailto:hed.maintainers@gmail.com)
