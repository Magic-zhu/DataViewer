"""
UI 样式定义

定义应用程序的样式表 - 暗色主题
"""

STYLES = {
    'main_window': """
        QMainWindow {
            background-color: #1e1e1e;
        }
    """,

    'toolbar': """
        QToolBar {
            background-color: #2d2d2d;
            border-bottom: 1px solid #3d3d3d;
            spacing: 5px;
            padding: 5px;
        }
        QToolBar QToolButton {
            padding: 5px;
            border-radius: 3px;
            border: none;
            color: #e0e0e0;
        }
        QToolBar QToolButton:hover {
            background-color: #3d3d3d;
        }
        QToolBar QToolButton:pressed {
            background-color: #4d4d4d;
        }
    """,

    'table': """
        QTableView {
            background-color: #1e1e1e;
            gridline-color: #3d3d3d;
            border: none;
            selection-background-color: #094771;
            selection-color: #ffffff;
            color: #e0e0e0;
        }
        QTableView::item {
            padding: 5px;
            color: #e0e0e0;
        }
        QTableView::item:selected {
            background-color: #094771;
            color: #ffffff;
        }
        QTableView::item:hover {
            background-color: #2d2d2d;
        }
        QHeaderView::section {
            background-color: #2d2d2d;
            padding: 5px;
            border: none;
            border-right: 1px solid #3d3d3d;
            border-bottom: 1px solid #3d3d3d;
            font-weight: bold;
            color: #e0e0e0;
        }
        QHeaderView {
            background-color: #2d2d2d;
        }
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background-color: #4d4d4d;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #5d5d5d;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 12px;
        }
        QScrollBar::handle:horizontal {
            background-color: #4d4d4d;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #5d5d5d;
        }
    """,

    'text_edit': """
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            font-family: Consolas, 'Courier New', monospace;
            font-size: 12px;
            color: #e0e0e0;
        }
    """,

    'search_panel': """
        QWidget#searchPanel {
            background-color: #2d2d2d;
            border-bottom: 1px solid #3d3d3d;
        }
        QLabel {
            color: #e0e0e0;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QLineEdit:focus {
            border: 1px solid #0078d4;
        }
        QComboBox {
            padding: 5px;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QComboBox:hover {
            border: 1px solid #4d4d4d;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            color: #e0e0e0;
            selection-background-color: #094771;
        }
        QCheckBox {
            color: #e0e0e0;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            background-color: #1e1e1e;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #0078d4;
        }
    """,

    'button_primary': """
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 5px 15px;
            min-width: 60px;
        }
        QPushButton:hover {
            background-color: #1084d8;
        }
        QPushButton:pressed {
            background-color: #006cbd;
        }
        QPushButton:disabled {
            background-color: #4d4d4d;
            color: #808080;
        }
    """,

    'button_secondary': """
        QPushButton {
            background-color: #3d3d3d;
            color: #e0e0e0;
            border: 1px solid #4d4d4d;
            border-radius: 3px;
            padding: 5px 15px;
            min-width: 60px;
        }
        QPushButton:hover {
            background-color: #4d4d4d;
            border: 1px solid #5d5d5d;
        }
        QPushButton:pressed {
            background-color: #5d5d5d;
        }
        QPushButton:disabled {
            background-color: #2d2d2d;
            color: #606060;
        }
    """,

    'status_bar': """
        QStatusBar {
            background-color: #2d2d2d;
            border-top: 1px solid #3d3d3d;
            color: #e0e0e0;
        }
        QStatusBar QLabel {
            color: #b0b0b0;
        }
    """,

    'splitter': """
        QSplitter {
            background-color: #1e1e1e;
        }
        QSplitter::handle {
            background-color: #3d3d3d;
        }
        QSplitter::handle:horizontal {
            width: 2px;
        }
        QSplitter::handle:vertical {
            height: 2px;
        }
        QSplitter::handle:hover {
            background-color: #0078d4;
        }
    """,

    'menu': """
        QMenuBar {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border-bottom: 1px solid #3d3d3d;
        }
        QMenuBar::item {
            padding: 5px 10px;
        }
        QMenuBar::item:selected {
            background-color: #3d3d3d;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
        }
        QMenu::item {
            padding: 5px 30px 5px 20px;
        }
        QMenu::item:selected {
            background-color: #094771;
        }
        QMenu::separator {
            height: 1px;
            background-color: #3d3d3d;
            margin: 5px 10px;
        }
    """,

    'label': """
        QLabel {
            color: #e0e0e0;
            background-color: transparent;
        }
    """,

    'spinbox': """
        QSpinBox {
            background-color: #1e1e1e;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            padding: 3px;
            color: #e0e0e0;
        }
        QSpinBox:focus {
            border: 1px solid #0078d4;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #3d3d3d;
            border: none;
            width: 16px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #4d4d4d;
        }
    """,

    'combobox': """
        QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            padding: 5px;
            color: #e0e0e0;
        }
        QComboBox:hover {
            border: 1px solid #4d4d4d;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            color: #e0e0e0;
            selection-background-color: #094771;
            border: 1px solid #3d3d3d;
        }
    """,
}


def get_stylesheet(*names: str) -> str:
    """获取指定组件的样式表"""
    styles = []
    for name in names:
        if name in STYLES:
            styles.append(STYLES[name])
    return '\n'.join(styles)


def get_full_stylesheet() -> str:
    """获取完整样式表"""
    return '\n'.join(STYLES.values())
