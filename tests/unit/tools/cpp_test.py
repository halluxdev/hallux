import tempfile
import unittest
from pathlib import Path
from shutil import which
from unittest.mock import Mock, patch

import pytest

from hallux.tools.cpp.cpp import Cpp_IssueSolver


class TestCpp_IssueSolver(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.tmp_dir.name)
        self.config = {"compile": {"option1": "value1", "option2": "value2"}}
        self.query_backend = Mock()
        self.diff_target = Mock()

    def test_process_with_makefile(self):
        processor = Cpp_IssueSolver(self.base_path, self.base_path)
        makefile = self.base_path / "Makefile"
        with open(makefile, "w") as f:
            f.write("help:\n\techo help\n")
            f.close()

        with patch("hallux.logger.logger.info") as mock_print:
            processor.solve_issues(self.query_backend, self.diff_target)
            mock_print.assert_called_with("0 Makefile targets found")

    @pytest.mark.skipif(not which("cmake") or not which("make"), reason="CMake and/or Make is not installed")
    def test_process_with_cmakelists(self):
        processor = Cpp_IssueSolver(self.base_path, self.base_path)
        cmakelists = self.base_path / "CMakeLists.txt"
        with open(cmakelists, "w") as f:
            f.write("cmake_minimum_required(VERSION 3.4)\nproject(test)\n")
            f.close()

        with patch("hallux.logger.logger.info") as mock_print:
            processor.solve_issues(self.query_backend, self.diff_target)
            mock_print.assert_called_with("0 Makefile targets found")

    def test_process_without_make_nor_cmake(self):
        processor = Cpp_IssueSolver(self.base_path, self.base_path)
        with patch("hallux.logger.logger.error") as mock_print:
            processor.solve_issues(self.query_backend, self.diff_target)
            mock_print.assert_called_with("Process C/C++: cannot find `Makefile` nor 'CMakeLists.txt'")
