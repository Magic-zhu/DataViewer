#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试用 LMDB 数据库
"""

import os
import lmdb

# 测试数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_db")

def create_test_db():
    """创建测试数据库"""
    # 如果目录已存在，先删除
    if os.path.exists(DB_PATH):
        import shutil
        shutil.rmtree(DB_PATH)
    
    os.makedirs(DB_PATH, exist_ok=True)
    
    # 创建数据库
    env = lmdb.open(DB_PATH, map_size=10 * 1024 * 1024)  # 10MB
    
    with env.begin(write=True) as txn:
        # 基本字符串键值
        for i in range(50):
            txn.put(f"key_{i:03d}".encode(), f"value_{i:03d}_test_data".encode())
        
        # JSON 数据
        import json
        json_data = {
            "name": "test",
            "version": "1.0.0",
            "items": [1, 2, 3, 4, 5],
            "nested": {"a": 1, "b": 2}
        }
        txn.put(b"json_data", json.dumps(json_data).encode())
        
        # MessagePack 数据
        try:
            import msgpack
            msgpack_data = {"type": "msgpack", "data": [1, 2, 3], "flag": True}
            txn.put(b"msgpack_data", msgpack.packb(msgpack_data))
        except ImportError:
            print("msgpack not installed, skipping msgpack test data")
        
        # 中文数据
        txn.put("中文键".encode('utf-8'), "这是一个中文值的测试数据".encode('utf-8'))
        
        # 二进制数据
        txn.put(b"binary_data", bytes(range(256)))
        
        # 空值
        txn.put(b"empty_value", b"")
        
        # 大数据 (10KB)
        txn.put(b"large_data", b"x" * 10240)
        
        # 特殊字符键
        txn.put(b"key:with:colons", b"value with special key")
        txn.put(b"key-with-dashes", b"another special key")
        txn.put(b"key.with.dots", b"yet another")
        
        # 前缀测试数据
        for prefix in ["user", "config", "temp"]:
            for i in range(5):
                txn.put(f"{prefix}_item_{i}".encode(), f"{prefix} value {i}".encode())
    
    env.close()
    print(f"测试数据库已创建: {DB_PATH}")
    print("包含以下测试数据:")
    print("  - 50 个基本键值对 (key_000 - key_049)")
    print("  - JSON 格式数据")
    print("  - MessagePack 格式数据")
    print("  - 中文键值")
    print("  - 二进制数据")
    print("  - 空值")
    print("  - 大数据 (10KB)")
    print("  - 特殊字符键")
    print("  - 前缀测试数据 (user_*, config_*, temp_*)")

if __name__ == "__main__":
    create_test_db()
