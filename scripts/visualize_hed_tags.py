#!/usr/bin/env python3
"""
Command-line script for visualizing HED tags from tabular event files.

This script processes TSV files with HED annotations, counts tag frequencies,
and generates visualizations (word clouds) and summaries. It works with files
that have HED annotations either inline or via JSON sidecars.

Logging Options:
- Default: WARNING level logs go to stderr (quiet unless there are issues)
- --verbose or --log-level INFO: Show informational messages about progress
- --log-level DEBUG: Show detailed debugging information
- --log-file FILE: Save logs to a file instead of/in addition to stderr
- --log-quiet: When using --log-file, suppress stderr output (file only)

Examples:
    # Process event files with default HED schema
    visualize_hed_tags /path/to/data --output-dir ./output

    # Process with specific schema version
    visualize_hed_tags /path/to/data --schema 8.3.0 --output-dir ./output

    # Process all TSV files with word cloud customization
    visualize_hed_tags /path/to/data --suffix '*' --width 1200 --height 800

    # Save tag counts JSON without generating word cloud
    visualize_hed_tags /path/to/data --no-word-cloud --save-counts --output-file tags.json

    # Process with JSON sidecar pattern and exclude directories
    visualize_hed_tags /path/to/data --sidecar-pattern '*_events.json' --exclude-dirs derivatives

    # Filter to specific files and use custom mask
    visualize_hed_tags /path/to/data --filter 'sub-01' --mask brain_mask.png

    # Include context and replace definitions
    visualize_hed_tags /path/to/data --include-context --replace-defs

    # Organize tags by template
    visualize_hed_tags /path/to/data --tag-template template.json --output-dir ./output
"""

import argparse
import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional

from hed import _version as vr
from hed.schema import load_schema_version
from hed.models import TabularInput
from hed.tools.util.io_util import get_file_list
from hed.tools.analysis.hed_tag_counts import HedTagCounts
from hed.tools.analysis.event_manager import EventManager
from hed.tools.analysis.hed_tag_manager import HedTagManager

from hedvis.core.tag_visualizer import HedTagVisualizer
from hedvis.core.visualization_config import VisualizationConfig, WordCloudConfig


def get_parser():
    """Create the argument parser for visualize_hed_tags.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Visualize HED tags from a collection of tabular event files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Required arguments
    parser.add_argument("data_path", help="Full path of root directory containing TSV files to process.")

    # File selection arguments
    parser.add_argument(
        "-p",
        "--prefix",
        dest="name_prefix",
        default=None,
        help="Optional prefix for base filename (e.g., 'sub-' to match 'sub-01_events.tsv').",
    )
    parser.add_argument(
        "-s",
        "--suffix",
        dest="name_suffix",
        default="events",
        help="Suffix for base filename (e.g., 'events' to match files ending with '_events.tsv'). "
        "Use '*' to match all TSV files regardless of suffix. Default: events",
    )
    parser.add_argument(
        "-x",
        "--exclude-dirs",
        nargs="*",
        default=[],
        dest="exclude_dirs",
        help="Directory names to exclude from file search.",
    )
    parser.add_argument(
        "-fl",
        "--filter",
        dest="filename_filter",
        default=None,
        help="Optional string to filter filenames. Only files containing this string will be processed.",
    )
    parser.add_argument(
        "-sp",
        "--sidecar-pattern",
        dest="sidecar_pattern",
        default=None,
        help="Pattern to find JSON sidecar files (e.g., '*_events.json'). "
        "If not specified, looks for sidecar with same base name as TSV file.",
    )

    # HED schema arguments
    parser.add_argument(
        "--schema",
        dest="schema_version",
        default=None,
        help="HED schema version to use (e.g., '8.3.0'). If not specified, uses latest.",
    )

    # HED processing arguments
    parser.add_argument(
        "--include-context",
        action="store_true",
        default=True,
        help="Include contextual tags (tags that unfold over time) in counts. Default: True",
    )
    parser.add_argument(
        "--no-include-context",
        action="store_false",
        dest="include_context",
        help="Do not include contextual tags in counts.",
    )
    parser.add_argument(
        "--replace-defs",
        action="store_true",
        default=True,
        help="Replace Def tags with their definitions in counts. Default: True",
    )
    parser.add_argument(
        "--no-replace-defs", action="store_false", dest="replace_defs", help="Do not replace Def tags with definitions."
    )
    parser.add_argument(
        "--remove-types",
        nargs="*",
        default=None,
        help="List of type tags to exclude from counts (e.g., 'Condition-variable' 'Task').",
    )

    # Tag organization
    parser.add_argument(
        "-t",
        "--tag-template",
        dest="tag_template",
        default=None,
        help="JSON file with tag template for organizing output. "
        'Format: {"Category1": ["Tag1", "Tag2"], "Category2": ["Tag3"]}.',
    )

    # Output arguments
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default=None,
        help="Directory to save visualization output files. If not specified, saves to current directory.",
    )
    parser.add_argument(
        "-of",
        "--output-file",
        dest="output_file",
        default=None,
        help="Filename for tag counts JSON output. If not specified, uses 'hed_tag_counts.json'.",
    )
    parser.add_argument("--save-counts", action="store_true", help="Save tag counts to JSON file.")
    parser.add_argument(
        "--output-formats",
        nargs="*",
        default=["svg"],
        choices=["svg", "png", "jpg", "jpeg"],
        help="Output format(s) for word cloud. Default: svg",
    )

    # Word cloud arguments
    parser.add_argument("--no-word-cloud", action="store_true", help="Do not generate word cloud visualization.")
    parser.add_argument("-w", "--width", type=int, default=800, help="Width of word cloud in pixels. Default: 800")
    parser.add_argument("-ht", "--height", type=int, default=600, help="Height of word cloud in pixels. Default: 600")
    parser.add_argument(
        "--background-color",
        default=None,
        help="Background color for word cloud (e.g., 'white', 'black'). Default: transparent",
    )
    parser.add_argument(
        "--colormap", default="nipy_spectral", help="Matplotlib colormap name for word colors. Default: nipy_spectral"
    )
    parser.add_argument("--font-path", default=None, help="Path to custom TTF/OTF font file for word cloud.")
    parser.add_argument(
        "--mask", dest="mask_path", default=None, help="Path to mask image file (PNG/JPEG) to shape the word cloud."
    )
    parser.add_argument(
        "--contour-width", type=float, default=3.0, help="Width of contour line around masked region. Default: 3.0"
    )
    parser.add_argument("--contour-color", default="black", help="Color for contour line. Default: black")
    parser.add_argument("--min-font-size", type=int, default=8, help="Minimum font size in points. Default: 8")
    parser.add_argument(
        "--max-font-size",
        type=int,
        default=None,
        help="Maximum font size in points. If not specified, auto-calculated.",
    )

    # Logging arguments
    parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        help="Log level (case insensitive). Default: WARNING",
    )
    parser.add_argument(
        "-lf",
        "--log-file",
        dest="log_file",
        default=None,
        help="Full path to save log output to file. If not specified, logs go to stderr.",
    )
    parser.add_argument(
        "-lq",
        "--log-quiet",
        action="store_true",
        dest="log_quiet",
        help="If present, suppress log output to stderr (only applies if --log-file is used).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="If present, output informative messages as computation progresses (equivalent to --log-level INFO).",
    )

    return parser


def setup_logging(args):
    """Configure logging based on command line arguments.

    Parameters:
        args (argparse.Namespace): Parsed command line arguments.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Determine log level
    log_level = args.log_level.upper() if args.log_level else "WARNING"
    if args.verbose:
        log_level = "INFO"

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Clear any existing handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set the root logger level
    root_logger.setLevel(getattr(logging, log_level))

    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # File handler if log file specified
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file, mode="w")
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Console handler (stderr) unless explicitly quieted and file logging is used
    if not args.log_quiet or not args.log_file:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    logger = logging.getLogger("visualize_hed_tags")
    logger.info(f"Starting HED tag visualization with log level: {log_level}")
    if args.log_file:
        logger.info(f"Logging to file: {args.log_file}")

    return logger


def find_sidecar(tsv_path: Path, sidecar_pattern: Optional[str] = None) -> Optional[Path]:
    """Find JSON sidecar file for a TSV file.

    Parameters:
        tsv_path: Path to the TSV file.
        sidecar_pattern: Optional glob pattern for sidecar files.

    Returns:
        Path to sidecar file if found, None otherwise.
    """
    # Try same directory with same base name
    json_path = tsv_path.with_suffix(".json")
    if json_path.exists():
        return json_path

    # Try BIDS task-level sidecar (e.g., task-taskname_events.json)
    # Extract task name from filename like sub-001_task-Name_run-01_events.tsv
    filename = tsv_path.stem
    if "task-" in filename:
        # Extract the task part
        parts = filename.split("_")
        task_part = None
        for part in parts:
            if part.startswith("task-"):
                task_part = part
                break

        if task_part:
            # Try task-level sidecar: task-Name_events.json
            task_sidecar = tsv_path.parent / f"{task_part}_events.json"
            if task_sidecar.exists():
                return task_sidecar

    # Try with pattern if specified
    if sidecar_pattern:
        parent = tsv_path.parent
        matches = list(parent.glob(sidecar_pattern))
        if matches:
            return matches[0]

    return None


def load_tag_template(template_path: str) -> Optional[Dict[str, List[str]]]:
    """Load tag template from JSON file.

    Parameters:
        template_path: Path to JSON file with tag template.

    Returns:
        Dictionary with tag template or None if loading fails.
    """
    try:
        with open(template_path, "r") as f:
            template = json.load(f)
        return template
    except Exception as e:
        logging.getLogger("visualize_hed_tags").error(f"Failed to load tag template: {e}")
        return None


def merge_tag_counts(all_counts: List[HedTagCounts]) -> HedTagCounts:
    """Merge multiple HedTagCounts into a single combined count.

    Parameters:
        all_counts: List of HedTagCounts objects to merge.

    Returns:
        HedTagCounts: Combined tag counts.
    """
    merged = HedTagCounts("Combined Dataset")
    for counts in all_counts:
        # Use built-in merge method
        merged.merge_tag_dicts(counts.tag_dict)
        merged.total_events += counts.total_events
        merged.files.update(counts.files)

    return merged


def process_files(args, logger):
    """Process files and generate visualizations.

    Parameters:
        args (argparse.Namespace): Parsed command line arguments.
        logger (logging.Logger): Logger instance.

    Returns:
        tuple: (merged_tag_counts, visualization_results) or (None, None) on failure.
    """
    logger.info(f"Data directory: {args.data_path}")
    logger.info(f"HED tools version: {str(vr.get_versions())}")

    # Load HED schema
    logger.info("Loading HED schema...")
    try:
        if args.schema_version:
            schema = load_schema_version(args.schema_version)
            logger.info(f"Loaded HED schema version: {args.schema_version}")
        else:
            # Load latest stable version (8.3.0 is current stable as of documentation)
            schema = load_schema_version("8.3.0")
            logger.info("Loaded HED schema version 8.3.0 (default)")
    except Exception as e:
        logger.error(f"Failed to load HED schema: {e}")
        return None, None

    # Handle wildcard suffix
    suffix_filter = None if args.name_suffix == "*" else args.name_suffix

    # Get list of TSV files
    logger.info("Searching for TSV files matching criteria...")
    if args.name_suffix == "*":
        logger.info("Using wildcard (*) - will match all TSV files")

    try:
        file_list = get_file_list(
            root_path=args.data_path,
            name_prefix=args.name_prefix,
            name_suffix=suffix_filter,
            extensions=[".tsv"],
            exclude_dirs=args.exclude_dirs,
        )
    except Exception as e:
        logger.error(f"Error searching for files: {e}")
        return None, None

    # Apply filename filter
    if args.filename_filter:
        original_count = len(file_list)
        file_list = [f for f in file_list if args.filename_filter in str(f)]
        logger.info(f"Applied filename filter '{args.filename_filter}': {original_count} -> {len(file_list)} files")

    if not file_list:
        logger.error("No TSV files found matching the specified criteria.")
        logger.error(f"  Path: {args.data_path}")
        logger.error(f"  Prefix: {args.name_prefix}")
        logger.error(f"  Suffix: {args.name_suffix}")
        logger.error(f"  Filter: {args.filename_filter}")
        return None, None

    logger.info(f"Found {len(file_list)} files to process")
    if logger.isEnabledFor(logging.DEBUG):
        for f in file_list:
            logger.debug(f"  {f}")

    # Process each file
    logger.info("Processing files and counting HED tags...")
    all_tag_counts = []
    successful_files = 0
    failed_files = 0

    for tsv_path in file_list:
        try:
            logger.debug(f"Processing: {tsv_path}")

            # Find sidecar
            sidecar_path = find_sidecar(Path(tsv_path), args.sidecar_pattern)
            if sidecar_path:
                logger.debug(f"  Found sidecar: {sidecar_path}")
                # Pass the path, not the loaded dictionary
                sidecar = str(sidecar_path)
            else:
                logger.debug("  No sidecar found")
                sidecar = None

            # Create TabularInput
            tabular = TabularInput(tsv_path, sidecar=sidecar, name=str(tsv_path))

            # Compute tag counts
            tag_counts = HedTagCounts(str(tsv_path), total_events=len(tabular.dataframe))
            tag_man = HedTagManager(EventManager(tabular, schema), remove_types=args.remove_types or [])
            hed_objs = tag_man.get_hed_objs(include_context=args.include_context, replace_defs=args.replace_defs)
            for hed in hed_objs:
                tag_counts.update_tag_counts(hed, str(tsv_path))

            all_tag_counts.append(tag_counts)
            successful_files += 1
            logger.debug(
                f"  Successfully processed: {len(tabular.dataframe)} events, {len(tag_counts.tag_dict)} unique tags"
            )

        except Exception as e:
            logger.error(f"Failed to process {tsv_path}: {e}")
            failed_files += 1
            continue

    # Log final statistics
    logger.info("Processing complete:")
    logger.info(f"  Successfully processed: {successful_files} files")
    if failed_files > 0:
        logger.warning(f"  Failed to process: {failed_files} files")

    if successful_files == 0:
        logger.error("No files were successfully processed.")
        return None, None

    # Merge all tag counts
    logger.info("Merging tag counts from all files...")
    merged_counts = merge_tag_counts(all_tag_counts)
    logger.info(f"  Total events: {merged_counts.total_events}")
    logger.info(f"  Unique tags: {len(merged_counts.tag_dict)}")
    logger.info(f"  Files processed: {len(merged_counts.files)}")

    # Generate visualizations
    visualization_results = None
    if not args.no_word_cloud:
        logger.info("Generating visualizations...")

        # Load tag template if specified
        tag_template = None
        if args.tag_template:
            logger.info(f"Loading tag template from: {args.tag_template}")
            tag_template = load_tag_template(args.tag_template)
            if tag_template:
                logger.info(f"  Template has {len(tag_template)} categories")

        # Configure word cloud
        wc_config = WordCloudConfig(
            width=args.width,
            height=args.height,
            background_color=args.background_color,
            min_font_size=args.min_font_size,
            max_font_size=args.max_font_size,
            font_path=args.font_path,
            colormap=args.colormap,
            use_mask=args.mask_path is not None,
            mask_path=args.mask_path,
            contour_width=args.contour_width,
            contour_color=args.contour_color,
        )

        # Configure visualization
        viz_config = VisualizationConfig(
            output_formats=args.output_formats, save_directory=args.output_dir or ".", word_cloud=wc_config
        )

        # Create visualizer and generate
        try:
            visualizer = HedTagVisualizer(viz_config)
            visualization_results = visualizer.visualize_from_counts(
                merged_counts, tag_template=tag_template, output_basename="hed_tags"
            )

            logger.info("Visualization generation complete:")
            if "word_cloud" in visualization_results:
                wc_results = visualization_results["word_cloud"]
                for key, value in wc_results.items():
                    if key.endswith("_path"):
                        logger.info(f"  Saved {key.replace('_path', '')}: {value}")

        except Exception as e:
            logger.error(f"Failed to generate visualizations: {e}")
            visualization_results = None

    return merged_counts, visualization_results


def save_tag_counts(tag_counts: HedTagCounts, output_file: str, logger):
    """Save tag counts to JSON file.

    Parameters:
        tag_counts: HedTagCounts object to save.
        output_file: Path to output JSON file.
        logger: Logger instance.
    """
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create output dictionary
        output_dict = {
            "name": tag_counts.name,
            "total_events": tag_counts.total_events,
            "total_files": len(tag_counts.files),
            "files": list(tag_counts.files.keys()),
            "tags": {},
        }

        # Convert tag_dict to serializable format - values are HedTagCount objects
        for _tag_key, tag_count in tag_counts.tag_dict.items():
            output_dict["tags"][tag_count.tag] = {"events": tag_count.events, "files": list(tag_count.files.keys())}

        # Write to file
        with open(output_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(output_dict, f, indent=2)

        logger.info(f"Saved tag counts to: {output_file}")

    except Exception as e:
        logger.error(f"Failed to save tag counts: {e}")


def main(arg_list=None):
    """Main entry point for the script.

    Parameters:
        arg_list (list, None): Optional list of command line arguments for testing.
                              If None, uses sys.argv.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    # Parse arguments
    parser = get_parser()
    args = parser.parse_args(arg_list)

    # Setup logging
    logger = setup_logging(args)

    try:
        # Process files
        merged_counts, visualization_results = process_files(args, logger)

        if merged_counts is None:
            logger.error("Processing failed.")
            return 1

        # Save tag counts if requested
        if args.save_counts:
            output_file = args.output_file or "hed_tag_counts.json"
            if args.output_dir:
                output_file = str(Path(args.output_dir) / output_file)
            save_tag_counts(merged_counts, output_file, logger)

        logger.info("All operations completed successfully.")
        return 0

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
