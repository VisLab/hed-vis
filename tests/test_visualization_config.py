"""Tests for visualization configuration classes."""

import unittest

from hedvis.core.visualization_config import VisualizationConfig, WordCloudConfig


class TestWordCloudConfig(unittest.TestCase):
    """Tests for WordCloudConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = WordCloudConfig()
        self.assertEqual(config.width, 800)
        self.assertEqual(config.height, 600)
        self.assertIsNone(config.background_color)
        self.assertEqual(config.prefer_horizontal, 0.75)
        self.assertEqual(config.min_font_size, 8)
        self.assertIsNone(config.max_font_size)
        self.assertIsNone(config.font_path)
        self.assertEqual(config.colormap, "nipy_spectral")
        self.assertEqual(config.color_range, (0.0, 0.5))
        self.assertEqual(config.color_step_range, (0.15, 0.25))
        self.assertFalse(config.use_mask)
        self.assertIsNone(config.mask_path)
        self.assertEqual(config.contour_width, 3.0)
        self.assertEqual(config.contour_color, "black")
        self.assertEqual(config.scale_adjustment, 0.0)
        self.assertEqual(config.relative_scaling, 1.0)

    def test_custom_config(self):
        """Test custom configuration values."""
        config = WordCloudConfig(
            width=1200,
            height=800,
            background_color="white",
            prefer_horizontal=0.5,
            min_font_size=10,
            max_font_size=100,
            colormap="viridis",
            use_mask=True,
            mask_path="/path/to/mask.png",
        )
        self.assertEqual(config.width, 1200)
        self.assertEqual(config.height, 800)
        self.assertEqual(config.background_color, "white")
        self.assertEqual(config.prefer_horizontal, 0.5)
        self.assertEqual(config.min_font_size, 10)
        self.assertEqual(config.max_font_size, 100)
        self.assertEqual(config.colormap, "viridis")
        self.assertTrue(config.use_mask)
        self.assertEqual(config.mask_path, "/path/to/mask.png")

    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "width": 1024,
            "height": 768,
            "background_color": "black",
            "prefer_horizontal": 0.8,
            "min_font_size": 12,
            "colormap": "plasma",
            "extra_field": "should_be_ignored",  # Should not cause error
        }
        config = WordCloudConfig.from_dict(config_dict)
        self.assertEqual(config.width, 1024)
        self.assertEqual(config.height, 768)
        self.assertEqual(config.background_color, "black")
        self.assertEqual(config.prefer_horizontal, 0.8)
        self.assertEqual(config.min_font_size, 12)
        self.assertEqual(config.colormap, "plasma")
        # Extra field should not be in config
        self.assertFalse(hasattr(config, "extra_field"))

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = WordCloudConfig(width=1200, height=800, colormap="viridis")
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict["width"], 1200)
        self.assertEqual(config_dict["height"], 800)
        self.assertEqual(config_dict["colormap"], "viridis")
        # Should contain all public attributes
        self.assertIn("prefer_horizontal", config_dict)
        self.assertIn("min_font_size", config_dict)


class TestVisualizationConfig(unittest.TestCase):
    """Tests for VisualizationConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = VisualizationConfig()
        self.assertEqual(config.output_formats, ["svg"])
        self.assertIsNone(config.save_directory)
        self.assertIsNone(config.word_cloud)

    def test_custom_config(self):
        """Test custom configuration values."""
        wc_config = WordCloudConfig(width=1200, height=800)
        config = VisualizationConfig(output_formats=["svg", "png"], save_directory="./output", word_cloud=wc_config)
        self.assertEqual(config.output_formats, ["svg", "png"])
        self.assertEqual(config.save_directory, "./output")
        self.assertIsInstance(config.word_cloud, WordCloudConfig)
        self.assertEqual(config.word_cloud.width, 1200)

    def test_from_dict_simple(self):
        """Test creating config from simple dictionary."""
        config_dict = {"output_formats": ["png", "jpg"], "save_directory": "/tmp/output"}
        config = VisualizationConfig.from_dict(config_dict)
        self.assertEqual(config.output_formats, ["png", "jpg"])
        self.assertEqual(config.save_directory, "/tmp/output")
        self.assertIsNone(config.word_cloud)

    def test_from_dict_nested(self):
        """Test creating config from dictionary with nested word_cloud config."""
        config_dict = {
            "output_formats": ["svg"],
            "save_directory": "./viz",
            "word_cloud": {"width": 1024, "height": 768, "background_color": "white", "colormap": "viridis"},
        }
        config = VisualizationConfig.from_dict(config_dict)
        self.assertEqual(config.output_formats, ["svg"])
        self.assertEqual(config.save_directory, "./viz")
        self.assertIsInstance(config.word_cloud, WordCloudConfig)
        self.assertEqual(config.word_cloud.width, 1024)
        self.assertEqual(config.word_cloud.height, 768)
        self.assertEqual(config.word_cloud.background_color, "white")
        self.assertEqual(config.word_cloud.colormap, "viridis")

    def test_from_dict_with_wordcloud_object(self):
        """Test creating config from dictionary with WordCloudConfig object."""
        wc_config = WordCloudConfig(width=800, height=600)
        config_dict = {"output_formats": ["png"], "word_cloud": wc_config}
        config = VisualizationConfig.from_dict(config_dict)
        self.assertIsInstance(config.word_cloud, WordCloudConfig)
        self.assertEqual(config.word_cloud.width, 800)

    def test_to_dict(self):
        """Test converting config to dictionary."""
        wc_config = WordCloudConfig(width=1200, height=800)
        config = VisualizationConfig(output_formats=["svg", "png"], save_directory="./output", word_cloud=wc_config)
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict["output_formats"], ["svg", "png"])
        self.assertEqual(config_dict["save_directory"], "./output")
        self.assertIsInstance(config_dict["word_cloud"], dict)
        self.assertEqual(config_dict["word_cloud"]["width"], 1200)
        self.assertEqual(config_dict["word_cloud"]["height"], 800)

    def test_roundtrip_conversion(self):
        """Test that to_dict -> from_dict preserves configuration."""
        original = VisualizationConfig(
            output_formats=["svg", "png", "jpg"],
            save_directory="/tmp/test",
            word_cloud=WordCloudConfig(
                width=1024,
                height=768,
                background_color="black",
                prefer_horizontal=0.9,
                use_mask=True,
                mask_path="/path/to/mask.png",
            ),
        )

        # Convert to dict and back
        config_dict = original.to_dict()
        restored = VisualizationConfig.from_dict(config_dict)

        # Check that values match
        self.assertEqual(restored.output_formats, original.output_formats)
        self.assertEqual(restored.save_directory, original.save_directory)
        self.assertEqual(restored.word_cloud.width, original.word_cloud.width)
        self.assertEqual(restored.word_cloud.height, original.word_cloud.height)
        self.assertEqual(restored.word_cloud.background_color, original.word_cloud.background_color)
        self.assertEqual(restored.word_cloud.prefer_horizontal, original.word_cloud.prefer_horizontal)
        self.assertEqual(restored.word_cloud.use_mask, original.word_cloud.use_mask)
        self.assertEqual(restored.word_cloud.mask_path, original.word_cloud.mask_path)


if __name__ == "__main__":
    unittest.main()
