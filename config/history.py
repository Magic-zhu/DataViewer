"""
数据库历史记录模块

管理最近打开的数据库记录。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class HistoryEntry:
    """历史记录条目"""
    path: str
    name: str
    last_opened: str
    open_count: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        return cls(**data)


class DatabaseHistory:
    """
    数据库历史记录管理器

    管理最近打开的数据库列表。
    """

    MAX_HISTORY = 20  # 最大历史记录数

    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化历史记录管理器

        Args:
            config_dir: 配置文件目录，默认为用户目录下的 .dataviewer
        """
        if config_dir is None:
            config_dir = Path.home() / ".dataviewer"

        self._config_dir = config_dir
        self._history_file = config_dir / "history.json"
        self._entries: List[HistoryEntry] = []

        self._load()

    def _load(self) -> None:
        """加载历史记录"""
        if not self._history_file.exists():
            return

        try:
            with open(self._history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._entries = [HistoryEntry.from_dict(item) for item in data]
        except Exception:
            self._entries = []

    def _save(self) -> None:
        """保存历史记录"""
        self._config_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump([e.to_dict() for e in self._entries], f, indent=2)
        except Exception:
            pass

    def add(self, path: str) -> None:
        """
        添加数据库到历史记录

        Args:
            path: 数据库路径
        """
        path = str(Path(path).resolve())

        # 检查是否已存在
        for i, entry in enumerate(self._entries):
            if entry.path == path:
                # 更新现有记录
                entry.last_opened = datetime.now().isoformat()
                entry.open_count += 1
                # 移到最前面
                self._entries.pop(i)
                self._entries.insert(0, entry)
                self._save()
                return

        # 创建新记录
        name = Path(path).name
        entry = HistoryEntry(
            path=path,
            name=name,
            last_opened=datetime.now().isoformat(),
            open_count=1
        )

        # 添加到开头
        self._entries.insert(0, entry)

        # 限制数量
        if len(self._entries) > self.MAX_HISTORY:
            self._entries = self._entries[:self.MAX_HISTORY]

        self._save()

    def remove(self, path: str) -> bool:
        """
        从历史记录中移除

        Args:
            path: 数据库路径

        Returns:
            移除成功返回 True
        """
        path = str(Path(path).resolve())

        for i, entry in enumerate(self._entries):
            if entry.path == path:
                self._entries.pop(i)
                self._save()
                return True

        return False

    def clear(self) -> None:
        """清空历史记录"""
        self._entries.clear()
        self._save()

    def get_all(self) -> List[HistoryEntry]:
        """获取所有历史记录"""
        return self._entries.copy()

    def get_recent(self, count: int = 10) -> List[HistoryEntry]:
        """
        获取最近的历史记录

        Args:
            count: 数量

        Returns:
            最近的记录列表
        """
        return self._entries[:count]

    def get_by_path(self, path: str) -> Optional[HistoryEntry]:
        """
        根据路径获取记录

        Args:
            path: 数据库路径

        Returns:
            找到返回记录，否则返回 None
        """
        path = str(Path(path).resolve())

        for entry in self._entries:
            if entry.path == path:
                return entry

        return None

    def exists(self, path: str) -> bool:
        """
        检查路径是否在历史记录中

        Args:
            path: 数据库路径

        Returns:
            存在返回 True
        """
        return self.get_by_path(path) is not None

    def count(self) -> int:
        """获取历史记录数量"""
        return len(self._entries)
