"""
搜索面板模块

提供搜索功能的 UI 组件。
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QComboBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal


class SearchPanel(QWidget):
    """
    搜索面板组件

    提供按键搜索和按值搜索功能。
    """

    search_requested = pyqtSignal(str, str, bool)  # 搜索请求信号 (模式, pattern, 是否正则)
    clear_requested = pyqtSignal()  # 清除搜索信号

    def __init__(self, parent=None):
        super().__init__(parent)

        self._adapter = None
        self._search_callback = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("searchPanel")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Search label
        search_label = QLabel("Search:")
        layout.addWidget(search_label)

        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Enter search pattern...")
        self._search_input.setMinimumWidth(200)
        self._search_input.setMaximumWidth(400)
        self._search_input.returnPressed.connect(self._on_search)
        layout.addWidget(self._search_input, 1)

        # Search type combo
        self._search_type = QComboBox()
        self._search_type.addItems(["By Key", "By Value"])
        self._search_type.setCurrentIndex(0)
        layout.addWidget(self._search_type)

        # Regex checkbox
        self._regex_checkbox = QCheckBox("Regex")
        layout.addWidget(self._regex_checkbox)

        # Search button
        self._search_btn = QPushButton("Search")
        self._search_btn.clicked.connect(self._on_search)
        layout.addWidget(self._search_btn)

        # Clear button
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self._on_clear)
        layout.addWidget(self._clear_btn)

        # Result label
        self._result_label = QLabel("")
        layout.addWidget(self._result_label)

        layout.addStretch()

    def set_enabled(self, enabled: bool) -> None:
        """设置启用状态"""
        self._search_input.setEnabled(enabled)
        self._search_type.setEnabled(enabled)
        self._regex_checkbox.setEnabled(enabled)
        self._search_btn.setEnabled(enabled)
        self._clear_btn.setEnabled(enabled)

    def set_search_callback(self, callback) -> None:
        """设置搜索回调函数"""
        self._search_callback = callback

    def set_database_adapter(self, adapter) -> None:
        """设置数据库适配器"""
        self._adapter = adapter

    def get_search_type(self) -> str:
        """获取搜索类型"""
        return "key" if self._search_type.currentIndex() == 0 else "value"

    def is_regex_enabled(self) -> bool:
        """是否启用正则表达式"""
        return self._regex_checkbox.isChecked()

    def _on_search(self) -> None:
        """执行搜索"""
        pattern = self._search_input.text().strip()
        if not pattern:
            self._show_result("Please enter search pattern")
            return

        search_type = self.get_search_type()
        use_regex = self._regex_checkbox.isChecked()

        # 发射信号，让主窗口处理搜索
        self.search_requested.emit(pattern, search_type, use_regex)

    def _on_clear(self) -> None:
        """清除搜索"""
        self._search_input.clear()
        self._regex_checkbox.setChecked(False)
        self._show_result("")
        self.clear_requested.emit()

    def _show_result(self, message: str) -> None:
        """显示结果"""
        self._result_label.setText(message)

    def keyPressEvent(self, event) -> None:
        """键盘事件"""
        if event.key() == Qt.Key.Key_Return:
            self._on_search()
