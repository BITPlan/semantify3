"""Command-line interface for semantify³.

```yaml
🌐🕸
sem3_cmd:
  isA: PythonModule
  author: Wolfgang Fahl
  createdAt: 2025-11-29
  purpose: Command-line interface for semantify³.
```
"""

from argparse import ArgumentParser, Namespace
import argparse
import os
import sys

from basemkit.base_cmd import BaseCmd
from sem3.extractor import Extractor
from sem3.version import Version


class Semantify3Cmd(BaseCmd):
    """Command line interface for semantify³."""

    def __init__(self):
        """Initialize the semantify³ command."""
        super().__init__(version=Version, description=Version.description)

    def get_arg_parser(self) -> ArgumentParser:
        """Create and configure the argument parser.

        Returns:
            ArgumentParser: The configured argument parser.
        """
        parser = super().get_arg_parser()

        parser.add_argument(
            'files',
            nargs='*',
            help="Input files or glob patterns"
        )

        parser.add_argument(
            "-i",
            "--input",
            action='append',
            dest='input_patterns',
            help="Input file glob pattern (can be specified multiple times)",
        )
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            help="Output file path for triples",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=[
                "turtle",
                "n3",
                "ntriples",
                "xml",
                "json-ld",
                "sidif",
                "graphml",  # Supported by Gremlin and Neo4j (via APOC)
                "graphson",  # Gremlin specific JSON
                "cypher",  # Neo4j Cypher CREATE statements
            ],
            default="turtle",
            help="Output serialization format (default: turtle)",
        )
        return parser

    def handle_args(self, args: Namespace) -> bool:
        """Handle parsed arguments.

        Args:
            args: Parsed argument namespace.

        Returns:
            bool: True if handled, False otherwise.
        """
        handled = super().handle_args(args)
        if handled:
            return True

        # Collect all input patterns from both -i and positional arguments
        patterns = []
        if args.input_patterns:
            patterns.extend(args.input_patterns)
        if args.files:
            patterns.extend(args.files)

        if patterns:
            extractor = Extractor(debug=self.debug)
            markups = extractor.extract_from_glob_list(patterns)

            if args.verbose:
                print(f"Found {len(markups)} markups")

            for i, markup in enumerate(markups, 1):
                print(f"{i}: {markup.lang} in {os.path.basename(markup.source)}")
                print(markup.code)
                print("-" * 20)

            return True

        return False


def main(argv=None) -> int:
    """Main entry point for semantify3 CLI.

    Args:
        argv: Command line arguments.

    Returns:
        int: Exit code.
    """
    cmd = Semantify3Cmd()
    return cmd.run(argv)


if __name__ == "__main__":
    sys.exit(main())
