#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DataViewer - Database Data Viewer

Main entry point for the application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("DataViewer")
    app.setApplicationVersion("0.1.1")
    app.setOrganizationName("DataViewer")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
