import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tools.cpp.cpp import CppProcessor


class TestCppProcessor(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.tmp_dir.name)
        self.config = {"compile": {"option1": "value1", "option2": "value2"}}
        self.query_backend = Mock()
        self.diff_target = Mock()
        self.verbose = True

    def test_process_with_makefile(self):
        processor = CppProcessor(
            self.query_backend, self.diff_target, self.base_path, self.base_path, self.config, self.verbose
        )
        makefile = self.base_path / "Makefile"
        with open(makefile, "w") as f:
            f.write("help:\n\techo help\n")
            f.close()

        with patch("builtins.print") as mock_print:
            processor.process()
            mock_print.assert_called_with("0 targets found")

    def test_process_with_cmakelists(self):
        processor = CppProcessor(
            self.query_backend, self.diff_target, self.base_path, self.base_path, self.config, self.verbose
        )
        cmakelists = self.base_path / "CMakeLists.txt"
        with open(cmakelists, "w") as f:
            f.write("cmake_minimum_required(VERSION 3.4)\nproject(test)\n")
            f.close()

        with patch("builtins.print") as mock_print:
            processor.process()
            mock_print.assert_called_with("0 targets found")

    def test_process_without_make_nor_cmake(self):
        processor = CppProcessor(
            self.query_backend, self.diff_target, self.base_path, self.base_path, self.config, self.verbose
        )
        with patch("builtins.print") as mock_print:
            processor.process()
            mock_print.assert_called_with("C++ is enabled, but cannot `Makefile` nor 'CMakeLists.txt'")
