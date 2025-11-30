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
import sys
from argparse import ArgumentParser, Namespace

from basemkit.base_cmd import BaseCmd

from sem3.extractor import Extractor
from sem3.version import Version
from sem3.lod2rdf import RDFDumper


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
            "--extract",
            action="store_true",
            help="only extract and display markup snippets",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=[
                "turtle",
                "n3",
                "ntriples",
                #"xml",
                "json-ld",
                #"sidif",
                #"graphml",
                #"graphson",
                #"cypher",
            ],
            default="turtle",
            help="Output serialization format (default: turtle)",
        )
        parser.add_argument(
            "--base-uri",
            type=str,
            default="https://semantify3.bitplan.com/source_code/",
            help="Base URI for RDF subjects (default: https://semantify3.bitplan.com/source_code/)",
        )
        parser.add_argument(
            "--namespace",
            type=str,
            default="python_module",
            help="Namespace prefix (default: python_module)",
        )
        parser.add_argument(
            "--type-name",
            type=str,
            default="PythonModule",
            help="RDF type/fallback class (default: PythonModule)",
        )
        parser.add_argument(
            "--id-field",
            type=str,
            default="name",
            help="Dict field for subject ID (default: name)",
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

    def serialize_lod(self, lod: list[dict], args) -> bool:
        """LOD → RDF Graph → serialize (file/stdout)."""
        dumper = RDFDumper(
            base_uri=args.base_uri,
            namespace_prefix=args.namespace,
            debug=self.debug  # Pass CLI debug
        )
        rdf_graph = dumper.as_rdf(lod, args.type_name, args.id_field)
        output_format = args.format
        if args.output:
            rdf_graph.serialize(destination=args.output, format=output_format)
            if self.debug:
                print(f"RDF saved to: {args.output}")
        else:
            serialized = rdf_graph.serialize(format=output_format)
            if isinstance(serialized, bytes):
                serialized = serialized.decode('utf-8')
            print(serialized)
        return True

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
            if args.extract:
                extractor.print_markups(markups, verbose=args.verbose)
            else:
                # get the list of dict representation of the markups
                lod = extractor.markups_to_lod(markups)
                if self.debug:
                    print(f"LOD: {len(lod)} items")
                self.serialize_lod(lod, args)
            return True

        return False


def main(argv=None) -> int:
    """Main entry point for semantify3 CLI."""
    cmd = Semantify3Cmd()
    return cmd.run(argv)


if __name__ == "__main__":
    sys.exit(main())
