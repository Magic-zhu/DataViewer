"""
测试数据库历史记录模块
"""
import pytest
import tempfile
from pathlib import Path

from config.history import DatabaseHistory


class TestDatabaseHistory:
    """测试 DatabaseHistory"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def history(self, temp_dir):
        """创建历史记录实例"""
        return DatabaseHistory(temp_dir)

    def test_init(self, history):
        """测试初始化"""
        assert history.count() == 0

    def test_add(self, history):
        """测试添加记录"""
        history.add("/path/to/db1")

        assert history.count() == 1
        entries = history.get_all()
        assert len(entries) == 1
        # 路径会被规范化
        assert Path(entries[0].path).name == "db1"

    def test_add_multiple(self, history):
        """测试添加多个记录"""
        history.add("/path/to/db1")
        history.add("/path/to/db2")
        history.add("/path/to/db3")

        assert history.count() == 3
        entries = history.get_all()
        # 最新的应该在最前面
        assert Path(entries[0].path).name == "db3"

    def test_add_duplicate(self, history):
        """测试添加重复记录"""
        history.add("/path/to/db1")
        history.add("/path/to/db2")
        history.add("/path/to/db1")  # 再次添加

        # 应该更新而不是新增
        assert history.count() == 2
        entries = history.get_all()
        # db1 应该移到最前面
        assert Path(entries[0].path).name == "db1"
        assert entries[0].open_count == 2

    def test_remove(self, history):
        """测试移除记录"""
        history.add("/path/to/db1")
        history.add("/path/to/db2")

        result = history.remove("/path/to/db1")
        assert result is True
        assert history.count() == 1

    def test_remove_nonexistent(self, history):
        """测试移除不存在的记录"""
        result = history.remove("/path/to/nonexistent")
        assert result is False

    def test_clear(self, history):
        """测试清空历史"""
        history.add("/path/to/db1")
        history.add("/path/to/db2")

        history.clear()
        assert history.count() == 0

    def test_get_recent(self, history):
        """测试获取最近记录"""
        for i in range(15):
            history.add(f"/path/to/db{i}")

        recent = history.get_recent(5)
        assert len(recent) == 5

    def test_get_by_path(self, history):
        """测试根据路径获取记录"""
        history.add("/path/to/db1")

        entry = history.get_by_path("/path/to/db1")
        assert entry is not None
        assert Path(entry.path).name == "db1"

    def test_get_by_path_nonexistent(self, history):
        """测试获取不存在的记录"""
        entry = history.get_by_path("/path/to/nonexistent")
        assert entry is None

    def test_exists(self, history):
        """测试检查记录是否存在"""
        history.add("/path/to/db1")

        assert history.exists("/path/to/db1") is True
        assert history.exists("/path/to/db2") is False

    def test_max_history_limit(self, history):
        """测试最大历史记录限制"""
        # 添加超过限制的记录
        for i in range(30):
            history.add(f"/path/to/db{i}")

        # 应该只保留 MAX_HISTORY 个记录
        assert history.count() <= DatabaseHistory.MAX_HISTORY

    def test_persistence(self, temp_dir):
        """测试持久化"""
        # 创建第一个实例并 添加记录
        history1 = DatabaseHistory(temp_dir)
        history1.add("/path/to/db1")
        history1.add("/path/to/db2")

        # 创建第二个实例，应该加载之前的记录
        history2 = DatabaseHistory(temp_dir)
        assert history2.count() == 2
        assert history2.exists("/path/to/db1")
