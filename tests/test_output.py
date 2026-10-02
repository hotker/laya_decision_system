"""
Tests for output utilities
===========================
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from utils.output import (
    clean_all,
    clean_old_files,
    list_output_files,
    save_results,
    save_results_csv,
    save_single_result,
)


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

    @patch("utils.output._gen_filename")
    def test_save_empty_results(self, mock_gen):
        """Test saving empty results list"""
        mock_gen.return_value = "/tmp/test_empty.json"

        path = save_results([], prefix="test")
        output_path = Path(path)
        if output_path.exists():
            with open(output_path) as f:
                data = json.load(f)
            assert len(data["results"]) == 0


class TestSaveSingleResult:
    """Test save_single_result function"""

    @patch("utils.output._gen_filename")
    def test_save_single_result(self, mock_gen):
        """Test saving a single result"""
        mock_gen.return_value = "/tmp/test_single.json"

        result = {"category": "positive", "confidence": 0.95}
        path = save_single_result(result, prefix="sentiment", decision_type="sentiment")

        output_path = Path(path)
        if output_path.exists():
            with open(output_path) as f:
                data = json.load(f)
            assert "metadata" in data
            assert "result" in data
            assert data["result"]["confidence"] == 0.95


class TestSaveResultsCSV:
    """Test save_results_csv function"""

    def test_save_csv(self, tmp_path):
        """Test saving results as CSV"""
        results = [
            {"metadata": {"a": 1}, "answers": {"b": 2}},
        ]
        with patch("utils.output.OUTPUT_DIR", tmp_path):
            path = save_results_csv(results, prefix="csv_test")
        csv_path = Path(path)
        assert csv_path.exists()
        assert csv_path.suffix == ".csv"

    def test_save_csv_empty(self, tmp_path):
        """Test saving empty results as CSV"""
        with patch("utils.output.OUTPUT_DIR", tmp_path):
            path = save_results_csv([])
        csv_path = Path(path)
        assert csv_path.exists()


class TestListOutputFiles:
    """Test list_output_files function"""

    def test_list_files(self):
        """Test listing output files"""
        files = list_output_files()
        assert isinstance(files, list)

    def test_list_files_sorted_by_mtime(self, tmp_path):
        """Test that files are sorted by modification time"""
        file1 = tmp_path / "batch_decision_test_000001.json"
        file2 = tmp_path / "batch_decision_test_000002.json"
        file1.touch()
        # Small delay so mtime differs
        import time

        time.sleep(0.01)
        file2.touch()

        with patch("utils.output.OUTPUT_DIR", tmp_path):
            files = list_output_files()
        assert len(files) == 2
        assert files[0] == file2


class TestCleanOldFiles:
    """Test clean_old_files function"""

    def test_clean_old_files(self, tmp_path):
        """Test cleaning old files while keeping latest"""
        # Create 5 test files
        for i in range(5):
            f = tmp_path / f"batch_decision_test_{i:02d}.json"
            f.touch()
            import time
            time.sleep(0.01)

        with patch("utils.output.OUTPUT_DIR", tmp_path):
            deleted = clean_old_files(keep_count=2)
        assert deleted == 3
        remaining = list(tmp_path.glob("batch_decision_test_*.json"))
        assert len(remaining) == 2


class TestCleanAll:
    """Test clean_all function"""

    def test_clean_all(self):
        """Test cleaning all output files"""
        deleted = clean_all()
        assert isinstance(deleted, int)

    def test_clean_all_all_patterns(self, tmp_path):
        """Test cleaning all JSON files"""
        for i in range(3):
            f = tmp_path / f"test_{i}.json"
            f.touch()
        with patch("utils.output.OUTPUT_DIR", tmp_path):
            deleted = clean_all("*.json")
        assert deleted == 3