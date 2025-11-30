"""
```sidif
# 🌐🕸
base_sem3test isA PythonModule
  "Wolfgang Fahl" is author of it
  "2025-11-30" is createdAt of it
  "Base Test class for semantify³ tests" is purpose of it
```
"""

import os

from basemkit.basetest import Basetest

from sem3.extractor import Extractor


class BaseSem3test(Basetest):
    """Base Test class for semantify³ tests"""

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.script_path = os.path.abspath(__file__)
        self.project_root = os.path.dirname(os.path.dirname(self.script_path))

    def get_markups(self, path_glob: str = "**", file_glob="*.py"):
        # recursive=True in glob() requires the "**" pattern to actually traverse directories
        glob_patterns = [
            os.path.join(self.project_root, path_glob, file_glob),
        ]
        self.extractor = Extractor(debug=self.debug)
        markups = self.extractor.extract_from_glob_list(glob_patterns)
        if self.debug:
            self.extractor.print_markups(markups, limit=7)
        return markups
