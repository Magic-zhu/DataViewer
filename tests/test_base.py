"""
测试数据库基类模块
"""
import pytest
from abc import ABC
from core.base import (
    DatabaseAdapter,
    DatabaseStats,
    KeyValueItem,
    ConnectionStatus,
)


class TestConnectionStatus:
    """测试 ConnectionStatus 枚举"""

    def test_enum_values(self):
        """测试枚举值"""
        assert ConnectionStatus.DISCONNECTED.value == "disconnected"
        assert ConnectionStatus.CONNECTED.value == "connected"
        assert ConnectionStatus.ERROR.value == "error"


class TestDatabaseStats:
    """测试 DatabaseStats 数据类"""

    def test_default_values(self):
        """测试默认值"""
        stats = DatabaseStats()
        assert stats.total_entries == 0
        assert stats.total_size == 0
        assert stats.read_only is True
        assert stats.extra is None

    def test_custom_values(self):
        """测试自定义值"""
        stats = DatabaseStats(
            total_entries=100,
            total_size=1024,
            db_path="/path/to/db",
            read_only=False,
            extra={"custom": "value"}
        )
        assert stats.total_entries == 100
        assert stats.total_size == 1024
        assert stats.db_path == "/path/to/db"
        assert stats.read_only is False
        assert stats.extra == {"custom": "value"}


class TestKeyValueItem:
    """测试 KeyValueItem 数据类"""

    def test_basic_item(self):
        """测试基本数据项"""
        item = KeyValueItem(key=b"key1", value=b"value1")
        assert item.key == b"key1"
        assert item.value == b"value1"
        assert item.key_size == 4
        assert item.value_size == 6

    def test_explicit_sizes(self):
        """测试显式指定大小"""
        item = KeyValueItem(key=b"key1", value=b"value1", key_size=100, value_size=200)
        assert item.key_size == 100
        assert item.value_size == 200

    def test_empty_item(self):
        """测试空数据项"""
        item = KeyValueItem(key=b"", value=b"")
        assert item.key_size == 0
        assert item.value_size == 0


class TestDatabaseAdapter:
    """测试 DatabaseAdapter 抽象基类"""

    def test_is_abstract(self):
        """测试抽象类不能直接实例化"""
        with pytest.raises(TypeError):
            DatabaseAdapter()

    def test_abstract_methods(self):
        """测试子类必须实现所有抽象方法"""
        class IncompleteAdapter(DatabaseAdapter):
            pass

        with pytest.raises(TypeError):
            IncompleteAdapter()

    def test_complete_implementation(self):
        """测试完整实现"""
        class MockAdapter(DatabaseAdapter):
            def __init__(self):
                self._connected = False

            def connect(self, path: str, read_only: bool = True) -> bool:
                self._connected = True
                return True

            def disconnect(self) -> None:
                self._connected = False

            def is_connected(self) -> bool:
                return self._connected

            def get_all_keys(self):
                return [b"key1", b"key2"]

            def get_value(self, key: bytes):
                return b"value1" if key == b"key1" else None

            def set_value(self, key: bytes, value: bytes) -> bool:
                return True

            def delete_value(self, key: bytes) -> bool:
                return True

            def get_stats(self) -> DatabaseStats:
                return DatabaseStats(total_entries=2)

            def iter_items(self):
                yield KeyValueItem(b"key1", b"value1")
                yield KeyValueItem(b"key2", b"value2")

            def count(self) -> int:
                return 2

        adapter = MockAdapter()
        assert adapter.connect("/path") is True
        assert adapter.is_connected() is True
        assert len(adapter.get_all_keys()) == 2
        assert adapter.get_value(b"key1") == b"value1"
        assert adapter.get_value(b"key3") is None

    def test_context_manager(self):
        """测试上下文管理器"""
        class MockAdapter(DatabaseAdapter):
            def __init__(self):
                self._connected = False

            def connect(self, path: str, read_only: bool = True) -> bool:
                self._connected = True
                return True

            def disconnect(self) -> None:
                self._connected = False

            def is_connected(self) -> bool:
                return self._connected

            def get_all_keys(self):
                return []

            def get_value(self, key: bytes):
                return None

            def set_value(self, key: bytes, value: bytes) -> bool:
                return True

            def delete_value(self, key: bytes) -> bool:
                return True

            def get_stats(self) -> DatabaseStats:
                return DatabaseStats()

            def iter_items(self):
                return iter([])

            def count(self) -> int:
                return 0

        adapter = MockAdapter()
        adapter.connect("/path")

        with adapter as a:
            assert a.is_connected() is True

        # 退出上下文后应断开连接
        assert adapter.is_connected() is False

    def test_get_page_default_implementation(self):
        """测试默认分页实现"""
        class MockAdapter(DatabaseAdapter):
            def __init__(self):
                self._data = [
                    KeyValueItem(f"key{i}".encode(), f"value{i}".encode())
                    for i in range(10)
                ]

            def connect(self, path: str, read_only: bool = True) -> bool:
                return True

            def disconnect(self) -> None:
                pass

            def is_connected(self) -> bool:
                return True

            def get_all_keys(self):
                return [item.key for item in self._data]

            def get_value(self, key: bytes):
                for item in self._data:
                    if item.key == key:
                        return item.value
                return None

            def set_value(self, key: bytes, value: bytes) -> bool:
                return True

            def delete_value(self, key: bytes) -> bool:
                return True

            def get_stats(self) -> DatabaseStats:
                return DatabaseStats(total_entries=len(self._data))

            def iter_items(self):
                return iter(self._data)

            def count(self) -> int:
                return len(self._data)

        adapter = MockAdapter()

        # 测试第一页
        page = adapter.get_page(offset=0, limit=3)
        assert len(page) == 3
        assert page[0].key == b"key0"

        # 测试第二页
        page = adapter.get_page(offset=3, limit=3)
        assert len(page) == 3
        assert page[0].key == b"key3"

        # 测试最后一页
        page = adapter.get_page(offset=9, limit=3)
        assert len(page) == 1
        assert page[0].key == b"key9"

    def test_search_keys_substring(self):
        """测试键搜索（子串匹配）"""
        class MockAdapter(DatabaseAdapter):
            def __init__(self):
                self._keys = [b"apple", b"application", b"banana", b"app"]

            def connect(self, path: str, read_only: bool = True) -> bool:
                return True

            def disconnect(self) -> None:
                pass

            def is_connected(self) -> bool:
                return True

            def get_all_keys(self):
                return self._keys

            def get_value(self, key: bytes):
                return None

            def set_value(self, key: bytes, value: bytes) -> bool:
                return True

            def delete_value(self, key: bytes) -> bool:
                return True

            def get_stats(self) -> DatabaseStats:
                return DatabaseStats()

            def iter_items(self):
                return iter([])

            def count(self) -> int:
                return len(self._keys)

        adapter = MockAdapter()
        results = adapter.search_keys("app")
        assert len(results) == 3
        assert b"apple" in results
        assert b"application" in results
        assert b"app" in results
        assert b"banana" not in results

    def test_search_keys_regex(self):
        """测试键搜索（正则表达式）"""
        class MockAdapter(DatabaseAdapter):
            def __init__(self):
                self._keys = [b"key1", b"key2", b"item1", b"key10"]

            def connect(self, path: str, read_only: bool = True) -> bool:
                return True

            def disconnect(self) -> None:
                pass

            def is_connected(self) -> bool:
                return True

            def get_all_keys(self):
                return self._keys

            def get_value(self, key: bytes):
                return None

            def set_value(self, key: bytes, value: bytes) -> bool:
                return True

            def delete_value(self, key: bytes) -> bool:
                return True

            def get_stats(self) -> DatabaseStats:
                return DatabaseStats()

            def iter_items(self):
                return iter([])

            def count(self) -> int:
                return len(self._keys)

        adapter = MockAdapter()
        results = adapter.search_keys(r"key\d", regex=True)
        assert len(results) == 3
        assert b"key1" in results
        assert b"key2" in results
        assert b"key10" in results

    def test_search_values(self):
        """测试值搜索"""
        class MockAdapter(DatabaseAdapter):
            def __init__(self):
                self._data = [
                    KeyValueItem(b"k1", b"hello world"),
                    KeyValueItem(b"k2", b"hello python"),
                    KeyValueItem(b"k3", b"goodbye"),
                ]

            def connect(self, path: str, read_only: bool = True) -> bool:
                return True

            def disconnect(self) -> None:
                pass

            def is_connected(self) -> bool:
                return True

            def get_all_keys(self):
                return [item.key for item in self._data]

            def get_value(self, key: bytes):
                return None

            def set_value(self, key: bytes, value: bytes) -> bool:
                return True

            def delete_value(self, key: bytes) -> bool:
                return True

            def get_stats(self) -> DatabaseStats:
                return DatabaseStats()

            def iter_items(self):
                return iter(self._data)

            def count(self) -> int:
                return len(self._data)

        adapter = MockAdapter()
        results = adapter.search_values("hello")
        assert len(results) == 2
