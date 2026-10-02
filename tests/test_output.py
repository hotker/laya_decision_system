"""
输出工具测试
============
"""

import json
import os
from pathlib import Path

import pytest

from utils.output import (
    clean_all,
    clean_old_files,
    list_output_files,
    save_results,
    save_results_csv,
    save_single_result,
)


@pytest.fixture
def output_dir(tmp_path, monkeypatch):
    """使用临时目录作为输出目录"""
    monkeypatch.setenv("LAYA_OUTPUT_DIR", str(tmp_path))

    # 重置配置单例
    import config.config

    config.config._settings = None
    # 重新导入以生效
    importlib = __import__("importlib")
    import utils.output

    utils.output.OUTPUT_DIR = tmp_path
    utils.output._ensure_dir()
    return tmp_path


class TestSaveResults:
    """测试批量结果保存"""

    def test_save_and_read(self, output_dir):
        """保存并读取"""
        results = [
            {"review": "好产品", "category": "quality"},
            {"review": "太贵了", "category": "price"},
        ]
        path = save_results(results, prefix="test")

        assert Path(path).exists()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert "metadata" in data
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["category"] == "quality"
        assert data["metadata"]["count"] == 2
        assert data["metadata"]["system"] is not None

    def test_unique_filename(self, output_dir):
        """文件名唯一（UUID）"""
        save_results([{"a": 1}], prefix="unique")
        save_results([{"b": 2}], prefix="unique")

        files = list(output_dir.glob("batch_decision_unique_*.json"))
        assert len(files) == 2
        # 确认文件名不同
        names = [f.name for f in files]
        assert len(set(names)) == 2

    def test_decision_type_in_metadata(self, output_dir):
        """决策类型写入 metadata"""
        save_results([{"x": 1}], prefix="p", decision_type="custom")
        data = json.loads((list(output_dir.glob("batch_decision_p_*.json"))[0]).read_text())
        assert data["metadata"]["decision_type"] == "custom"


class TestSaveSingleResult:
    """测试单条结果保存"""

    def test_save_single(self, output_dir):
        """保存单条结果"""
        result = {"answers": {"category": {"choice": "A"}}}
        path = save_single_result(result, prefix="single", decision_type="classification")

        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert "metadata" in data
        assert "result" in data
        assert data["metadata"]["decision_type"] == "classification"


class TestSaveCSV:
    """测试 CSV 保存"""

    def test_save_csv(self, output_dir):
        """保存 CSV"""
        results = [
            {"name": "Alice", "score": 90},
            {"name": "Bob", "score": 80},
        ]
        path = save_results_csv(results, prefix="test")

        assert Path(path).exists()
        content = Path(path).read_text(encoding="utf-8-sig")
        assert "Alice" in content
        assert "score" in content


class TestListClean:
    """测试文件列表和清理"""

    def test_list_files(self, output_dir):
        """列出文件"""
        (output_dir / "batch_decision_a_000000.json").touch()
        (output_dir / "batch_decision_b_000000.json").touch()
        (output_dir / "other.txt").touch()  # 不应匹配

        files = list_output_files()
        assert len(files) == 2

    def test_clean_old_files(self, output_dir):
        """清理旧文件"""
        for i in range(15):
            (output_dir / f"batch_decision_test_{i:06d}.json").touch()

        deleted = clean_old_files(keep_count=10)
        assert deleted == 5

        remaining = list_output_files()
        assert len(remaining) == 10

    def test_clean_all(self, output_dir):
        """清空所有"""
        for i in range(5):
            (output_dir / f"batch_decision_test_{i:06d}.json").touch()

        deleted = clean_all()
        assert deleted == 5
        assert len(list_output_files()) == 0