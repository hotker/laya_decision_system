"""
Tests for data source utilities
================================
"""

from __future__ import annotations

import csv
import io
import json
import tempfile
from pathlib import Path

import pytest

from utils.data_source import load_data, save_output


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

    def test_json_file_single_dict(self):
        """Test loading a single JSON object"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"body": "solo text", "extra": "value"}, f)
            temp_path = f.name

        try:
            results = load_data(temp_path)
            assert len(results) == 1
            assert results[0]["body"] == "solo text"
            assert results[0]["extra"] == "value"
        finally:
            Path(temp_path).unlink()

    def test_json_file_nested_results_key(self):
        """Test loading JSON with 'results' wrapper"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"results": [{"body": "r1"}, {"body": "r2"}]}, f)
            temp_path = f.name

        try:
            results = load_data(temp_path)
            assert len(results) == 2
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

    def test_tsv_file(self):
        """Test loading from TSV file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False, newline="") as f:
            f.write("body\n")
            f.write("tsv 1\n")
            f.write("tsv 2\n")
            temp_path = f.name

        try:
            results = load_data(temp_path, text_column="body")
            assert len(results) == 2
            assert results[0]["body"] == "tsv 1"
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


class TestSaveOutput:
    """Test save_output function"""

    def test_save_json(self):
        """Test saving output as JSON"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            save_output([{"a": 1}, {"a": 2}], temp_path, fmt="json")
            with open(temp_path) as f:
                data = json.load(f)
            assert len(data) == 2
        finally:
            Path(temp_path).unlink()

    def test_save_csv(self):
        """Test saving output as CSV"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            temp_path = f.name

        try:
            save_output([{"a": 1, "b": 2}], temp_path, fmt="csv")
            with open(temp_path, encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                row = next(reader)
            assert row["a"] == "1"
            assert row["b"] == "2"
        finally:
            Path(temp_path).unlink()

    def test_save_csv_empty(self):
        """Test saving empty output as CSV"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            temp_path = f.name

        try:
            save_output([], temp_path, fmt="csv")
            with open(temp_path) as f:
                content = f.read()
            assert content == ""
        finally:
            Path(temp_path).unlink()

    def test_save_unsupported_format(self):
        """Test saving with unsupported format"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError):
                save_output([{}], temp_path, fmt="xml")
        finally:
            Path(temp_path).unlink()