"""Configuration classes for HED visualizations."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WordCloudConfig:
    """Configuration for word cloud visualizations.

    Attributes:
        width: Width of word cloud in pixels.
        height: Height of word cloud in pixels.
        background_color: Background color name or None for transparent.
        prefer_horizontal: Fraction of words oriented horizontally (0.0-1.0).
        min_font_size: Minimum font size in points.
        max_font_size: Maximum font size in points (auto-calculated if None).
        font_path: Path to TTF/OTF font file (None uses default).
        colormap: Matplotlib colormap name for word colors.
        color_range: Tuple of (min, max) values from colormap to use.
        color_step_range: Tuple of (min, max) step sizes through colormap.
        use_mask: Whether to use a mask image to shape the cloud.
        mask_path: Path to mask image file (PNG/JPEG).
        contour_width: Width of contour line around masked region.
        contour_color: Color name for contour line.
        scale_adjustment: Adjustment factor for log-transformed frequencies.
        relative_scaling: Scaling factor for word sizes (0.0-1.0).
    """

    # Dimensions
    width: int = 800
    height: int = 600

    # Appearance
    background_color: str | None = None  # None = transparent
    prefer_horizontal: float = 0.75
    min_font_size: int = 8
    max_font_size: int | None = None  # Auto-calculated if None

    # Font settings
    font_path: str | None = None

    # Color scheme
    colormap: str = "nipy_spectral"
    color_range: tuple = (0.0, 0.5)
    color_step_range: tuple = (0.15, 0.25)

    # Mask settings
    use_mask: bool = False
    mask_path: str | None = None
    contour_width: float = 3.0
    contour_color: str = "black"

    # Scaling
    scale_adjustment: float = 0.0  # For log-transform adjustments
    relative_scaling: float = 1.0

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "WordCloudConfig":
        """Create configuration from dictionary.

        Parameters:
            config_dict: Dictionary with configuration parameters.

        Returns:
            WordCloudConfig: Configuration object.
        """
        # Filter to only valid fields
        valid_fields = {k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            dict: Dictionary representation of configuration.
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


@dataclass
class VisualizationConfig:
    """Master configuration for all HED visualizations.

    Attributes:
        output_formats: List of output formats ('svg', 'png', 'jpg', etc.).
        save_directory: Directory path for saving visualizations (None = don't save).
        word_cloud: Configuration for word cloud visualization (None = don't generate).
    """

    # Output settings
    output_formats: list[str] = field(default_factory=lambda: ["svg"])
    save_directory: str | None = None

    # Visualization types to generate
    word_cloud: WordCloudConfig | None = None

    # Future visualization types can be added here:
    # timeline: Optional[TimelineConfig] = None
    # network: Optional[NetworkConfig] = None
    # heatmap: Optional[HeatmapConfig] = None

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "VisualizationConfig":
        """Create configuration from dictionary.

        Parameters:
            config_dict: Dictionary with configuration parameters.

        Returns:
            VisualizationConfig: Configuration object.

        Notes:
            Nested dictionaries are automatically converted to appropriate config objects.
        """
        config = config_dict.copy()

        # Handle nested word_cloud config
        if "word_cloud" in config and isinstance(config["word_cloud"], dict):
            config["word_cloud"] = WordCloudConfig.from_dict(config["word_cloud"])

        # Filter to only valid fields
        valid_fields = {k: v for k, v in config.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            dict: Dictionary representation of configuration.
        """
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            if hasattr(value, "to_dict"):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
