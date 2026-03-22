"""
数据查看器模块

显示选中键值对的详细内容。
"""

import json
import re
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QMessageBox,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QSyntaxHighlighter, QTextDocument

from core import (
    try_decode_text,
    try_parse_json,
    try_parse_msgpack,
    format_size,
    HAS_MSGPACK,
)
from .styles import get_stylesheet


def highlight_json(data) -> str:
    """将 JSON 数据转换为带语法高亮的 HTML"""
    text = json.dumps(data, indent=2, ensure_ascii=False)

    # 转义 HTML 特殊字符
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # 颜色定义 (暗色主题)
    colors = {
        'string': '#98c379',    # 绿色 - 字符串
        'number': '#d19a66',    # 橙色 - 数字
        'boolean': '#56b6c2',   # 青色 - 布尔值
        'null': '#e06c75',      # 红色 - null
        'key': '#e5c07b',       # 黄色 - 键名
        'bracket': '#abb2bf',   # 灰色 - 括号
    }

    result = []
    i = 0
    in_string = False
    is_key = False

    while i < len(text):
        char = text[i]

        # 检测字符串开始/结束
        if char == '"' and (i == 0 or text[i-1] != '\\'):
            if not in_string:
                in_string = True
                # 检查是否是键名（后面紧跟冒号）
                j = i + 1
                while j < len(text) and text[j] != '"':
                    if text[j] == '\\':
                        j += 2
                    else:
                        j += 1
                # 找到字符串结束后的第一个非空白字符
                k = j + 1
                while k < len(text) and text[k] in ' \t\n\r':
                    k += 1
                is_key = k < len(text) and text[k] == ':'

                if is_key:
                    result.append(f'<span style="color:{colors["key"]}">')
                else:
                    result.append(f'<span style="color:{colors["string"]}">')
                result.append(char)
            else:
                result.append(char)
                result.append('</span>')
                in_string = False
            i += 1
            continue

        if in_string:
            result.append(char)
            i += 1
            continue

        # 检测数字
        if char in '-0123456789':
            j = i
            while j < len(text) and text[j] in '-0123456789.eE+':
                j += 1
            result.append(f'<span style="color:{colors["number"]}">{text[i:j]}</span>')
            i = j
            continue

        # 检测布尔值和 null
        if text[i:i+4] == 'true':
            result.append(f'<span style="color:{colors["boolean"]}">true</span>')
            i += 4
            continue
        if text[i:i+5] == 'false':
            result.append(f'<span style="color:{colors["boolean"]}">false</span>')
            i += 5
            continue
        if text[i:i+4] == 'null':
            result.append(f'<span style="color:{colors["null"]}">null</span>')
            i += 4
            continue

        # 括号
        if char in '{}[]':
            result.append(f'<span style="color:{colors["bracket"]}">{char}</span>')
            i += 1
            continue

        result.append(char)
        i += 1

    return ''.join(result)


class DataViewer(QWidget):
    """
    数据查看器组件

    显示选中键值对的详细内容，支持多种视图模式。
    """

    view_mode_changed = pyqtSignal(str)
    data_copied = pyqtSignal()
    data_changed = pyqtSignal()

    class ViewMode:
        TEXT = "text"
        HEX = "hex"
        JSON = "json"
        MSGPACK = "msgpack"

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_key = b""
        self._current_value = b""
        self._current_mode = self.ViewMode.TEXT
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 标题区域
        header_layout = QHBoxLayout()
        self._key_label = QLabel("Key: ")
        self._value_size_label = QLabel("Value Size: 0 B")
        header_layout.addWidget(self._key_label)
        header_layout.addStretch()
        header_layout.addWidget(self._value_size_label)
        layout.addLayout(header_layout)

        # 视图模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("View Mode:"))
        
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Text", "Hex", "JSON", "MsgPack"])
        self._mode_combo.setCurrentIndex(0)
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self._mode_combo)

        mode_layout.addStretch()

        self._copy_btn = QPushButton("Copy")
        self._copy_btn.clicked.connect(self._on_copy)
        mode_layout.addWidget(self._copy_btn)

        layout.addLayout(mode_layout)

        # 内容区域
        self._content_edit = QTextEdit()
        self._content_edit.setReadOnly(True)
        self._content_edit.setStyleSheet(get_stylesheet('text_edit'))
        self._content_edit.setFontFamily("Consolas")
        layout.addWidget(self._content_edit, 1)

        # 状态栏
        status_layout = QHBoxLayout()
        self._status_label = QLabel("No data")
        status_layout.addWidget(self._status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

    def set_data(self, key: bytes, value: bytes) -> None:
        """设置数据"""
        self._current_key = key
        self._current_value = value

        # 更新标签
        try:
            key_text = key.decode('utf-8')
        except UnicodeDecodeError:
            key_text = key.hex()[:50] + ("..." if len(key.hex()) > 50 else "")

        self._key_label.setText(f"Key: {key_text}")
        self._value_size_label.setText(f"Value Size: {format_size(len(value))}")

        # 更新内容
        self._update_content()
        self.data_changed.emit()

    def clear(self) -> None:
        """清空数据"""
        self._current_key = b""
        self._current_value = b""
        self._key_label.setText("Key: ")
        self._value_size_label.setText("Value Size: 0 B")
        self._content_edit.clear()
        self._status_label.setText("No data")

    def _update_content(self) -> None:
        """更新内容显示"""
        if not self._current_value:
            self._content_edit.clear()
            self._status_label.setText("No data")
            return

        try:
            if self._current_mode == self.ViewMode.TEXT:
                text, success = try_decode_text(self._current_value)
                if success:
                    self._content_edit.setPlainText(text)
                    self._status_label.setText(f"Text ({len(self._current_value)} bytes)")
                else:
                    self._content_edit.setPlainText(self._current_value.hex())
                    self._status_label.setText(f"Binary ({len(self._current_value)} bytes)")

            elif self._current_mode == self.ViewMode.HEX:
                hex_content = self._format_hex_display(self._current_value)
                self._content_edit.setPlainText(hex_content)
                self._status_label.setText(f"Hex ({len(self._current_value)} bytes)")

            elif self._current_mode == self.ViewMode.JSON:
                data, success = try_parse_json(self._current_value)
                if success:
                    html = highlight_json(data)
                    self._content_edit.setHtml(f'<pre style="font-family: Consolas; margin: 0;">{html}</pre>')
                    self._status_label.setText(f"JSON ({len(self._current_value)} bytes)")
                else:
                    self._content_edit.setPlainText("Invalid JSON data")
                    self._status_label.setText("Parse failed")

            elif self._current_mode == self.ViewMode.MSGPACK:
                if not HAS_MSGPACK:
                    self._content_edit.setPlainText("MsgPack module not installed")
                    self._status_label.setText("Not available")
                else:
                    data, success = try_parse_msgpack(self._current_value)
                    if success:
                        html = highlight_json(data)
                        self._content_edit.setHtml(f'<pre style="font-family: Consolas; margin: 0;">{html}</pre>')
                        self._status_label.setText(f"MsgPack ({len(self._current_value)} bytes)")
                    else:
                        self._content_edit.setPlainText("Invalid MsgPack data")
                        self._status_label.setText("Parse failed")

        except Exception as e:
            self._content_edit.setPlainText(f"Error: {e}")
            self._status_label.setText("Error")

    def _format_hex_display(self, data: bytes, bytes_per_line: int = 16) -> str:
        """格式化十六进制显示"""
        lines = []
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i + bytes_per_line]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f'{i:08x}  {hex_part:<48s}  |{ascii_part}|')

        if not lines:
            return "(empty)"
        return '\n'.join(lines)

    def _on_mode_changed(self, index: int) -> None:
        """视图模式改变"""
        modes = ["text", "hex", "json", "msgpack"]
        if 0 <= index < len(modes):
            self._current_mode = modes[index]
            self._update_content()
            self.view_mode_changed.emit(modes[index])

    def _on_copy(self) -> None:
        """复制数据"""
        try:
            import pyperclip

            if self._current_mode == self.ViewMode.TEXT:
                text, _ = try_decode_text(self._current_value)
                pyperclip.copy(text)
            elif self._current_mode == self.ViewMode.HEX:
                pyperclip.copy(self._current_value.hex())
            elif self._current_mode in (self.ViewMode.JSON, self.ViewMode.MSGPACK):
                text = self._content_edit.toPlainText()
                pyperclip.copy(text)
            else:
                pyperclip.copy(self._current_value.hex())

            self.data_copied.emit()
            self._status_label.setText("Copied to clipboard")

        except ImportError:
            # pyperclip not installed, use Qt clipboard
            clipboard = QApplication.clipboard()
            if self._current_mode == self.ViewMode.TEXT:
                text, _ = try_decode_text(self._current_value)
                clipboard.setText(text)
            elif self._current_mode == self.ViewMode.HEX:
                clipboard.setText(self._current_value.hex())
            else:
                clipboard.setText(self._content_edit.toPlainText())
            self._status_label.setText("Copied to clipboard")
        except Exception as e:
            QMessageBox.warning(self, "Copy Failed", f"Failed to copy: {e}")
