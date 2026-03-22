"""
数据导出模块

支持将数据导出为 JSON、CSV、TXT 格式。
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from core.base import KeyValueItem
from core import try_decode_text


class DataExporter:
    """
    数据导出器

    支持多种格式的数据导出。
    """

    class Format:
        JSON = "json"
        CSV = "csv"
        TXT = "txt"

    @staticmethod
    def export(
        items: List[KeyValueItem],
        file_path: str,
        format_type: str = Format.JSON,
        encoding: str = "utf-8"
    ) -> bool:
        """
        导出数据到文件

        Args:
            items: 要导出的数据项列表
            file_path: 目标文件路径
            format_type: 导出格式 (json, csv, txt)
            encoding: 文件编码

        Returns:
            导出成功返回 True
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            if format_type == DataExporter.Format.JSON:
                return DataExporter._export_json(items, path, encoding)
            elif format_type == DataExporter.Format.CSV:
                return DataExporter._export_csv(items, path, encoding)
            elif format_type == DataExporter.Format.TXT:
                return DataExporter._export_txt(items, path, encoding)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

        except Exception as e:
            raise ExportError(f"Export failed: {e}")

    @staticmethod
    def _export_json(items: List[KeyValueItem], path: Path, encoding: str) -> bool:
        """导出为 JSON 格式"""
        data = []
        for item in items:
            key_text, _ = try_decode_text(item.key)
            value_text, _ = try_decode_text(item.value)

            data.append({
                "key": key_text,
                "key_hex": item.key.hex(),
                "value": value_text,
                "value_hex": item.value.hex(),
                "key_size": item.key_size,
                "value_size": item.value_size,
            })

        with open(path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    @staticmethod
    def _export_csv(items: List[KeyValueItem], path: Path, encoding: str) -> bool:
        """导出为 CSV 格式"""
        with open(path, 'w', encoding=encoding, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Key', 'Value', 'Key Size', 'Value Size'])

            for item in items:
                key_text, _ = try_decode_text(item.key)
                value_text, _ = try_decode_text(item.value)
                writer.writerow([key_text, value_text, item.key_size, item.value_size])

        return True

    @staticmethod
    def _export_txt(items: List[KeyValueItem], path: Path, encoding: str) -> bool:
        """导出为 TXT 格式"""
        with open(path, 'w', encoding=encoding) as f:
            f.write(f"# DataViewer Export\n")
            f.write(f"# Date: {datetime.now().isoformat()}\n")
            f.write(f"# Total entries: {len(items)}\n")
            f.write("#" + "=" * 60 + "\n\n")

            for i, item in enumerate(items, 1):
                key_text, _ = try_decode_text(item.key)
                value_text, _ = try_decode_text(item.value)

                f.write(f"[Entry {i}]\n")
                f.write(f"Key: {key_text}\n")
                f.write(f"Value: {value_text}\n")
                f.write(f"Key Size: {item.key_size} bytes\n")
                f.write(f"Value Size: {item.value_size} bytes\n")
                f.write("-" * 40 + "\n\n")

        return True

    @staticmethod
    def export_to_clipboard(items: List[KeyValueItem], format_type: str = Format.JSON) -> str:
        """
        导出数据到剪贴板

        Args:
            items: 要导出的数据项列表
            format_type: 导出格式

        Returns:
            导出的字符串
        """
        if format_type == DataExporter.Format.JSON:
            data = []
            for item in items:
                key_text, _ = try_decode_text(item.key)
                value_text, _ = try_decode_text(item.value)
                data.append({"key": key_text, "value": value_text})
            return json.dumps(data, indent=2, ensure_ascii=False)

        elif format_type == DataExporter.Format.CSV:
            lines = ['Key,Value']
            for item in items:
                key_text, _ = try_decode_text(item.key)
                value_text, _ = try_decode_text(item.value)
                # 处理 CSV 特殊字符
                key_text = key_text.replace('"', '""')
                value_text = value_text.replace('"', '""')
                lines.append(f'"{key_text}","{value_text}"')
            return '\n'.join(lines)

        else:  # TXT
            lines = []
            for i, item in enumerate(items, 1):
                key_text, _ = try_decode_text(item.key)
                value_text, _ = try_decode_text(item.value)
                lines.append(f"[{i}] {key_text} = {value_text}")
            return '\n'.join(lines)


class ExportError(Exception):
    """导出错误"""
    pass
