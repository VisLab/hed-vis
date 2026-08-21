"""Tests for HedTagVisualizer."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from hed.models import HedString, Sidecar, TabularInput
from hed.schema import load_schema_version
from hed.tools.analysis.hed_tag_counts import HedTagCounts

from hedvis import HedTagVisualizer, VisualizationConfig, WordCloudConfig


class TestHedTagVisualizerInit(unittest.TestCase):
    """Tests for HedTagVisualizer initialization."""

    def test_init_default(self):
        """Test initialization with default config."""
        visualizer = HedTagVisualizer()
        self.assertIsInstance(visualizer.config, VisualizationConfig)
        self.assertEqual(visualizer.config.output_formats, ["svg"])

    def test_init_with_config_object(self):
        """Test initialization with VisualizationConfig object."""
        config = VisualizationConfig(output_formats=["png"], save_directory="/tmp")
        visualizer = HedTagVisualizer(config)
        self.assertEqual(visualizer.config.output_formats, ["png"])
        self.assertEqual(visualizer.config.save_directory, "/tmp")

    def test_init_with_dict(self):
        """Test initialization with dictionary."""
        config_dict = {
            "output_formats": ["svg", "png"],
            "save_directory": "./output",
            "word_cloud": {"width": 1200, "height": 800},
        }
        visualizer = HedTagVisualizer(config_dict)
        self.assertEqual(visualizer.config.output_formats, ["svg", "png"])
        self.assertEqual(visualizer.config.save_directory, "./output")
        self.assertEqual(visualizer.config.word_cloud.width, 1200)


class TestHedTagVisualizerWordFrequencies(unittest.TestCase):
    """Tests for word frequency extraction."""

    def setUp(self):
        """Set up test fixtures."""
        # Create real HedTagCounts with actual data
        data_path = os.path.join(os.path.dirname(__file__), "data", "sub-002_task-FacePerception_run-1_events.tsv")
        json_path = os.path.join(os.path.dirname(__file__), "data", "task-FacePerception_events.json")

        schema = load_schema_version("8.1.0")
        sidecar = Sidecar(json_path)
        input_data = TabularInput(data_path, sidecar=sidecar)

        self.tag_counts = HedTagCounts(input_data.name, len(input_data.dataframe))

        # Process some events to populate tag_counts
        for hed_string in input_data.series_a[:20]:  # Use first 20 events for speed
            if hed_string:
                self.tag_counts.update_tag_counts(HedString(hed_string, schema), input_data.name)

    def test_extract_word_frequencies_no_template(self):
        """Test extracting word frequencies without template."""
        visualizer = HedTagVisualizer()
        word_freq = visualizer._extract_word_frequencies(self.tag_counts)

        # Should have some tags from the real data
        self.assertGreater(len(word_freq), 0)
        # All values should be positive integers
        for _tag, count in word_freq.items():
            self.assertIsInstance(count, int)
            self.assertGreater(count, 0)

    def test_extract_word_frequencies_with_template(self):
        """Test extracting word frequencies with template."""
        visualizer = HedTagVisualizer()

        # Use a template that matches common HED tags
        template = {"Sensory": ["Visual-presentation", "Auditory-presentation"], "Task": ["Experimental-trial", "Task"]}
        word_freq = visualizer._extract_word_frequencies(self.tag_counts, template)

        # Should have extracted frequencies using the template
        self.assertGreaterEqual(len(word_freq), 0)
        # All values should be positive integers
        for _tag, count in word_freq.items():
            self.assertIsInstance(count, int)
            self.assertGreater(count, 0)

    def test_extract_word_frequencies_with_unmatched(self):
        """Test that unmatched tags are included."""
        visualizer = HedTagVisualizer()

        # Use a template with a narrow match - most tags will be unmatched
        template = {"Sensory": ["Visual-presentation"]}
        word_freq = visualizer._extract_word_frequencies(self.tag_counts, template)

        # Should have some frequencies (matched or unmatched)
        self.assertGreater(len(word_freq), 0)
        for _tag, count in word_freq.items():
            self.assertIsInstance(count, int)
            self.assertGreater(count, 0)


class TestHedTagVisualizerGenerateWordCloud(unittest.TestCase):
    """Tests for word cloud generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.word_freq = {"Visual": 50, "Auditory": 30, "Action": 20}

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_generate_word_cloud_no_save(self):
        """Test generating word cloud without saving."""
        config = VisualizationConfig(word_cloud=WordCloudConfig(width=400, height=300))
        visualizer = HedTagVisualizer(config)

        result = visualizer._generate_word_cloud(self.word_freq, "test")

        self.assertIn("wordcloud_object", result)
        self.assertIsNotNone(result["wordcloud_object"])
        # Should not have file paths
        self.assertNotIn("svg_path", result)
        self.assertNotIn("png_path", result)

    def test_generate_word_cloud_save_svg(self):
        """Test generating and saving word cloud as SVG."""
        config = VisualizationConfig(
            output_formats=["svg"], save_directory=self.temp_dir, word_cloud=WordCloudConfig(width=400, height=300)
        )
        visualizer = HedTagVisualizer(config)

        result = visualizer._generate_word_cloud(self.word_freq, "test_output")

        self.assertIn("wordcloud_object", result)
        self.assertIn("svg_path", result)

        # Check that file was created
        svg_path = Path(result["svg_path"])
        self.assertTrue(svg_path.exists())
        self.assertEqual(svg_path.name, "test_output.svg")

        # Check that it contains SVG content
        content = svg_path.read_text()
        self.assertIn("<svg", content)

    def test_generate_word_cloud_save_png(self):
        """Test generating and saving word cloud as PNG."""
        config = VisualizationConfig(
            output_formats=["png"], save_directory=self.temp_dir, word_cloud=WordCloudConfig(width=400, height=300)
        )
        visualizer = HedTagVisualizer(config)

        result = visualizer._generate_word_cloud(self.word_freq, "test_output")

        self.assertIn("wordcloud_object", result)
        self.assertIn("png_path", result)

        # Check that file was created
        png_path = Path(result["png_path"])
        self.assertTrue(png_path.exists())
        self.assertEqual(png_path.name, "test_output.png")

    def test_generate_word_cloud_save_multiple_formats(self):
        """Test generating and saving word cloud in multiple formats."""
        config = VisualizationConfig(
            output_formats=["svg", "png", "jpg"],
            save_directory=self.temp_dir,
            word_cloud=WordCloudConfig(width=400, height=300),
        )
        visualizer = HedTagVisualizer(config)

        result = visualizer._generate_word_cloud(self.word_freq, "test_output")

        self.assertIn("svg_path", result)
        self.assertIn("png_path", result)
        self.assertIn("jpg_path", result)

        # Check that all files were created
        self.assertTrue(Path(result["svg_path"]).exists())
        self.assertTrue(Path(result["png_path"]).exists())
        self.assertTrue(Path(result["jpg_path"]).exists())

    def test_generate_word_cloud_creates_directory(self):
        """Test that save directory is created if it doesn't exist."""
        save_dir = Path(self.temp_dir) / "subdir" / "output"
        config = VisualizationConfig(
            output_formats=["svg"], save_directory=str(save_dir), word_cloud=WordCloudConfig(width=400, height=300)
        )
        visualizer = HedTagVisualizer(config)

        result = visualizer._generate_word_cloud(self.word_freq, "test")

        # Check that directory was created
        self.assertTrue(save_dir.exists())
        self.assertTrue(Path(result["svg_path"]).exists())


class TestHedTagVisualizerVisualizeFromCounts(unittest.TestCase):
    """Tests for visualize_from_counts method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Create real HedTagCounts with actual data
        data_path = os.path.join(os.path.dirname(__file__), "data", "sub-002_task-FacePerception_run-1_events.tsv")
        json_path = os.path.join(os.path.dirname(__file__), "data", "task-FacePerception_events.json")

        schema = load_schema_version("8.1.0")
        sidecar = Sidecar(json_path)
        input_data = TabularInput(data_path, sidecar=sidecar)

        self.tag_counts = HedTagCounts(input_data.name, len(input_data.dataframe))

        # Process some events to populate tag_counts
        for hed_string in input_data.series_a[:20]:  # Use first 20 events for speed
            if hed_string:
                self.tag_counts.update_tag_counts(HedString(hed_string, schema), input_data.name)

    def test_visualize_from_counts_no_word_cloud(self):
        """Test visualization with no word cloud config."""
        config = VisualizationConfig()  # No word_cloud config
        visualizer = HedTagVisualizer(config)

        results = visualizer.visualize_from_counts(self.tag_counts)

        self.assertEqual(len(results), 0)  # No visualizations generated

    def test_visualize_from_counts_with_word_cloud(self):
        """Test visualization with word cloud config."""
        config = VisualizationConfig(
            word_cloud=WordCloudConfig(width=400, height=300), save_directory=self.temp_dir, output_formats=["svg"]
        )
        visualizer = HedTagVisualizer(config)

        results = visualizer.visualize_from_counts(self.tag_counts, output_basename="test_viz")

        self.assertIn("word_cloud", results)
        self.assertIn("wordcloud_object", results["word_cloud"])
        self.assertIn("svg_path", results["word_cloud"])

    def test_visualize_from_counts_with_template(self):
        """Test visualization with tag template."""
        config = VisualizationConfig(word_cloud=WordCloudConfig(width=400, height=300))
        visualizer = HedTagVisualizer(config)

        template = {"Sensory": ["Visual-presentation", "Auditory-presentation"], "Task": ["Experimental-trial", "Task"]}
        results = visualizer.visualize_from_counts(self.tag_counts, tag_template=template)

        self.assertIn("word_cloud", results)


class TestHedTagVisualizerComputeTagCounts(unittest.TestCase):
    """Tests for _compute_tag_counts method."""

    def test_compute_tag_counts(self):
        """Test computing tag counts from tabular input."""
        # Load real data
        data_path = os.path.join(os.path.dirname(__file__), "data", "sub-002_task-FacePerception_run-1_events.tsv")
        json_path = os.path.join(os.path.dirname(__file__), "data", "task-FacePerception_events.json")

        schema = load_schema_version("8.1.0")
        sidecar = Sidecar(json_path)
        tabular_input = TabularInput(data_path, sidecar=sidecar)

        # Create visualizer
        visualizer = HedTagVisualizer()

        # Compute tag counts
        tag_counts = visualizer._compute_tag_counts(
            tabular_input, schema, include_context=False, replace_defs=False, remove_types=["Condition-variable"]
        )

        # Verify results
        self.assertIsInstance(tag_counts, HedTagCounts)
        self.assertEqual(tag_counts.name, tabular_input.name)
        self.assertEqual(tag_counts.total_events, len(tabular_input.dataframe))
        self.assertGreater(len(tag_counts.tag_dict), 0)  # Should have extracted some tags


if __name__ == "__main__":
    unittest.main()
