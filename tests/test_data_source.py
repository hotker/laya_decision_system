"""
Tests for data source utilities
================================
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from utils.data_source import load_data


class TestLoadData:
    """Test load_data function"""

    def test_none_source(self):
        """Test None source returns None"""
        result = load_data(None)
        assert result is None

    def test_json_file(self):
        """Test loading from JSON file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"body": "test 1"}, {"body": "test 2"}], f)
            temp_path = f.name

        try:
            results = load_data(temp_path)
            assert len(results) == 2
            assert results[0]["body"] == "test 1"
        finally:
            Path(temp_path).unlink()

    def test_json_file_string_array(self):
        """Test loading JSON array of strings"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(["test 1", "test 2"], f)
            temp_path = f.name

        try:
            results = load_data(temp_path)
            assert len(results) == 2
            assert results[0]["body"] == "test 1"
        finally:
            Path(temp_path).unlink()

    def test_csv_file(self):
        """Test loading from CSV file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            f.write("body\n")
            f.write("test 1\n")
            f.write("test 2\n")
            temp_path = f.name

        try:
            results = load_data(temp_path, text_column="body")
            assert len(results) == 2
            assert results[0]["body"] == "test 1"
        finally:
            Path(temp_path).unlink()

    def test_nonexistent_file(self):
        """Test loading non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent.json")

    def test_unsupported_format(self):
        """Test unsupported file format"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            with pytest.raises(ValueError):
                load_data(temp_path)
        finally:
            Path(temp_path).unlink()