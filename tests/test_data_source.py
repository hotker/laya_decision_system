"""
数据源测试
==========
"""

import json
from pathlib import Path

import pytest

from utils.data_source import load_data


class TestLoadData:
    """测试数据加载"""

    def test_none_returns_none(self, tmp_path):
        """source=None 返回 None"""
        assert load_data(None) is None

    def test_json_array(self, tmp_path):
        """JSON 数组加载"""
        data = [{"body": "评论1"}, {"body": "评论2"}]
        f = tmp_path / "data.json"
        f.write_text(json.dumps(data), encoding="utf-8")

        result = load_data(str(f), text_column="body")
        assert len(result) == 2
        assert result[0]["body"] == "评论1"

    def test_json_nested_results(self, tmp_path):
        """兼容输出格式 {"results": [...]}"""
        data = {"results": [{"body": "A"}, {"body": "B"}]}
        f = tmp_path / "output.json"
        f.write_text(json.dumps(data), encoding="utf-8")

        result = load_data(str(f), text_column="body")
        assert len(result) == 2
        assert result[0]["body"] == "A"

    def test_json_string_array(self, tmp_path):
        """纯字符串数组"""
        data = ["好", "坏", "一般"]
        f = tmp_path / "data.json"
        f.write_text(json.dumps(data), encoding="utf-8")

        result = load_data(str(f), text_column="body")
        assert len(result) == 3
        assert result[0]["body"] == "好"

    def test_json_dict_item(self, tmp_path):
        """字典中取 body 字段"""
        data = {"text": "hello", "extra": "value"}
        f = tmp_path / "data.json"
        f.write_text(json.dumps(data), encoding="utf-8")

        result = load_data(str(f), text_column="body")
        assert len(result) == 1
        assert result[0]["body"] == "hello"

    def test_csv_file(self, tmp_path):
        """CSV 加载"""
        f = tmp_path / "data.csv"
        f.write_text("body,extra\n好,A\n坏,B\n", encoding="utf-8")

        result = load_data(str(f), text_column="body")
        assert len(result) == 2
        assert result[0]["body"] == "好"
        assert result[0]["extra"] == "A"

    def test_file_not_found(self, tmp_path):
        """文件不存在"""
        with pytest.raises(FileNotFoundError):
            load_data(str(tmp_path / "nonexistent.json"))

    def test_unsupported_format(self, tmp_path):
        """不支持的格式"""
        f = tmp_path / "data.xml"
        f.write_text("<data/>")
        with pytest.raises(ValueError, match="不支持的数据格式"):
            load_data(str(f))