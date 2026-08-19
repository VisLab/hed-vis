"""Quick example demonstrating the new hedvis API."""

from hedvis import HedTagVisualizer, VisualizationConfig, WordCloudConfig, create_wordcloud, word_cloud_to_svg

# Example 1: Simple dictionary configuration
print("Example 1: Simple dictionary configuration")
config_dict = {"word_cloud": {"width": 400, "height": 300, "background_color": "white"}, "output_formats": ["svg"]}

visualizer = HedTagVisualizer(config_dict)
print(f"Visualizer created with config: {visualizer.config.word_cloud.width}x{visualizer.config.word_cloud.height}")

# Example 2: Using configuration classes
print("\nExample 2: Using configuration classes")
wc_config = WordCloudConfig(width=800, height=600, background_color="black", prefer_horizontal=0.9)

viz_config = VisualizationConfig(output_formats=["svg", "png"], save_directory="./test_output", word_cloud=wc_config)

visualizer2 = HedTagVisualizer(viz_config)
print(f"Visualizer created with {len(visualizer2.config.output_formats)} output formats")

# Example 3: Legacy API still works
print("\nExample 3: Legacy API compatibility")

word_dict = {"HED": 10, "Tags": 8, "Events": 6, "Schema": 5}
wc = create_wordcloud(word_dict, width=300, height=200)
print(f"Word cloud created with {len(word_dict)} words")
print(f"Word cloud dimensions: {wc.width}x{wc.height}")

svg = word_cloud_to_svg(wc)
print(f"SVG generated: {len(svg)} characters")

print("\n✅ All examples completed successfully!")
print("The new hedvis API is working correctly.")
