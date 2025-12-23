#!/usr/bin/env python3
"""CLI entry point for Obsidian MOC Exporter."""

import argparse
import sys
import textwrap
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from moc_exporter.exporter import ObsidianMOCExporter


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog='obsidian-moc-exporter',
        description=textwrap.dedent('''\
            Export Obsidian notes from a MOC (Map of Content) to standard Markdown.

            This tool recursively traverses links from a specified MOC note and
            exports all referenced notes and attachments in a format suitable
            for importing into NotebookLM.
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--vault',
        type=Path,
        required=True,
        help='Path to the Obsidian vault root directory',
    )

    parser.add_argument(
        '--moc',
        type=str,
        required=True,
        help='Path to the MOC file, relative to vault root or just the filename',
    )

    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output directory path for exported files',
    )

    parser.add_argument(
        '--depth',
        type=int,
        default=2,
        help='Maximum link traversal depth (default: 2)',
    )

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """
    Validate parsed arguments.

    Args:
        args: Parsed arguments namespace

    Raises:
        ValueError: If arguments are invalid
    """
    if not args.vault.exists():
        raise ValueError(f"Vault directory does not exist: {args.vault}")

    if not args.vault.is_dir():
        raise ValueError(f"Vault path is not a directory: {args.vault}")

    if args.depth < 0:
        raise ValueError(f"Depth must be non-negative: {args.depth}")


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        args = parse_args()
        validate_args(args)

        exporter = ObsidianMOCExporter(
            vault_path=args.vault,
            output_path=args.output,
            max_depth=args.depth,
        )

        exporter.export(args.moc)
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nExport cancelled by user.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
