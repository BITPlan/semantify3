"""Command-line interface for semantify³.

```yaml
# 🌐🕸
extractor:
  isA: PythonModule
  author: Wolfgang Fahl
  createdAt: 2025-11-29
  purpose: extraction of relevant markup snippets for semantify³.
```
"""

import glob
import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from basemkit.yamlable import lod_storable


@lod_storable
@dataclass
class Markup:
    """A single markup."""

    lang: str
    code: str
    source: str


class Extractor:
    """Extract semantic annotation markup from files."""

    def __init__(self, marker: str = "🌐🕸", debug: bool = False):
        """constructor."""
        self.marker = marker
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)

    def log(self, msg: str):
        if self.debug:
            self.logger.debug(msg)

    def extract_from_file(self, filepath: str) -> List[Markup]:
        """Extract markup snippets from a single file.

        Args:
            filepath: Path to the file to extract from.

        Returns:
            List[Markup]: List of extracted markup snippets.
        """
        markups = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            markups = self.extract_from_text(content, source_path=filepath)
        except (IOError, UnicodeDecodeError) as e:
            self.logger.warning(f"Error reading {filepath}: {e}")
            markups = []
        return markups

    def extract_from_text(
        self, text: str, source_path: Optional[str] = None
    ) -> List[Markup]:
        """Extract all semantic markup snippets from text in a single pass.

        Uses one regex to find blocks (even if commented/indented), then
        delegates logic to create_markup_from_block.

        Args:
            text: The source text to extract from.
            source_path: Optional file path for location tracking.

        Returns:
            List[Markup]: List of extracted markup snippets.
        """
        # Step 1: Quick check to avoid regex if marker isn't there
        if self.marker not in text:
            return []

        markups = []

        # Single Regex: Matches indentation/comments (prefix), language, and content.
        # Ensure the closing fence matches the opening prefix exactly.
        pattern = re.compile(
            r"(?P<prefix>^[ \t]*(?:#|//)?[ \t]*)```(?P<lang>yaml|sidif)\s*\n"
            r"(?P<content>.*?)"
            r"\n(?P=prefix)```",
            re.DOTALL | re.MULTILINE
        )

        for match in pattern.finditer(text):
            # Calculate line number based on the match start position
            line_num = text[: match.start()].count("\n") + 1

            # Extract raw groups
            prefix = match.group("prefix")
            lang = match.group("lang")
            content = match.group("content")

            # Delegate pure logic to testable method
            markup = self.create_markup_from_block(
                content, lang, prefix, line_num, source_path
            )

            if markup:
                markups.append(markup)

        if self.debug and len(markups) > 0:
            self.log(f"Found {len(markups)} snippets in {source_path}")

        return markups

    def create_markup_from_block(
        self,
        raw_content: str,
        lang: str,
        prefix: str,
        line_num: int,
        source_path: Optional[str]
    ) -> Optional[Markup]:
        """Process a raw block match into a Markup object.

        This method performs the cleaning (stripping prefixes), validation
        (checking for the marker), and object creation. It is purely logical
        and easy to test without regex matches.

        Args:
            raw_content: The content inside the fences (still potentially indented).
            lang: The language (yaml/sidif).
            prefix: The indentation/comment string found before the opening fence.
            line_num: The line number where the block started.
            source_path: The filename/path source.

        Returns:
            Optional[Markup]: The valid Markup object, or None if invalid/empty.
        """
        lines = raw_content.split("\n")
        cleaned_lines = []

        # 1. Clean the lines (Strip the prefix)
        for line in lines:
            if line.startswith(prefix):
                cleaned_lines.append(line[len(prefix):])
            elif line.startswith(prefix.rstrip()):
                # Handle lines that are just the prefix (or prefix w/o trailing space)
                cleaned_lines.append(line[len(prefix.rstrip()):])
            else:
                # If indentation doesn't match, keep line as is (or could be error)
                cleaned_lines.append(line)

        # 2. Locate the first actual content line
        first_content_idx = None
        for idx, line in enumerate(cleaned_lines):
            if line.strip():
                first_content_idx = idx
                break

        if first_content_idx is None:
            return None

        # 3. Validate Marker
        first_line = cleaned_lines[first_content_idx].strip()
        if self.marker not in first_line:
            return None

        # 4. Extract code content (everything after the marker line)
        code_lines = cleaned_lines[first_content_idx + 1 :]
        code = "\n".join(code_lines).strip()

        if not code:
            return None

        # 5. Build Source String
        source = ""
        if source_path:
            source = f"{source_path}:{line_num}"

        markup= Markup(lang=lang, code=code, source=source)
        return markup

    def extract_from_glob(self, pattern: str) -> List[Markup]:
        """Extract markup snippets from files matching a glob pattern.

        Args:
            pattern: Glob pattern to match files (supports **).

        Returns:
            List[Markup]: All markup snippets from matching files.
        """
        all_markups = []

        files = glob.glob(pattern, recursive=True)
        self.log(f"Glob pattern '{pattern}' found {len(files)} files")

        for filepath in files:
            markups = self.extract_from_file(filepath)
            all_markups.extend(markups)

        return all_markups

    def extract_from_glob_list(self, patterns: List[str]) -> List[Markup]:
        """Extract markup snippets from files matching multiple glob patterns.

        Args:
            patterns: List of glob patterns to match files.

        Returns:
            List[Markup]: All markup snippets from matching files.
        """
        all_markups = []

        self.log(f"Processing {len(patterns)} glob patterns")

        for pattern in patterns:
            self.log(f"Checking pattern: {pattern}")
            markups = self.extract_from_glob(pattern)
            all_markups.extend(markups)

        return all_markups
