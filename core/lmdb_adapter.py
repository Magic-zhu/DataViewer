"""
LMDB 数据库适配器模块

实现 DatabaseAdapter 接口，封装 LMDB 操作。
"""

import os
from typing import Dict, Iterator, List, Optional, Any

from .base import DatabaseAdapter, DatabaseStats, KeyValueItem

# 尝试导入 lmdb，如果不可用则抛出错误
try:
    import lmdb
    HAS_LMDB = True
except ImportError:
    HAS_LMDB = False
    lmdb = None  # type: ignore


class LMDBError(Exception):
    """LMDB 相关错误"""
    pass


class LMDBAdapter(DatabaseAdapter):
    """
    LMDB 数据库适配器

    实现 DatabaseAdapter 接口，提供 LMDB 数据库的操作功能。
    """

    DEFAULT_MAP_SIZE = 1024 * 1024 * 1024  # 1GB 默认 map size
    DEFAULT_MAX_READERS = 126
    DEFAULT_MAX_DBS = 10

    def __init__(self):
        """初始化 LMDB 适配器"""
        if not HAS_LMDB:
            raise LMDBError(
                "lmdb module not installed. "
                "Please install it with: pip install lmdb"
            )

        self._env: Optional[lmdb.Environment] = None
        self._db: Optional[lmdb._Database] = None
        self._path: str = ""
        self._read_only: bool = True
        self._connected: bool = False

    def connect(self, path: str, read_only: bool = True) -> bool:
        """
        连接到 LMDB 数据库

        Args:
            path: 数据库路径
            read_only: 是否以只读模式打开

        Returns:
            连接成功返回 True

        Raises:
            LMDBError: 连接失败时抛出
        """
        if self._connected:
            self.disconnect()

        if not os.path.exists(path):
            raise LMDBError(f"Database path does not exist: {path}")

        try:
            # 检查目录权限
            if read_only:
                if not os.access(path, os.R_OK):
                    raise LMDBError(f"No read permission for path: {path}")
            else:
                if not os.access(path, os.R_OK | os.W_OK):
                    raise LMDBError(f"No write permission for path: {path}")

            self._env = lmdb.open(
                path,
                readonly=read_only,
                map_size=self.DEFAULT_MAP_SIZE,
                max_readers=self.DEFAULT_MAX_READERS,
                max_dbs=self.DEFAULT_MAX_DBS,
                lock=not read_only,
            )

            # 获取默认数据库句柄（None 表示使用默认数据库）
            self._db = None

            self._path = path
            self._read_only = read_only
            self._connected = True
            return True

        except lmdb.Error as e:
            raise LMDBError(f"Failed to connect to LMDB: {e}")
        except Exception as e:
            raise LMDBError(f"Unexpected error during connection: {e}")

    def disconnect(self) -> None:
        """断开数据库连接并释放资源"""
        if self._env is not None:
            try:
                self._env.close()
            except Exception:
                pass

        self._env = None
        self._db = None
        self._path = ""
        self._read_only = True
        self._connected = False

    def is_connected(self) -> bool:
        """检查数据库是否已连接"""
        return self._connected and self._env is not None

    def _check_connection(self) -> None:
        """检查连接状态，未连接时抛出异常"""
        if not self.is_connected():
            raise LMDBError("Database not connected")

    def _check_write_permission(self) -> None:
        """检查写权限"""
        if self._read_only:
            raise LMDBError("Database is in read-only mode")

    def get_all_keys(self) -> List[bytes]:
        """获取数据库中所有的键"""
        self._check_connection()

        keys: List[bytes] = []
        with self._env.begin() as txn:
            cursor = txn.cursor(self._db)
            for key, _ in cursor:
                keys.append(bytes(key))

        return keys

    def get_value(self, key: bytes) -> Optional[bytes]:
        """根据键获取值"""
        self._check_connection()

        with self._env.begin() as txn:
            value = txn.get(key, db=self._db)
            if value is not None:
                return bytes(value)
            return None

    def set_value(self, key: bytes, value: bytes) -> bool:
        """设置键值对"""
        self._check_connection()
        self._check_write_permission()

        try:
            with self._env.begin(write=True) as txn:
                txn.put(key, value, db=self._db)
            return True
        except lmdb.MapFullError:
            raise LMDBError("Database map is full. Consider increasing map_size.")
        except lmdb.Error as e:
            raise LMDBError(f"Failed to set value: {e}")

    def delete_value(self, key: bytes) -> bool:
        """删除指定键的值"""
        self._check_connection()
        self._check_write_permission()

        try:
            with self._env.begin(write=True) as txn:
                return txn.delete(key, db=self._db)
        except lmdb.Error as e:
            raise LMDBError(f"Failed to delete value: {e}")

    def get_stats(self) -> DatabaseStats:
        """获取数据库统计信息"""
        self._check_connection()

        env_info = self._env.info()
        env_stat = self._env.stat()

        total_entries = env_stat['entries']
        total_size = env_info['map_size']

        # 计算键值大小统计
        key_sizes: List[int] = []
        value_sizes: List[int] = []
        key_size_total = 0
        value_size_total = 0

        with self._env.begin() as txn:
            cursor = txn.cursor(self._db)
            for key, value in cursor:
                k_size = len(key)
                v_size = len(value)
                key_sizes.append(k_size)
                value_sizes.append(v_size)
                key_size_total += k_size
                value_size_total += v_size

        avg_key_size = key_size_total / total_entries if total_entries > 0 else 0.0
        avg_value_size = value_size_total / total_entries if total_entries > 0 else 0.0

        max_key_size = max(key_sizes) if key_sizes else 0
        max_value_size = max(value_sizes) if value_sizes else 0
        min_key_size = min(key_sizes) if key_sizes else 0
        min_value_size = min(value_sizes) if value_sizes else 0

        return DatabaseStats(
            total_entries=total_entries,
            total_size=total_size,
            key_size_total=key_size_total,
            value_size_total=value_size_total,
            avg_key_size=avg_key_size,
            avg_value_size=avg_value_size,
            max_key_size=max_key_size,
            max_value_size=max_value_size,
            min_key_size=min_key_size,
            min_value_size=min_value_size,
            db_path=self._path,
            read_only=self._read_only,
            extra={
                'map_size': env_info['map_size'],
                'map_used': env_info['map_used'] if 'map_used' in env_info else 0,
                'last_pgno': env_stat['psize'] * env_stat['last_pgno'] if 'last_pgno' in env_stat else 0,
                'depth': env_stat['depth'],
                'branch_pages': env_stat['branch_pages'],
                'leaf_pages': env_stat['leaf_pages'],
                'overflow_pages': env_stat['overflow_pages'],
            }
        )

    def iter_items(self) -> Iterator[KeyValueItem]:
        """迭代所有键值对"""
        self._check_connection()

        with self._env.begin() as txn:
            cursor = txn.cursor(self._db)
            for key, value in cursor:
                yield KeyValueItem(
                    key=bytes(key),
                    value=bytes(value),
                    key_size=len(key),
                    value_size=len(value)
                )

    def count(self) -> int:
        """获取数据库中条目的总数"""
        self._check_connection()
        return self._env.stat()['entries']

    def get_page(self, offset: int = 0, limit: int = 100) -> List[KeyValueItem]:
        """
        分页获取数据

        使用 LMDB 的游标进行高效分页。

        Args:
            offset: 起始偏移量
            limit: 每页数量

        Returns:
            KeyValueItem 列表
        """
        self._check_connection()

        items: List[KeyValueItem] = []
        with self._env.begin() as txn:
            cursor = txn.cursor(self._db)

            # 跳过 offset 条记录
            if offset > 0:
                if not cursor.first():
                    return items
                for _ in range(offset):
                    if not cursor.next():
                        return items

            # 获取 limit 条记录
            count = 0
            for key, value in cursor:
                if count >= limit:
                    break
                items.append(KeyValueItem(
                    key=bytes(key),
                    value=bytes(value),
                    key_size=len(key),
                    value_size=len(value)
                ))
                count += 1

        return items

    def get_env_info(self) -> Dict[str, Any]:
        """
        获取 LMDB 环境信息

        Returns:
            包含环境信息的字典
        """
        self._check_connection()

        info = self._env.info()
        stat = self._env.stat()

        return {
            'path': self._path,
            'map_size': info['map_size'],
            'last_pgno': info['last_pgno'],
            'last_txnid': info['last_txnid'],
            'max_readers': info['max_readers'],
            'num_readers': info['num_readers'],
            'page_size': stat['psize'],
            'depth': stat['depth'],
            'branch_pages': stat['branch_pages'],
            'leaf_pages': stat['leaf_pages'],
            'overflow_pages': stat['overflow_pages'],
            'entries': stat['entries'],
        }
