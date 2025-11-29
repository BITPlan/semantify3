"""Tests for semantify³ command-line interface.

```yaml
# 🌐🕸
test_cmd:
  isA: PythonTestModule
  author: Wolfgang Fahl
  createdAt: 2025-11-29
  purpose: Unit tests for the semantify³ CLI.
```
Tests for semantify³ command-line interface."""

import io
import os
from contextlib import redirect_stdout

from basemkit.basetest import Basetest

from sem3.sem3_cmd import Semantify3Cmd, main
from sem3.version import Version


class TestCmd(Basetest):
    """Test semantify³ command-line interface."""

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.script_path = os.path.abspath(__file__)
        self.project_root = os.path.dirname(os.path.dirname(self.script_path))
        self.cmd = Semantify3Cmd()

    def capture_run(self, args):
        """
        Helper to run command and capture output.
        Handles SystemExit for --help and --version.
        """
        capture = io.StringIO()
        exit_code = -1
        try:
            with redirect_stdout(capture):
                exit_code = self.cmd.run(args)
        except SystemExit as e:
            exit_code = e.code
        text = capture.getvalue()
        if self.debug:
            print(f"{args}\nexit-code:{exit_code}\n{text}")
        return exit_code, text

    def test_version(self):
        """Test version output."""
        exit_code, output = self.capture_run(["--version"])

        self.assertEqual(exit_code, 0)
        # Based on log: semantify³ 0.0.1 2025-11-29
        self.assertIn("semantify³", output)
        self.assertIn(Version.version, output)

    def test_help(self):
        """Test help output."""
        exit_code, output = self.capture_run(["--help"])

        self.assertEqual(exit_code, 0)
        self.assertIn("usage:", output)
        # self.assertIn("semantify³", output)
        self.assertIn("--input", output)
        self.assertIn("--format", output)

    def test_extract_from_single_file(self):
        """Test extracting markups from a single file."""
        test_file = os.path.join(self.project_root, "sem3", "extractor.py")
        exit_code, output = self.capture_run([test_file])

        self.assertEqual(exit_code, 0)
        self.assertIn("yaml in extractor.py", output)
        self.assertIn("isA: PythonModule", output)
        self.assertIn("author: Wolfgang Fahl", output)

    def test_extract_with_glob_pattern(self):
        """Test extracting markups using -i with glob pattern."""
        pattern = os.path.join(self.project_root, "sem3", "*.py")
        exit_code, output = self.capture_run(["-i", pattern])

        self.assertEqual(exit_code, 0)
        self.assertIn("extractor:", output)
        self.assertIn("sem3_cmd:", output)

    def test_extract_with_multiple_patterns(self):
        """Test extracting markups with multiple -i options."""
        py_pattern = os.path.join(self.project_root, "sem3", "*.py")
        md_pattern = os.path.join(self.project_root, "*.md")

        exit_code, output = self.capture_run(["-i", py_pattern, "-i", md_pattern])

        self.assertEqual(exit_code, 0)
        self.assertIn("extractor:", output)
        self.assertIn("sem3_cmd:", output)

    def test_extract_with_verbose(self):
        """Test verbose output."""
        test_file = os.path.join(self.project_root, "sem3", "extractor.py")
        exit_code, output = self.capture_run(["--verbose", test_file])

        self.assertEqual(exit_code, 0)
        self.assertIn("Found 1 markups", output)
        self.assertIn("isA: PythonModule", output)

    def test_mixed_input_methods(self):
        """Test combining positional args and -i option."""
        file1 = os.path.join(self.project_root, "sem3", "extractor.py")
        file2 = os.path.join(self.project_root, "sem3", "version.py")

        exit_code, output = self.capture_run(["-i", file1, file2])

        self.assertEqual(exit_code, 0)
        self.assertIn("extractor:", output)

    def test_main_function(self):
        """Test the main() entry point directly."""
        test_file = os.path.join(self.project_root, "sem3", "extractor.py")

        # We manually capture here because main() instantiates its own Cmd class,
        # bypasses self.cmd, and we want to test that specific wiring.
        capture = io.StringIO()
        with redirect_stdout(capture):
            exit_code = main([test_file])

        self.assertEqual(exit_code, 0)
        output = capture.getvalue()
        self.assertIn("extractor:", output)
        self.assertIn("isA: PythonModule", output)

    def test_debug_mode(self):
        """Test debug mode."""
        test_file = os.path.join(self.project_root, "sem3", "extractor.py")
        exit_code, output = self.capture_run(["--debug", test_file])

        self.assertEqual(exit_code, 0)
        self.assertIn("extractor:", output)

    def test_format_options(self):
        """Test that format options are accepted."""
        test_file = os.path.join(self.project_root, "sem3", "extractor.py")
        for fmt in ["turtle", "n3", "json-ld", "sidif"]:
            exit_code, output = self.capture_run(["--format", fmt, test_file])
            self.assertEqual(exit_code, 0)
            self.assertIn("extractor", output)

    def test_extract_from_own_source(self):
        """Test that the extractor can find annotations in the project's own source code."""
        pattern = os.path.join(self.project_root, "**", "*.py")
        exit_code, output = self.capture_run(["-i", pattern])

        self.assertEqual(exit_code, 0)

        self.assertIn("test_cmd:", output)
        self.assertIn("test_extractor isA PythonModule", output)
        self.assertIn("extractor:", output)
        self.assertIn("sem3_cmd:", output)
