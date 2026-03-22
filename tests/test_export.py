"""
测试数据导出模块
"""
import pytest
import tempfile
import os

from utils.export import DataExporter, ExportError
from core.base import KeyValueItem


class TestDataExporter:
    """测试 DataExporter"""

    @pytest.fixture
    def sample_items(self):
        """创建测试数据"""
        return [
            KeyValueItem(key=b"key1", value=b"value1", key_size=4, value_size=6),
            KeyValueItem(key=b"key2", value=b"value2", key_size=4, value_size=6),
            KeyValueItem(key=b"key3", value=b"value3", key_size=4, value_size=6),
        ]

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_export_json(self, sample_items, temp_dir):
        """测试 JSON 导出"""
        file_path = os.path.join(temp_dir, "export.json")
        result = DataExporter.export(sample_items, file_path, DataExporter.Format.JSON)

        assert result is True
        assert os.path.exists(file_path)

        # 验证内容
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data) == 3
        assert data[0]['key'] == 'key1'
        assert data[0]['value'] == 'value1'

    def test_export_csv(self, sample_items, temp_dir):
        """测试 CSV 导出"""
        file_path = os.path.join(temp_dir, "export.csv")
        result = DataExporter.export(sample_items, file_path, DataExporter.Format.CSV)

        assert result is True
        assert os.path.exists(file_path)

        # 验证内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        assert len(lines) == 4  # header + 3 data rows
        assert 'Key,Value' in lines[0]
        assert 'key1' in lines[1]

    def test_export_txt(self, sample_items, temp_dir):
        """测试 TXT 导出"""
        file_path = os.path.join(temp_dir, "export.txt")
        result = DataExporter.export(sample_items, file_path, DataExporter.Format.TXT)

        assert result is True
        assert os.path.exists(file_path)

        # 验证内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'DataViewer Export' in content
        assert 'key1' in content

    def test_export_empty_items(self, temp_dir):
        """测试空数据导出"""
        file_path = os.path.join(temp_dir, "export.json")
        result = DataExporter.export([], file_path, DataExporter.Format.JSON)

        assert result is True

        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data) == 0

    def test_export_to_clipboard_json(self, sample_items):
        """测试剪贴板导出 JSON"""
        result = DataExporter.export_to_clipboard(sample_items, DataExporter.Format.JSON)

        import json
        data = json.loads(result)
        assert len(data) == 3

    def test_export_to_clipboard_csv(self, sample_items):
        """测试剪贴板导出 CSV"""
        result = DataExporter.export_to_clipboard(sample_items, DataExporter.Format.CSV)

        lines = result.split('\n')
        assert 'Key,Value' in lines[0]

    def test_export_to_clipboard_txt(self, sample_items):
        """测试剪贴板导出 TXT"""
        result = DataExporter.export_to_clipboard(sample_items, DataExporter.Format.TXT)

        assert '[1]' in result
        assert 'key1' in result

    def test_export_unicode_data(self, temp_dir):
        """测试 Unicode 数据导出"""
        items = [
            KeyValueItem(key="中文键".encode('utf-8'), value="中文值".encode('utf-8')),
        ]

        file_path = os.path.join(temp_dir, "export.json")
        result = DataExporter.export(items, file_path, DataExporter.Format.JSON)

        assert result is True

        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data[0]['key'] == '中文键'
        assert data[0]['value'] == '中文值'

    def test_export_creates_directory(self, sample_items, temp_dir):
        """测试自动创建目录"""
        file_path = os.path.join(temp_dir, "subdir", "export.json")
        result = DataExporter.export(sample_items, file_path, DataExporter.Format.JSON)

        assert result is True
        assert os.path.exists(file_path)
