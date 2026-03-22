"""
数据库视图模块

显示数据库键值对的表格视图。
"""

from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QLabel,
    QPushButton,
    QAbstractItemView,
    QMenu,
    QSpinBox,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.base import KeyValueItem
from models.database_model import DatabaseModel


class DatabaseView(QWidget):
    """
    数据库视图组件

    显示键值对的表格，支持分页、选择、排序。
    """

    item_selected = pyqtSignal(object)
    item_double_clicked = pyqtSignal(object)
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._model = DatabaseModel()
        self._total_count = 0
        self._current_page = 0
        self._page_size = 100

        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 表格视图
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.setSortingEnabled(True)
        self._table.setAlternatingRowColors(True)

        # 设置列宽
        self._table.setColumnWidth(0, 200)
        self._table.setColumnWidth(1, 300)
        self._table.setColumnWidth(2, 80)
        self._table.setColumnWidth(3, 80)

        # 连接信号
        self._table.clicked.connect(self._on_table_clicked)
        self._table.doubleClicked.connect(self._on_table_double_clicked)
        self._table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self._table, 1)

        # 分页控制
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(5, 5, 5, 5)

        self._prev_btn = QPushButton("Previous")
        self._prev_btn.clicked.connect(self._on_prev_page)
        self._prev_btn.setEnabled(False)
        pagination_layout.addWidget(self._prev_btn)

        self._page_label = QLabel("Page 0/0")
        pagination_layout.addWidget(self._page_label)

        self._next_btn = QPushButton("Next")
        self._next_btn.clicked.connect(self._on_next_page)
        self._next_btn.setEnabled(False)
        pagination_layout.addWidget(self._next_btn)

        pagination_layout.addStretch()

        self._page_size_label = QLabel("Page Size:")
        pagination_layout.addWidget(self._page_size_label)

        self._page_size_spin = QSpinBox()
        self._page_size_spin.setRange(10, 500)
        self._page_size_spin.setValue(100)
        self._page_size_spin.valueChanged.connect(self._on_page_size_changed)
        pagination_layout.addWidget(self._page_size_spin)

        layout.addWidget(pagination_widget)

    def set_data(self, items: List[KeyValueItem]) -> None:
        """设置数据"""
        self._model.set_data(items)
        self._total_count = len(items)
        self._current_page = 0
        self._update_pagination()

    def clear(self) -> None:
        """清空数据"""
        self._model.clear()
        self._total_count = 0
        self._current_page = 0
        self._update_pagination()

    def get_selected_item(self) -> Optional[KeyValueItem]:
        """获取选中的项"""
        indexes = self._table.selectionModel().selectedIndexes()
        if indexes:
            return self._model.get_item(indexes[0].row())
        return None

    def _on_table_clicked(self, index) -> None:
        """表格点击事件"""
        item = self._model.get_item(index.row())
        if item:
            self.item_selected.emit(item)

    def _on_table_double_clicked(self, index) -> None:
        """表格双击事件"""
        item = self._model.get_item(index.row())
        if item:
            self.item_double_clicked.emit(item)

    def _show_context_menu(self, pos) -> None:
        """显示上下文菜单"""
        item = self.get_selected_item()
        if not item:
            return

        menu = QMenu(self)

        copy_key_action = menu.addAction("Copy Key")
        copy_key_action.triggered.connect(lambda: self._copy_key(item))

        copy_value_action = menu.addAction("Copy Value")
        copy_value_action.triggered.connect(lambda: self._copy_value(item))

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_key(self, item: KeyValueItem) -> None:
        """复制键"""
        clipboard = QApplication.clipboard()
        try:
            text = item.key.decode('utf-8')
        except UnicodeDecodeError:
            text = item.key.hex()
        clipboard.setText(text)

    def _copy_value(self, item: KeyValueItem) -> None:
        """复制值"""
        clipboard = QApplication.clipboard()
        try:
            text = item.value.decode('utf-8')
        except UnicodeDecodeError:
            text = item.value.hex()
        clipboard.setText(text)

    def _on_prev_page(self) -> None:
        """上一页"""
        if self._current_page > 0:
            self._current_page -= 1
            self._update_pagination()
            self.refresh_requested.emit()

    def _on_next_page(self) -> None:
        """下一页"""
        total_pages = self._get_total_pages()
        if self._current_page < total_pages - 1:
            self._current_page += 1
            self._update_pagination()
            self.refresh_requested.emit()

    def _on_page_size_changed(self, value: int) -> None:
        """页大小改变"""
        self._page_size = value
        self._current_page = 0
        self._update_pagination()

    def _get_total_pages(self) -> int:
        """获取总页数"""
        if self._page_size <= 0:
            return 1
        return (self._total_count + self._page_size - 1) // self._page_size

    def _update_pagination(self) -> None:
        """更新分页控件"""
        total_pages = self._get_total_pages()
        self._page_label.setText(
            f"Page {self._current_page + 1}/{total_pages} "
            f"(Total: {self._total_count} entries)"
        )
        self._prev_btn.setEnabled(self._current_page > 0)
        self._next_btn.setEnabled(self._current_page < total_pages - 1)
