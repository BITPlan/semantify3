"""
```sidif
# 🌐🕸
test_extractor isA PythonModule
  "Wolfgang Fahl" is author of it
  "2025-11-29" is createdAt of it
  "Test main micro annotation snippet extraction" is purpose of it
```
"""

import os

from basemkit.basetest import Basetest

from sem3.extractor import Extractor


class Test_Extractor(Basetest):
    """Test the extractor."""

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.script_path = os.path.abspath(__file__)
        self.project_root = os.path.dirname(os.path.dirname(self.script_path))

    def test_extract_from_own_source(self):
        """Test that the extractor can find annotations in the project's own
        source code."""
        # recursive=True in glob() requires the "**" pattern to actually traverse directories
        glob_patterns = [
            os.path.join(self.project_root, "**", "*.py"),
        ]

        extractor = Extractor(debug=self.debug)
        markups = extractor.extract_from_glob_list(glob_patterns)
        if self.debug:
            print(f"Found {len(markups)} markups")
            for i, markup in enumerate(markups):
                print(f"{i+1}: {markup.lang} in {os.path.basename(markup.source)}")
                print(markup.code)
                print("-" * 20)
        self.assertGreaterEqual(3, len(markups))
        for markup in markups:
            for field in ["isA", "author", "createdAt", "purpose"]:
                self.assertTrue(field in markup.code)
