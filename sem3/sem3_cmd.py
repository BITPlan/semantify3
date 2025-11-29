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

import glob
import os
import sys
from argparse import ArgumentParser, Namespace

from basemkit.base_cmd import BaseCmd

from sem3.extractor import Extractor
from sem3.version import Version


class Semantify3Cmd(BaseCmd):
    """Command line interface for semantify³."""

    def __init__(self):
        """Initialize the semantify³ command."""
        super().__init__(version=Version, description=Version.description)

    def get_arg_parser(self) -> ArgumentParser:
        """Create and configure the argument parser."""
        parser = super().get_arg_parser()

        parser.add_argument("files", nargs="*", help="Input files or glob patterns")

        parser.add_argument(
            "-i",
            "--input",
            action="append",
            dest="input_patterns",
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
                "graphml",
                "graphson",
                "cypher",
            ],
            default="turtle",
            help="Output serialization format (default: turtle)",
        )
        return parser

    def expand_files(self, inputs: list) -> list:
        """
        Takes a list of input arguments (file paths or glob patterns),
        expands them, and returns a flat, unique list of file paths.
        """
        file_list = []
        for input_path in inputs:
            matches = glob.glob(input_path, recursive=True)
            file_list.extend(matches)

        return sorted(list(set(file_list)))

    def handle_args(self, args: Namespace) -> bool:
        """Handle parsed arguments."""
        handled = super().handle_args(args)
        if handled:
            return True

        # 1. Collect all input patterns from both -i and positional arguments
        raw_patterns = []
        if args.input_patterns:
            raw_patterns.extend(args.input_patterns)
        if args.files:
            raw_patterns.extend(args.files)

        if raw_patterns:
            # 2. Expand globs and deduplicate before passing to Extractor
            files = self.expand_files(raw_patterns)

            if not files and args.verbose:
                print("No files found matching the provided patterns.")
                return True

            extractor = Extractor(debug=self.debug)

            # Passing concrete files list to the extractor
            markups = extractor.extract_from_glob_list(files)

            if args.verbose:
                print(f"Found {len(markups)} markups")

            for i, markup in enumerate(markups, 1):
                print(f"{i}: {markup.lang} in {os.path.basename(markup.source)}")
                print(markup.code)
                print("-" * 20)

            return True

        return False


def main(argv=None) -> int:
    """Main entry point for semantify3 CLI."""
    cmd = Semantify3Cmd()
    return cmd.run(argv)


if __name__ == "__main__":
    sys.exit(main())
