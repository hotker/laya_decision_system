"""
Tests for output utilities
===========================
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from utils.output import save_results, list_output_files, clean_old_files, clean_all


class TestSaveResults:
    """Test save_results function"""

    @patch("utils.output._gen_filename")
    def test_save_json_result(self, mock_gen):
        """Test saving JSON result"""
        mock_gen.return_value = "/tmp/test_output.json"

        results = [
            {"text": "test 1", "category": "positive"},
            {"text": "test 2", "category": "negative"},
        ]

        path = save_results(results, prefix="test", decision_type="classification")

        assert path == "/tmp/test_output.json"
        output_path = Path(path)
        if output_path.exists():
            with open(output_path) as f:
                data = json.load(f)
            assert "metadata" in data
            assert "results" in data
            assert len(data["results"]) == 2


class TestListOutputFiles:
    """Test list_output_files function"""

    def test_list_files(self):
        """Test listing output files"""
        files = list_output_files()
        assert isinstance(files, list)


class TestCleanAll:
    """Test clean_all function"""

    def test_clean_all(self):
        """Test cleaning all output files"""
        deleted = clean_all()
        assert isinstance(deleted, int)