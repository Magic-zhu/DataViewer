"""
数据库抽象基类模块

定义统一的数据库接口，便于未来扩展支持其他数据库类型。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Tuple


class ConnectionStatus(Enum):
    """连接状态枚举"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class DatabaseStats:
    """数据库统计信息"""
    total_entries: int = 0
    total_size: int = 0
    key_size_total: int = 0
    value_size_total: int = 0
    avg_key_size: float = 0.0
    avg_value_size: float = 0.0
    max_key_size: int = 0
    max_value_size: int = 0
    min_key_size: int = 0
    min_value_size: int = 0
    db_path: str = ""
    read_only: bool = True
    extra: Optional[Dict[str, Any]] = None


@dataclass
class KeyValueItem:
    """键值对数据项"""
    key: bytes
    value: bytes
    key_size: int = 0
    value_size: int = 0

    def __post_init__(self):
        if self.key_size == 0:
            self.key_size = len(self.key)
        if self.value_size == 0:
            self.value_size = len(self.value)


class DatabaseAdapter(ABC):
    """
    数据库适配器抽象基类

    所有数据库适配器必须实现此接口，以提供统一的操作方式。
    """

    @abstractmethod
    def connect(self, path: str, read_only: bool = True) -> bool:
        """
        连接到数据库

        Args:
            path: 数据库路径
            read_only: 是否以只读模式打开，默认为 True

        Returns:
            连接成功返回 True，否则返回 False
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开数据库连接并释放资源"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        检查数据库是否已连接

        Returns:
            已连接返回 True，否则返回 False
        """
        pass

    @abstractmethod
    def get_all_keys(self) -> List[bytes]:
        """
        获取数据库中所有的键

        Returns:
            键的列表（bytes 格式）
        """
        pass

    @abstractmethod
    def get_value(self, key: bytes) -> Optional[bytes]:
        """
        根据键获取值

        Args:
            key: 要查找的键（bytes 格式）

        Returns:
            找到返回对应的值（bytes），否则返回 None
        """
        pass

    @abstractmethod
    def set_value(self, key: bytes, value: bytes) -> bool:
        """
        设置键值对

        Args:
            key: 键（bytes 格式）
            value: 值（bytes 格式）

        Returns:
            设置成功返回 True，否则返回 False
        """
        pass

    @abstractmethod
    def delete_value(self, key: bytes) -> bool:
        """
        删除指定键的值

        Args:
            key: 要删除的键（bytes 格式）

        Returns:
            删除成功返回 True，键不存在返回 False
        """
        pass

    @abstractmethod
    def get_stats(self) -> DatabaseStats:
        """
        获取数据库统计信息

        Returns:
            DatabaseStats 对象包含各种统计信息
        """
        pass

    @abstractmethod
    def iter_items(self) -> Iterator[KeyValueItem]:
        """
        迭代所有键值对

        Yields:
            KeyValueItem 对象
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        获取数据库中条目的总数

        Returns:
            条目总数
        """
        pass

    def get_page(self, offset: int = 0, limit: int = 100) -> List[KeyValueItem]:
        """
        分页获取数据

        Args:
            offset: 起始偏移量，默认为 0
            limit: 每页数量，默认为 100

        Returns:
            KeyValueItem 列表
        """
        items = []
        for i, item in enumerate(self.iter_items()):
            if i < offset:
                continue
            if len(items) >= limit:
                break
            items.append(item)
        return items

    def search_keys(self, pattern: str, regex: bool = False) -> List[bytes]:
        """
        搜索匹配的键

        Args:
            pattern: 搜索模式
            regex: 是否使用正则表达式，默认为 False（子串匹配）

        Returns:
            匹配的键列表
        """
        import re

        matches = []
        if regex:
            regex_pattern = re.compile(pattern)
            for key in self.get_all_keys():
                try:
                    decoded = key.decode('utf-8', errors='replace')
                    if regex_pattern.search(decoded):
                        matches.append(key)
                except Exception:
                    if regex_pattern.search(key):
                        matches.append(key)
        else:
            pattern_bytes = pattern.encode('utf-8')
            for key in self.get_all_keys():
                if pattern_bytes in key:
                    matches.append(key)
                else:
                    try:
                        decoded = key.decode('utf-8', errors='replace')
                        if pattern in decoded:
                            matches.append(key)
                    except Exception:
                        pass
        return matches

    def search_values(self, pattern: str, regex: bool = False) -> List[Tuple[bytes, bytes]]:
        """
        搜索匹配的值

        Args:
            pattern: 搜索模式
            regex: 是否使用正则表达式，默认为 False（子串匹配）

        Returns:
            匹配的 (key, value) 元组列表
        """
        import re

        matches = []
        if regex:
            regex_pattern = re.compile(pattern)
            for item in self.iter_items():
                try:
                    decoded = item.value.decode('utf-8', errors='replace')
                    if regex_pattern.search(decoded):
                        matches.append((item.key, item.value))
                except Exception:
                    if regex_pattern.search(item.value):
                        matches.append((item.key, item.value))
        else:
            pattern_bytes = pattern.encode('utf-8')
            for item in self.iter_items():
                if pattern_bytes in item.value:
                    matches.append((item.key, item.value))
                else:
                    try:
                        decoded = item.value.decode('utf-8', errors='replace')
                        if pattern in decoded:
                            matches.append((item.key, item.value))
                    except Exception:
                        pass
        return matches

    def __enter__(self) -> 'DatabaseAdapter':
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口，自动断开连接"""
        self.disconnect()
