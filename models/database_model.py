"""
数据库表格模型

提供 Qt 表格视图的数据模型，支持分页加载。
"""

from typing import Any, List, Optional

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal

from core.base import KeyValueItem


class DatabaseModel(QAbstractTableModel):
    """
    数据库键值对表格模型

    提供 QTableView 显示的数据模型，支持分页加载。
    """

    HEADERS = ["Key", "Value", "Key Size", "Value Size"]

    data_loaded = pyqtSignal(int)  # 加载完成信号，参数为加载的条目数
    loading_changed = pyqtSignal(bool)  # 加载状态变化信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[KeyValueItem] = []
        self._display_data: List[KeyValueItem] = []
        self._total_count: int = 0
        self._page_size: int = 100
        self._current_page: int = 0
        self._is_loading: bool = False

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._display_data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 4

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or index.row() >= len(self._display_data):
            return None

        item = self._display_data[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            col = index.column()
            if col == 0:
                return self._format_key(item.key)
            elif col == 1:
                return self._format_value(item.value)
            elif col == 2:
                return f"{item.key_size} B"
            elif col == 3:
                return f"{item.value_size} B"

        elif role == Qt.ItemDataRole.UserRole:
            return item

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            col = index.column()
            if col in (2, 3):
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.HEADERS[section]
        return None

    def set_data(self, items: List[KeyValueItem]) -> None:
        """设置数据"""
        self.beginResetModel()
        self._display_data = items
        self._data = items
        self._total_count = len(items)
        self.endResetModel()
        self.data_loaded.emit(len(items))

    def set_page_data(self, items: List[KeyValueItem], total_count: int, page: int) -> None:
        """设置分页数据"""
        self.beginResetModel()
        self._display_data = items
        self._total_count = total_count
        self._current_page = page
        self.endResetModel()
        self.data_loaded.emit(len(items))

    def clear(self) -> None:
        """清空数据"""
        self.beginResetModel()
        self._data = []
        self._display_data = []
        self._total_count = 0
        self._current_page = 0
        self.endResetModel()

    def get_item(self, row: int) -> Optional[KeyValueItem]:
        """获取指定行的数据项"""
        if 0 <= row < len(self._display_data):
            return self._display_data[row]
        return None

    def get_total_count(self) -> int:
        """获取总条目数"""
        return self._total_count

    def get_page_count(self) -> int:
        """获取总页数"""
        if self._page_size <= 0:
            return 1
        return (self._total_count + self._page_size - 1) // self._page_size

    def get_current_page(self) -> int:
        """获取当前页码"""
        return self._current_page

    def get_page_size(self) -> int:
        """获取每页大小"""
        return self._page_size

    def set_page_size(self, size: int) -> None:
        """设置每页大小"""
        self._page_size = max(1, size)

    def is_loading(self) -> bool:
        """是否正在加载"""
        return self._is_loading

    def set_loading(self, loading: bool) -> None:
        """设置加载状态"""
        if self._is_loading != loading:
            self._is_loading = loading
            self.loading_changed.emit(loading)

    def _format_key(self, key: bytes) -> str:
        """格式化键显示"""
        try:
            decoded = key.decode('utf-8')
            if decoded.isprintable():
                return decoded
        except UnicodeDecodeError:
            pass
        return key.hex()[:50] + ("..." if len(key.hex()) > 50 else "")

    def _format_value(self, value: bytes) -> str:
        """格式化值显示"""
        try:
            decoded = value.decode('utf-8')
            if decoded.isprintable() or '\n' in decoded or '\t' in decoded:
                preview = decoded[:100]
                return preview + ("..." if len(decoded) > 100 else "")
        except UnicodeDecodeError:
            pass
        hex_str = value.hex()
        return hex_str[:50] + ("..." if len(hex_str) > 50 else "")

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """排序"""
        self.beginResetModel()

        if column == 0:
            self._display_data.sort(key=lambda x: x.key, reverse=(order == Qt.SortOrder.DescendingOrder))
        elif column == 1:
            self._display_data.sort(key=lambda x: x.value, reverse=(order == Qt.SortOrder.DescendingOrder))
        elif column == 2:
            self._display_data.sort(key=lambda x: x.key_size, reverse=(order == Qt.SortOrder.DescendingOrder))
        elif column == 3:
            self._display_data.sort(key=lambda x: x.value_size, reverse=(order == Qt.SortOrder.DescendingOrder))

        self.endResetModel()
