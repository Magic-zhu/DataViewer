"""
统计信息面板模块

显示数据库的统计信息。
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout,
    QFrame,
)
from PyQt6.QtCore import Qt

from core.base import DatabaseStats
from core import format_size


class StatsPanel(QWidget):
    """
    统计信息面板

    显示数据库的各种统计信息。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stats: Optional[DatabaseStats] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 基本信息
        basic_group = QGroupBox("Basic Information")
        basic_layout = QGridLayout(basic_group)

        self._path_label = self._create_info_label()
        self._mode_label = self._create_info_label()
        self._entries_label = self._create_info_label()
        self._size_label = self._create_info_label()

        basic_layout.addWidget(QLabel("Path:"), 0, 0)
        basic_layout.addWidget(self._path_label, 0, 1)
        basic_layout.addWidget(QLabel("Mode:"), 1, 0)
        basic_layout.addWidget(self._mode_label, 1, 1)
        basic_layout.addWidget(QLabel("Entries:"), 2, 0)
        basic_layout.addWidget(self._entries_label, 2, 1)
        basic_layout.addWidget(QLabel("Size:"), 3, 0)
        basic_layout.addWidget(self._size_label, 3, 1)

        basic_layout.setColumnStretch(1, 1)
        layout.addWidget(basic_group)

        # 键统计
        key_group = QGroupBox("Key Statistics")
        key_layout = QGridLayout(key_group)

        self._key_total_label = self._create_info_label()
        self._key_avg_label = self._create_info_label()
        self._key_max_label = self._create_info_label()
        self._key_min_label = self._create_info_label()

        key_layout.addWidget(QLabel("Total:"), 0, 0)
        key_layout.addWidget(self._key_total_label, 0, 1)
        key_layout.addWidget(QLabel("Average:"), 1, 0)
        key_layout.addWidget(self._key_avg_label, 1, 1)
        key_layout.addWidget(QLabel("Maximum:"), 2, 0)
        key_layout.addWidget(self._key_max_label, 2, 1)
        key_layout.addWidget(QLabel("Minimum:"), 3, 0)
        key_layout.addWidget(self._key_min_label, 3, 1)

        key_layout.setColumnStretch(1, 1)
        layout.addWidget(key_group)

        # 值统计
        value_group = QGroupBox("Value Statistics")
        value_layout = QGridLayout(value_group)

        self._value_total_label = self._create_info_label()
        self._value_avg_label = self._create_info_label()
        self._value_max_label = self._create_info_label()
        self._value_min_label = self._create_info_label()

        value_layout.addWidget(QLabel("Total:"), 0, 0)
        value_layout.addWidget(self._value_total_label, 0, 1)
        value_layout.addWidget(QLabel("Average:"), 1, 0)
        value_layout.addWidget(self._value_avg_label, 1, 1)
        value_layout.addWidget(QLabel("Maximum:"), 2, 0)
        value_layout.addWidget(self._value_max_label, 2, 1)
        value_layout.addWidget(QLabel("Minimum:"), 3, 0)
        value_layout.addWidget(self._value_min_label, 3, 1)

        value_layout.setColumnStretch(1, 1)
        layout.addWidget(value_group)

        layout.addStretch()

        # 初始状态
        self.clear()

    def _create_info_label(self) -> QLabel:
        """创建信息标签"""
        label = QLabel("-")
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

    def set_stats(self, stats: DatabaseStats) -> None:
        """设置统计信息"""
        self._stats = stats
        self._update_display()

    def clear(self) -> None:
        """清空统计信息"""
        self._stats = None

        self._path_label.setText("-")
        self._mode_label.setText("-")
        self._entries_label.setText("-")
        self._size_label.setText("-")

        self._key_total_label.setText("-")
        self._key_avg_label.setText("-")
        self._key_max_label.setText("-")
        self._key_min_label.setText("-")

        self._value_total_label.setText("-")
        self._value_avg_label.setText("-")
        self._value_max_label.setText("-")
        self._value_min_label.setText("-")

    def _update_display(self) -> None:
        """更新显示"""
        if not self._stats:
            return

        stats = self._stats

        # 基本信息
        self._path_label.setText(stats.db_path or "-")
        self._path_label.setToolTip(stats.db_path or "")
        self._mode_label.setText("Read Only" if stats.read_only else "Read/Write")
        self._entries_label.setText(f"{stats.total_entries:,}")
        self._size_label.setText(format_size(stats.total_size))

        # 键统计
        self._key_total_label.setText(format_size(stats.key_size_total))
        self._key_avg_label.setText(f"{stats.avg_key_size:.1f} B")
        self._key_max_label.setText(f"{stats.max_key_size:,} B")
        self._key_min_label.setText(f"{stats.min_key_size:,} B")

        # 值统计
        self._value_total_label.setText(format_size(stats.value_size_total))
        self._value_avg_label.setText(f"{stats.avg_value_size:.1f} B")
        self._value_max_label.setText(f"{stats.max_value_size:,} B")
        self._value_min_label.setText(f"{stats.min_value_size:,} B")
