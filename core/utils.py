"""
通用工具函数模块

提供数据处理相关的通用工具函数。
"""

import json
from typing import Any, Optional, Tuple

# 尝试导入 msgpack，如果不可用则设置标志
try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False


def format_bytes(data: bytes, max_len: int = 256) -> str:
    """
    将字节数据格式化为十六进制字符串

    Args:
        data: 原始字节数据
        max_len: 最大显示长度，超过则截断

    Returns:
        格式化后的十六进制字符串
    """
    if not data:
        return ""

    if len(data) > max_len:
        truncated = data[:max_len]
        return truncated.hex() + "..."

    return data.hex()


def detect_encoding(data: bytes) -> str:
    """
    检测数据的编码类型

    Args:
        data: 原始字节数据

    Returns:
        编码类型字符串: 'utf-8', 'ascii', 'binary'
    """
    if not data:
        return 'ascii'

    # 先尝试 ASCII
    try:
        data.decode('ascii')
        return 'ascii'
    except UnicodeDecodeError:
        pass

    # 再尝试 UTF-8
    try:
        data.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        pass

    return 'binary'


def try_decode_text(data: bytes, encoding: Optional[str] = None) -> Tuple[str, bool]:
    """
    尝试将字节数据解码为文本

    Args:
        data: 原始字节数据
        encoding: 指定编码，如果为 None 则自动检测

    Returns:
        (解码后的文本, 是否成功) 元组
    """
    if not data:
        return "", True

    if encoding:
        try:
            return data.decode(encoding), True
        except (UnicodeDecodeError, LookupError):
            return data.hex(), False

    # 自动尝试常见编码（latin-1 和 cp1252 可以解码任何字节，所以不使用）
    for enc in ['utf-8', 'ascii']:
        try:
            return data.decode(enc), True
        except (UnicodeDecodeError, LookupError):
            continue

    return data.hex(), False


def try_parse_json(data: bytes) -> Tuple[Any, bool]:
    """
    尝试将字节数据解析为 JSON

    Args:
        data: 原始字节数据

    Returns:
        (解析结果, 是否成功) 元组
    """
    if not data:
        return None, False

    try:
        text = data.decode('utf-8')
        result = json.loads(text)
        return result, True
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, False


def try_parse_msgpack(data: bytes) -> Tuple[Any, bool]:
    """
    尝试将字节数据解析为 MessagePack

    Args:
        data: 原始字节数据

    Returns:
        (解析结果, 是否成功) 元组
    """
    if not data:
        return None, False

    if not HAS_MSGPACK:
        return None, False

    try:
        result = msgpack.unpackb(data, raw=False)
        return result, True
    except (msgpack.UnpackException, ValueError, TypeError):
        return None, False


def format_size(size: int, precision: int = 2) -> str:
    """
    格式化文件大小为人类可读格式

    Args:
        size: 字节数
        precision: 小数精度

    Returns:
        格式化后的大小字符串，如 "1.23 MB"
    """
    if size < 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0

    value = float(size)
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"

    return f"{value:.{precision}f} {units[unit_index]}"


def is_printable(data: bytes, threshold: float = 0.85) -> bool:
    """
    检查数据是否主要是可打印字符

    Args:
        data: 原始字节数据
        threshold: 可打印字符比例阈值，默认 0.85

    Returns:
        如果可打印字符比例超过阈值则返回 True
    """
    if not data:
        return True

    printable_count = 0
    for byte in data:
        # 可打印 ASCII 范围: 32-126，加上换行、制表符等
        if 32 <= byte <= 126 or byte in (9, 10, 13):
            printable_count += 1

    ratio = printable_count / len(data)
    return ratio >= threshold


def truncate_bytes(data: bytes, max_len: int = 1024) -> Tuple[bytes, bool]:
    """
    截断字节数据

    Args:
        data: 原始字节数据
        max_len: 最大长度

    Returns:
        (截断后的数据, 是否被截断) 元组
    """
    if not data:
        return b"", False

    if len(data) <= max_len:
        return data, False

    return data[:max_len], True


def safe_repr(data: bytes, max_len: int = 100) -> str:
    """
    安全地表示字节数据

    如果是可打印文本则返回解码后的字符串，
    否则返回十六进制表示。

    Args:
        data: 原始字节数据
        max_len: 最大显示长度

    Returns:
        安全的字符串表示
    """
    if not data:
        return "(empty)"

    truncated, was_truncated = truncate_bytes(data, max_len)

    if is_printable(truncated):
        text, _ = try_decode_text(truncated)
        suffix = "..." if was_truncated else ""
        return text + suffix

    hex_str = format_bytes(data, max_len // 2)
    return f"<hex> {hex_str}"


def calculate_hash(data: bytes, algorithm: str = 'md5') -> str:
    """
    计算数据的哈希值

    Args:
        data: 原始字节数据
        algorithm: 哈希算法，支持 'md5', 'sha1', 'sha256'

    Returns:
        哈希值的十六进制字符串
    """
    import hashlib

    if not data:
        return ""

    algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
    }

    if algorithm not in algorithms:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    hasher = algorithms[algorithm]()
    hasher.update(data)
    return hasher.hexdigest()
