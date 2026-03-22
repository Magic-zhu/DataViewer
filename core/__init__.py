"""
Core 模块 - 数据库核心抽象层

提供数据库操作的统一接口和 LMDB 实现。
"""

from .base import (
    DatabaseAdapter,
    DatabaseStats,
    KeyValueItem,
    ConnectionStatus,
)
from .lmdb_adapter import LMDBAdapter, LMDBError
from .utils import (
    format_bytes,
    detect_encoding,
    try_decode_text,
    try_parse_json,
    try_parse_msgpack,
    format_size,
    is_printable,
    truncate_bytes,
    safe_repr,
    calculate_hash,
    HAS_MSGPACK,
)

__all__ = [
    # Base
    'DatabaseAdapter',
    'DatabaseStats',
    'KeyValueItem',
    'ConnectionStatus',
    # LMDB
    'LMDBAdapter',
    'LMDBError',
    # Utils
    'format_bytes',
    'detect_encoding',
    'try_decode_text',
    'try_parse_json',
    'try_parse_msgpack',
    'format_size',
    'is_printable',
    'truncate_bytes',
    'safe_repr',
    'calculate_hash',
    'HAS_MSGPACK',
]
