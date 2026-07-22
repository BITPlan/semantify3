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
from sem3.homepage import ENGINE_GLOBS, ServiceHomepage
from sem3.lod2rdf import RDFDumper
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
            "--extract",
            action="store_true",
            help="only extract and display markup snippets",
        )
        parser.add_argument(
            "--homepage",
            action="store_true",
            help="render a service-overview homepage from annotated web-server configs",
        )
        parser.add_argument(
            "--engine",
            type=str,
            choices=sorted(ENGINE_GLOBS.keys()),
            default="apache",
            help="web-server engine whose default config glob is used when no input is given (default: apache)",
        )
        parser.add_argument(
            "--title",
            type=str,
            help="homepage title / heading (default: the engine name)",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=[
                "turtle",
                "n3",
                "ntriples",
                # "xml",
                "json-ld",
                # "sidif",
                # "graphml",
                # "graphson",
                # "cypher",
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
            debug=self.debug,  # Pass CLI debug
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
                serialized = serialized.decode("utf-8")
            print(serialized)
        return True

    def generate_homepage(self, args: Namespace, raw_patterns: list) -> bool:
        """
        Render the service-overview homepage from annotated web-server configs.

        Args:
            args: parsed command-line arguments
            raw_patterns: explicit input globs (-i / positional); when empty the
                engine's default config glob is used

        Returns:
            True (the homepage request was handled)
        """
        patterns = raw_patterns if raw_patterns else ENGINE_GLOBS.get(args.engine, [])
        title = args.title if args.title else args.engine
        homepage = ServiceHomepage(title=title, debug=self.debug)
        service_count = homepage.read_files(patterns)
        if self.debug:
            print(f"homepage: {service_count} services from {len(patterns)} pattern(s)")
        page = homepage.as_html()
        if args.output:
            with open(args.output, "w", encoding="utf-8") as html_file:
                html_file.write(page)
            if self.debug:
                print(f"homepage written to: {args.output}")
        else:
            print(page)
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

        if args.homepage:
            return self.generate_homepage(args, raw_patterns)

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
