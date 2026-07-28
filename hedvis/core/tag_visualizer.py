"""Main API for generating HED tag visualizations."""

from typing import Dict, Optional, Union, List, Any
from pathlib import Path
from PIL import Image
from hed import HedSchema
from hed.models import TabularInput
from hed.tools.analysis.hed_tag_counts import HedTagCounts
from hed.tools.analysis.event_manager import EventManager
from hed.tools.analysis.hed_tag_manager import HedTagManager
from hedvis.generators import word_cloud
from hedvis.core.visualization_config import VisualizationConfig


class HedTagVisualizer:
    """Generate visualizations from HED tag data.

    This class provides an API for creating visualizations from HED-annotated
    datasets without requiring the remodeling framework. It works directly with
    hedtools data structures.
    """

    def __init__(self, config: Union[VisualizationConfig, Dict, None] = None):
        """Initialize visualizer with configuration.

        Parameters:
            config: VisualizationConfig object or dictionary of settings.
                   If None, uses default configuration.
        """
        if config is None:
            config = VisualizationConfig()
        elif isinstance(config, dict):
            config = VisualizationConfig.from_dict(config)

        self.config = config

    def visualize_from_counts(
        self,
        tag_counts: HedTagCounts,
        tag_template: Optional[Dict[str, List[str]]] = None,
        output_basename: str = "hed_tags",
    ) -> Dict[str, Any]:
        """Generate visualizations from pre-computed tag counts.

        Parameters:
            tag_counts: HedTagCounts object with tag frequency data.
            tag_template: Optional dictionary organizing tags by category.
                         Keys are category names, values are lists of tag patterns.
            output_basename: Base name for output files.

        Returns:
            Dictionary with generated visualizations (paths and/or objects).
            Structure: {'word_cloud': {'wordcloud_object': ..., 'svg_path': ..., 'png_path': ...}}
        """
        results = {}

        # Extract word frequencies
        word_freq = self._extract_word_frequencies(tag_counts, tag_template)

        # Generate word cloud
        if self.config.word_cloud and word_freq:
            results["word_cloud"] = self._generate_word_cloud(word_freq, output_basename)

        return results

    def visualize_from_tabular(
        self,
        tabular_input: TabularInput,
        schema: HedSchema,
        tag_template: Optional[Dict[str, List[str]]] = None,
        output_basename: str = "hed_tags",
        include_context: bool = True,
        replace_defs: bool = True,
        remove_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate visualizations directly from tabular data.

        Parameters:
            tabular_input: TabularInput with HED annotations.
            schema: HED schema for validation and processing.
            tag_template: Optional dictionary organizing tags by category.
            output_basename: Base name for output files.
            include_context: Include contextual tags in counts.
            replace_defs: Replace Def tags with their definitions.
            remove_types: List of type tags to exclude (e.g., ['Condition-variable']).

        Returns:
            Dictionary with generated visualizations.
        """
        # Compute tag counts
        tag_counts = self._compute_tag_counts(
            tabular_input,
            schema,
            include_context=include_context,
            replace_defs=replace_defs,
            remove_types=remove_types or [],
        )

        # Generate visualizations
        return self.visualize_from_counts(tag_counts, tag_template, output_basename)

    def visualize_from_dataframe(
        self,
        df,
        schema: Union[HedSchema, str],
        sidecar=None,
        name: str = "dataset",
        tag_template: Optional[Dict[str, List[str]]] = None,
        output_basename: str = "hed_tags",
        include_context: bool = True,
        replace_defs: bool = True,
        remove_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate visualizations from a pandas DataFrame.

        Parameters:
            df: Pandas DataFrame with event data.
            schema: HED schema object or version string.
            sidecar: JSON sidecar dictionary or file path.
            name: Name for this dataset.
            tag_template: Optional dictionary organizing tags by category.
            output_basename: Base name for output files.
            include_context: Include contextual tags in counts.
            replace_defs: Replace Def tags with their definitions.
            remove_types: List of type tags to exclude.

        Returns:
            Dictionary with generated visualizations.
        """
        from hed import load_schema

        # Load schema if string provided
        if isinstance(schema, str):
            schema = load_schema(schema)

        # Create TabularInput
        tabular = TabularInput(df, sidecar=sidecar, name=name)

        # Generate visualizations
        return self.visualize_from_tabular(
            tabular,
            schema,
            tag_template=tag_template,
            output_basename=output_basename,
            include_context=include_context,
            replace_defs=replace_defs,
            remove_types=remove_types,
        )

    def _compute_tag_counts(
        self,
        tabular_input: TabularInput,
        schema: HedSchema,
        include_context: bool = True,
        replace_defs: bool = True,
        remove_types: Optional[List[str]] = None,
    ) -> HedTagCounts:
        """Compute tag counts from tabular input.

        Parameters:
            tabular_input: TabularInput with HED annotations.
            schema: HED schema for processing.
            include_context: Include contextual tags.
            replace_defs: Replace Def tags with definitions.
            remove_types: List of type tags to exclude.

        Returns:
            HedTagCounts: Computed tag frequency data.
        """
        if remove_types is None:
            remove_types = []

        tag_counts = HedTagCounts(tabular_input.name, total_events=len(tabular_input.dataframe))
        tag_man = HedTagManager(EventManager(tabular_input, schema), remove_types=remove_types)
        hed_objs = tag_man.get_hed_objs(include_context=include_context, replace_defs=replace_defs)
        for hed in hed_objs:
            tag_counts.update_tag_counts(hed, tabular_input.name)

        return tag_counts

    def _extract_word_frequencies(
        self, tag_counts: HedTagCounts, tag_template: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, int]:
        """Extract word frequencies from tag counts.

        Parameters:
            tag_counts: HedTagCounts object.
            tag_template: Optional template for organizing tags.

        Returns:
            Dictionary mapping tag strings to frequencies.
        """
        word_freq = {}

        if tag_template:
            # Use template to organize tags
            organized, unmatched = tag_counts.organize_tags(tag_template)

            # Extract frequencies from organized tags
            for _category, tags in organized.items():
                for tag in tags:
                    word_freq[tag.tag] = tag.events

            # Also include unmatched tags if they exist
            for tag in unmatched:
                word_freq[tag.tag] = tag.events
        else:
            # Use all tags from tag_dict - values are HedTagCount objects
            for _tag_key, tag_count in tag_counts.tag_dict.items():
                word_freq[tag_count.tag] = tag_count.events

        return word_freq

    def _generate_word_cloud(self, word_freq: Dict[str, int], output_basename: str) -> Dict[str, Any]:
        """Generate word cloud visualization.

        Parameters:
            word_freq: Dictionary mapping words to frequencies.
            output_basename: Base name for output files.

        Returns:
            Dictionary with word cloud data (file paths and/or objects).
        """
        wc_config = self.config.word_cloud

        # Prepare keyword arguments for word cloud generator
        kwargs = {
            "background_color": wc_config.background_color,
            "width": wc_config.width,
            "height": wc_config.height,
            "prefer_horizontal": wc_config.prefer_horizontal,
            "min_font_size": wc_config.min_font_size,
            "contour_width": wc_config.contour_width,
            "contour_color": wc_config.contour_color,
            "relative_scaling": wc_config.relative_scaling,
        }

        if wc_config.max_font_size:
            kwargs["max_font_size"] = wc_config.max_font_size

        if wc_config.font_path:
            kwargs["font_path"] = wc_config.font_path

        # Set up color function
        from hedvis.generators.word_cloud_util import ColormapColorFunc

        color_func = ColormapColorFunc(
            colormap=wc_config.colormap, color_range=wc_config.color_range, color_step_range=wc_config.color_step_range
        )
        kwargs["color_func"] = color_func.color_func

        # Generate word cloud
        mask_path = wc_config.mask_path if wc_config.use_mask else None
        wc = word_cloud.create_wordcloud(word_freq, mask_path=mask_path, **kwargs)

        result = {"wordcloud_object": wc}

        # Save to files if directory specified
        if self.config.save_directory:
            save_dir = Path(self.config.save_directory)
            save_dir.mkdir(parents=True, exist_ok=True)

            for fmt in self.config.output_formats:
                if fmt == "svg":
                    svg_path = save_dir / f"{output_basename}.svg"
                    svg_content = word_cloud.word_cloud_to_svg(wc)
                    svg_path.write_text(svg_content, encoding="utf-8", newline="\n")
                    result["svg_path"] = str(svg_path)
                elif fmt in ["png", "jpg", "jpeg"]:
                    img_path = save_dir / f"{output_basename}.{fmt}"
                    img = wc.to_image()
                    # Convert RGBA to RGB for JPEG
                    if fmt in ["jpg", "jpeg"] and img.mode == "RGBA":
                        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[3])
                        rgb_img.save(str(img_path))
                    else:
                        img.save(str(img_path))
                    result[f"{fmt}_path"] = str(img_path)

        return result
