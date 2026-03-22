"""
主窗口模块

提供应用程序主窗口界面。
"""

import sys
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QLabel,
    QMenu,
    QDockWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

from core import LMDBAdapter, LMDBError
from core.base import KeyValueItem
from config.history import DatabaseHistory
from utils.export import DataExporter, ExportError
from .database_view import DatabaseView
from .data_viewer import DataViewer
from .search_panel import SearchPanel
from .stats_panel import StatsPanel
from .styles import get_full_stylesheet


class MainWindow(QMainWindow):
    """应用程序主窗口"""

    database_opened = pyqtSignal(str)
    database_closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._adapter: Optional[LMDBAdapter] = None
        self._db_path: str = ""
        self._history = DatabaseHistory()

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_docks()
        self._connect_signals()
        self._update_history_menu()

        self.setWindowTitle("DataViewer")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)

        self.setStyleSheet(get_full_stylesheet())

    def _setup_ui(self) -> None:
        """设置 UI 布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 1, 1, 1)
        layout.setSpacing(0)

        # 搜索面板
        self._search_panel = SearchPanel()
        layout.addWidget(self._search_panel)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter, 1)

        # 数据库视图
        self._database_view = DatabaseView()
        splitter.addWidget(self._database_view)

        # 数据查看器
        self._data_viewer = DataViewer()
        splitter.addWidget(self._data_viewer)

        splitter.setSizes([500, 200])

    def _setup_menu(self) -> None:
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Database...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_database)
        file_menu.addAction(open_action)

        # 最近打开
        self._recent_menu = file_menu.addMenu("Recent")
        file_menu.addSeparator()

        close_action = QAction("&Close Database", self)
        close_action.triggered.connect(self._on_close_database)
        close_action.setEnabled(False)
        self._close_action = close_action
        file_menu.addAction(close_action)

        file_menu.addSeparator()

        # 导出菜单
        export_menu = file_menu.addMenu("&Export")

        export_json_action = QAction("Export as &JSON...", self)
        export_json_action.triggered.connect(lambda: self._on_export(DataExporter.Format.JSON))
        export_json_action.setEnabled(False)
        self._export_json_action = export_json_action
        export_menu.addAction(export_json_action)

        export_csv_action = QAction("Export as &CSV...", self)
        export_csv_action.triggered.connect(lambda: self._on_export(DataExporter.Format.CSV))
        export_csv_action.setEnabled(False)
        self._export_csv_action = export_csv_action
        export_menu.addAction(export_csv_action)

        export_txt_action = QAction("Export as &TXT...", self)
        export_txt_action.triggered.connect(lambda: self._on_export(DataExporter.Format.TXT))
        export_txt_action.setEnabled(False)
        self._export_txt_action = export_txt_action
        export_menu.addAction(export_txt_action)

        file_menu.addSeparator()

        clear_history_action = QAction("Clear &History", self)
        clear_history_action.triggered.connect(self._on_clear_history)
        file_menu.addAction(clear_history_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 视图菜单
        view_menu = menubar.addMenu("&View")

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self._on_refresh)
        self._refresh_action = refresh_action
        view_menu.addAction(refresh_action)

        view_menu.addSeparator()

        stats_action = QAction("&Statistics", self)
        stats_action.triggered.connect(self._toggle_stats_panel)
        view_menu.addAction(stats_action)

        # 帮助菜单
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """设置工具栏"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)

        open_btn = QAction("Open", self)
        open_btn.setToolTip("Open Database")
        open_btn.triggered.connect(self._on_open_database)
        toolbar.addAction(open_btn)

        self._refresh_btn = QAction("Refresh", self)
        self._refresh_btn.setToolTip("Refresh Data")
        self._refresh_btn.triggered.connect(self._on_refresh)
        self._refresh_btn.setEnabled(False)
        toolbar.addAction(self._refresh_btn)

        export_btn = QAction("Export", self)
        export_btn.setToolTip("Export Data")
        export_btn.triggered.connect(lambda: self._on_export(DataExporter.Format.JSON))
        export_btn.setEnabled(False)
        self._export_btn = export_btn
        toolbar.addAction(export_btn)

    def _setup_statusbar(self) -> None:
        """设置状态栏"""
        self._statusbar = self.statusBar()
        self.setStatusBar(self._statusbar)

        self._status_label = QLabel("No database opened")
        self._statusbar.addWidget(self._status_label, 1)

        self._count_label = QLabel("Entries: 0")
        self._statusbar.addPermanentWidget(self._count_label)

    def _setup_docks(self) -> None:
        """设置停靠窗口"""
        # 统计面板
        self._stats_panel = StatsPanel()
        stats_dock = QDockWidget("Statistics", self)
        stats_dock.setWidget(self._stats_panel)
        stats_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, stats_dock)
        self._stats_dock = stats_dock

    def _connect_signals(self) -> None:
        """连接信号"""
        self._search_panel.search_requested.connect(self._on_search)
        self._search_panel.clear_requested.connect(self._on_clear_search)
        self._database_view.item_selected.connect(self._on_item_selected)

    def _update_history_menu(self) -> None:
        """更新历史记录菜单"""
        self._recent_menu.clear()

        recent = self._history.get_recent(10)
        if not recent:
            empty_action = QAction("(Empty)", self)
            empty_action.setEnabled(False)
            self._recent_menu.addAction(empty_action)
        else:
            for entry in recent:
                action = QAction(entry.name, self)
                action.setToolTip(entry.path)
                action.triggered.connect(lambda checked=entry.path: self._open_database_path(entry.path))
                self._recent_menu.addAction(action)

    def _on_open_database(self) -> None:
        """打开数据库"""
        path = QFileDialog.getExistingDirectory(
            self,
            "Open LMDB Database",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if path:
            self._open_database_path(path)

    def _open_database_path(self, path: str) -> None:
        """打开指定路径的数据库"""
        try:
            self._adapter = LMDBAdapter()
            self._adapter.connect(path, read_only=True)
            self._db_path = path

            # 添加到历史记录
            self._history.add(path)
            self._update_history_menu()

            # 加载数据
            self._load_data()

            # 加载统计信息
            stats = self._adapter.get_stats()
            self._stats_panel.set_stats(stats)

            # 更新 UI 状态
            self._update_ui_state(True)

            self.database_opened.emit(path)
            self._status_label.setText(f"Opened: {path}")

        except LMDBError as e:
            QMessageBox.critical(self, "Error", f"Failed to open database:\n{e}")

    def _on_close_database(self) -> None:
        """关闭数据库"""
        if self._adapter:
            self._adapter.disconnect()
            self._adapter = None

        self._db_path = ""
        self._database_view.clear()
        self._data_viewer.clear()
        self._stats_panel.clear()

        self._update_ui_state(False)
        self.database_closed.emit()
        self._status_label.setText("No database opened")

    def _load_data(self) -> None:
        """加载数据"""
        if not self._adapter:
            return

        items = list(self._adapter.iter_items())
        self._database_view.set_data(items)

        count = len(items)
        self._count_label.setText(f"Entries: {count}")

    def _update_ui_state(self, has_database: bool) -> None:
        """更新 UI 状态"""
        self._close_action.setEnabled(has_database)
        self._refresh_btn.setEnabled(has_database)
        self._refresh_action.setEnabled(has_database)
        self._export_btn.setEnabled(has_database)
        self._export_json_action.setEnabled(has_database)
        self._export_csv_action.setEnabled(has_database)
        self._export_txt_action.setEnabled(has_database)
        self._search_panel.set_enabled(has_database)

    def _on_refresh(self) -> None:
        """刷新数据"""
        self._load_data()
        if self._adapter:
            stats = self._adapter.get_stats()
            self._stats_panel.set_stats(stats)
        self._status_label.setText("Data refreshed")

    def _on_export(self, format_type: str) -> None:
        """导出数据"""
        if not self._adapter:
            return

        # 获取导出文件路径
        ext_map = {
            DataExporter.Format.JSON: "json",
            DataExporter.Format.CSV: "csv",
            DataExporter.Format.TXT: "txt",
        }
        ext = ext_map.get(format_type, "txt")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            f"export.{ext}",
            f"{format_type.upper()} Files (*.{ext})"
        )

        if not file_path:
            return

        try:
            items = list(self._adapter.iter_items())
            DataExporter.export(items, file_path, format_type)
            self._status_label.setText(f"Exported to: {file_path}")
            QMessageBox.information(self, "Export", f"Data exported successfully to:\n{file_path}")
        except ExportError as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _on_clear_history(self) -> None:
        """清空历史记录"""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._history.clear()
            self._update_history_menu()
            self._status_label.setText("History cleared")

    def _toggle_stats_panel(self) -> None:
        """切换统计面板"""
        self._stats_dock.setVisible(not self._stats_dock.isVisible())

    def _on_search(self, pattern: str, search_type: str, use_regex: bool) -> None:
        """搜索"""
        if not self._adapter:
            return

        try:
            if search_type == "key":
                results = self._adapter.search_keys(pattern, regex=use_regex)
                filtered_items = []
                for key in results:
                    value = self._adapter.get_value(key)
                    if value is not None:
                        filtered_items.append(KeyValueItem(
                            key=key,
                            value=value,
                            key_size=len(key),
                            value_size=len(value)
                        ))
            else:
                results = self._adapter.search_values(pattern, regex=use_regex)
                filtered_items = [
                    KeyValueItem(
                        key=k,
                        value=v,
                        key_size=len(k),
                        value_size=len(v)
                    )
                    for k, v in results
                ]

            self._database_view.set_data(filtered_items)
            self._count_label.setText(f"Found: {len(filtered_items)}")
            self._status_label.setText(f"Search completed: {len(filtered_items)} results")

        except Exception as e:
            QMessageBox.warning(self, "Search Error", f"Search failed:\n{e}")

    def _on_clear_search(self) -> None:
        """清除搜索"""
        self._load_data()
        self._status_label.setText("Search cleared")

    def _on_item_selected(self, item) -> None:
        """选中项改变"""
        self._data_viewer.set_data(item.key, item.value)

    def _on_about(self) -> None:
        """关于对话框"""
        QMessageBox.about(
            self,
            "About DataViewer",
            "DataViewer - Database Data Viewer\n\n"
            "Version: 0.2.0\n\n"
            "A cross-platform database viewer for developers.\n\n"
            "Features:\n"
            "- LMDB database support\n"
            "- Multi-format data viewing (Text, Hex, JSON, MsgPack)\n"
            "- Search by key or value (with regex support)\n"
            "- Data export (JSON, CSV, TXT)\n"
            "- Database history\n\n"
            "Built with Python and PyQt6"
        )

    def closeEvent(self, event) -> None:
        """窗口关闭事件"""
        if self._adapter:
            self._adapter.disconnect()
        event.accept()


def run_app() -> int:
    """运行应用程序"""
    app = QApplication(sys.argv)
    app.setApplicationName("DataViewer")
    app.setApplicationVersion("0.2.0")

    window = MainWindow()
    window.show()

    return app.exec()
