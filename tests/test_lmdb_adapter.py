"""
测试 LMDB 适配器模块
"""
import os
import tempfile
import shutil
import pytest

from core.lmdb_adapter import LMDBAdapter, LMDBError
from core.base import DatabaseStats, KeyValueItem

# 尝试导入 lmdb
try:
    import lmdb
    HAS_LMDB = True
except ImportError:
    HAS_LMDB = False


@pytest.mark.skipif(not HAS_LMDB, reason="lmdb not installed")
class TestLMDBAdapter:
    """测试 LMDB 适配器"""

    @pytest.fixture
    def temp_db(self):
        """创建临时测试数据库"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_db")

        # 创建数据库并添加测试数据
        env = lmdb.open(db_path, map_size=1024 * 1024)
        with env.begin(write=True) as txn:
            txn.put(b"key1", b"value1")
            txn.put(b"key2", b"value2")
            txn.put(b"key3", b"value3")
        env.close()

        yield db_path

        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def adapter(self):
        """创建适配器实例"""
        return LMDBAdapter()

    def test_init(self, adapter):
        """测试初始化"""
        assert adapter.is_connected() is False

    def test_connect_read_only(self, adapter, temp_db):
        """测试只读模式连接"""
        result = adapter.connect(temp_db, read_only=True)
        assert result is True
        assert adapter.is_connected() is True
        adapter.disconnect()

    def test_connect_read_write(self, adapter, temp_db):
        """测试读写模式连接"""
        result = adapter.connect(temp_db, read_only=False)
        assert result is True
        assert adapter.is_connected() is True
        adapter.disconnect()

    def test_connect_invalid_path(self, adapter):
        """测试连接无效路径"""
        with pytest.raises(LMDBError):
            adapter.connect("/nonexistent/path")

    def test_disconnect(self, adapter, temp_db):
        """测试断开连接"""
        adapter.connect(temp_db)
        assert adapter.is_connected() is True

        adapter.disconnect()
        assert adapter.is_connected() is False

    def test_get_all_keys(self, adapter, temp_db):
        """测试获取所有键"""
        adapter.connect(temp_db)
        keys = adapter.get_all_keys()
        assert len(keys) == 3
        assert b"key1" in keys
        assert b"key2" in keys
        assert b"key3" in keys
        adapter.disconnect()

    def test_get_value_existing(self, adapter, temp_db):
        """测试获取存在的值"""
        adapter.connect(temp_db)
        value = adapter.get_value(b"key1")
        assert value == b"value1"
        adapter.disconnect()

    def test_get_value_non_existing(self, adapter, temp_db):
        """测试获取不存在的值"""
        adapter.connect(temp_db)
        value = adapter.get_value(b"nonexistent")
        assert value is None
        adapter.disconnect()

    def test_set_value(self, adapter, temp_db):
        """测试设置值"""
        adapter.connect(temp_db, read_only=False)
        result = adapter.set_value(b"key4", b"value4")
        assert result is True

        value = adapter.get_value(b"key4")
        assert value == b"value4"
        adapter.disconnect()

    def test_set_value_read_only(self, adapter, temp_db):
        """测试只读模式下设置值"""
        adapter.connect(temp_db, read_only=True)
        with pytest.raises(LMDBError):
            adapter.set_value(b"key4", b"value4")
        adapter.disconnect()

    def test_delete_value(self, adapter, temp_db):
        """测试删除值"""
        adapter.connect(temp_db, read_only=False)
        result = adapter.delete_value(b"key1")
        assert result is True

        value = adapter.get_value(b"key1")
        assert value is None
        adapter.disconnect()

    def test_delete_value_non_existing(self, adapter, temp_db):
        """测试删除不存在的值"""
        adapter.connect(temp_db, read_only=False)
        result = adapter.delete_value(b"nonexistent")
        assert result is False
        adapter.disconnect()

    def test_delete_value_read_only(self, adapter, temp_db):
        """测试只读模式下删除值"""
        adapter.connect(temp_db, read_only=True)
        with pytest.raises(LMDBError):
            adapter.delete_value(b"key1")
        adapter.disconnect()

    def test_get_stats(self, adapter, temp_db):
        """测试获取统计信息"""
        adapter.connect(temp_db)
        stats = adapter.get_stats()

        assert isinstance(stats, DatabaseStats)
        assert stats.total_entries == 3
        assert stats.db_path == temp_db
        assert stats.read_only is True
        assert stats.extra is not None
        adapter.disconnect()

    def test_iter_items(self, adapter, temp_db):
        """测试迭代键值对"""
        adapter.connect(temp_db)
        items = list(adapter.iter_items())

        assert len(items) == 3
        for item in items:
            assert isinstance(item, KeyValueItem)
            assert item.key.startswith(b"key")
            assert item.value.startswith(b"value")
        adapter.disconnect()

    def test_count(self, adapter, temp_db):
        """测试获取条目数量"""
        adapter.connect(temp_db)
        count = adapter.count()
        assert count == 3
        adapter.disconnect()

    def test_get_page(self, adapter, temp_db):
        """测试分页获取数据"""
        adapter.connect(temp_db)

        # 添加更多数据用于分页测试
        adapter.disconnect()
        adapter.connect(temp_db, read_only=False)
        for i in range(4, 15):
            adapter.set_value(f"key{i}".encode(), f"value{i}".encode())
        adapter.disconnect()

        adapter.connect(temp_db)

        # 第一页
        page = adapter.get_page(offset=0, limit=5)
        assert len(page) == 5

        # 第二页
        page = adapter.get_page(offset=5, limit=5)
        assert len(page) == 5

        adapter.disconnect()

    def test_get_page_empty(self, adapter, temp_db):
        """测试分页获取空数据"""
        adapter.connect(temp_db)

        # 超出范围的分页
        page = adapter.get_page(offset=100, limit=10)
        assert len(page) == 0

        adapter.disconnect()

    def test_search_keys(self, adapter, temp_db):
        """测试键搜索"""
        adapter.connect(temp_db)
        results = adapter.search_keys("key")
        assert len(results) == 3

        results = adapter.search_keys("key1")
        assert len(results) == 1
        adapter.disconnect()

    def test_search_keys_regex(self, adapter, temp_db):
        """测试键搜索（正则表达式）"""
        adapter.connect(temp_db)
        results = adapter.search_keys(r"key[12]", regex=True)
        assert len(results) == 2
        adapter.disconnect()

    def test_search_values(self, adapter, temp_db):
        """测试值搜索"""
        adapter.connect(temp_db)
        results = adapter.search_values("value")
        assert len(results) == 3
        adapter.disconnect()

    def test_context_manager(self, adapter, temp_db):
        """测试上下文管理器"""
        with LMDBAdapter() as adapter:
            adapter.connect(temp_db)
            assert adapter.is_connected() is True

        # 退出上下文后应断开连接
        assert adapter.is_connected() is False

    def test_get_env_info(self, adapter, temp_db):
        """测试获取环境信息"""
        adapter.connect(temp_db)
        info = adapter.get_env_info()

        assert info['path'] == temp_db
        assert info['entries'] == 3
        assert 'map_size' in info
        assert 'page_size' in info
        adapter.disconnect()

    def test_operation_without_connection(self, adapter):
        """测试未连接时执行操作"""
        with pytest.raises(LMDBError):
            adapter.get_all_keys()

        with pytest.raises(LMDBError):
            adapter.get_value(b"key")

        with pytest.raises(LMDBError):
            adapter.get_stats()

    def test_reconnect(self, adapter, temp_db):
        """测试重新连接"""
        adapter.connect(temp_db)
        assert adapter.is_connected() is True

        # 重新连接应该自动断开之前的连接
        adapter.connect(temp_db)
        assert adapter.is_connected() is True

        adapter.disconnect()


@pytest.mark.skipif(not HAS_LMDB, reason="lmdb not installed")
class TestLMDBAdapterEdgeCases:
    """测试 LMDB 适配器边缘情况"""

    @pytest.fixture
    def empty_db(self):
        """创建空数据库"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "empty_db")

        env = lmdb.open(db_path, map_size=1024 * 1024)
        env.close()

        yield db_path

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_empty_database(self, empty_db):
        """测试空数据库"""
        adapter = LMDBAdapter()
        adapter.connect(empty_db)

        assert adapter.count() == 0
        assert len(adapter.get_all_keys()) == 0
        assert adapter.get_value(b"any") is None

        stats = adapter.get_stats()
        assert stats.total_entries == 0

        adapter.disconnect()

    def test_large_key_value(self):
        """测试大键值对"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "large_db")

        # 创建包含大值的数据库
        env = lmdb.open(db_path, map_size=10 * 1024 * 1024)
        large_value = b"x" * 100000  # 100KB
        with env.begin(write=True) as txn:
            txn.put(b"large_key", large_value)
        env.close()

        adapter = LMDBAdapter()
        adapter.connect(db_path)

        value = adapter.get_value(b"large_key")
        assert value == large_value

        adapter.disconnect()
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_unicode_keys_values(self):
        """测试 Unicode 键值"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "unicode_db")

        env = lmdb.open(db_path, map_size=1024 * 1024)
        with env.begin(write=True) as txn:
            txn.put("中文键".encode('utf-8'), "中文值".encode('utf-8'))
            txn.put("emoji".encode('utf-8'), "😀🎉".encode('utf-8'))
        env.close()

        adapter = LMDBAdapter()
        adapter.connect(db_path)

        value = adapter.get_value("中文键".encode('utf-8'))
        assert value == "中文值".encode('utf-8')

        value = adapter.get_value("emoji".encode('utf-8'))
        assert value == "😀🎉".encode('utf-8')

        adapter.disconnect()
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_binary_keys_values(self):
        """测试二进制键值"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "binary_db")

        env = lmdb.open(db_path, map_size=1024 * 1024)
        with env.begin(write=True) as txn:
            txn.put(b"\x00\x01\x02\x03", b"\xff\xfe\xfd\xfc")
        env.close()

        adapter = LMDBAdapter()
        adapter.connect(db_path)

        value = adapter.get_value(b"\x00\x01\x02\x03")
        assert value == b"\xff\xfe\xfd\xfc"

        adapter.disconnect()
        shutil.rmtree(temp_dir, ignore_errors=True)
