"""Command-line interface for semantify³.

```yaml
🌐🕸
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
        """Extract all semantic markup snippets from text.

        Args:
            text: The source text to extract from.
            source_path: Optional file path for location tracking.

        Returns:
            List[Markup]: List of extracted markup snippets.
        """
        markups = []

        # Pattern to match code blocks with yaml or sidif
        pattern = re.compile(
            r"```(yaml|sidif)\s*\n"  # Opening fence with language
            r"(.*?)"  # Content (non-greedy)
            r"\n\s*```",  # Closing fence
            re.DOTALL,
        )

        for match in pattern.finditer(text):
            lang = match.group(1)
            raw_content = match.group(2)

            # Find first non-empty line
            lines = raw_content.split("\n")
            first_content_idx = None

            for idx, line in enumerate(lines):
                if line.strip():
                    first_content_idx = idx
                    break

            if first_content_idx is None:
                continue

            first_line = lines[first_content_idx].strip()

            # Check for marker
            if self.marker not in first_line:
                continue

            # Extract content after marker line
            content_lines = lines[first_content_idx + 1 :]
            code = "\n".join(content_lines).strip()

            if not code:
                continue

            # Calculate source line (1-based)
            line_num = text[: match.start()].count("\n") + 1

            source = ""
            if source_path:
                source = f"{source_path}:{line_num}"

            markup = Markup(lang=lang, code=code, source=source)
            markups.append(markup)

        if self.debug and len(markups) > 0:
            self.log(f"Found {len(markups)} snippets in {source_path}")

        return markups

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
