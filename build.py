#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DataViewer Build Script

Builds the application for distribution.

Usage:
    python build.py              # Build for current platform
    python build.py --clean      # Clean build artifacts first
    python build.py --debug      # Build with console window (debug mode)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.resolve()


def clean_build():
    """Remove build artifacts."""
    project_root = get_project_root()
    dirs_to_remove = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_remove:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"Removing {dir_path}...")
            shutil.rmtree(dir_path)
    
    # Remove .pyc files
    for pyc_file in project_root.rglob('*.pyc'):
        pyc_file.unlink()
    
    # Remove spec file if exists (will regenerate)
    spec_file = project_root / 'dataviewer.spec'
    if spec_file.exists():
        # Keep the spec file if it's custom
        pass
    
    print("Clean complete.")


def build_pyinstaller(debug: bool = False):
    """Build the application using PyInstaller."""
    project_root = get_project_root()
    
    # Change to project directory
    os.chdir(project_root)
    
    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', 'DataViewer',
        '--onefile',
        '--windowed' if not debug else '--console',
        '--clean',
        '--noconfirm',
    ]
    
    # Add hidden imports
    hidden_imports = [
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'lmdb',
        'msgpack',
        'pyperclip',
    ]
    
    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])
    
    # Add excludes
    excludes = [
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ]
    
    for exc in excludes:
        cmd.extend(['--exclude-module', exc])
    
    # Platform-specific options
    if platform.system() == 'Darwin':
        # macOS specific
        cmd.extend(['--osx-bundle-identifier', 'com.dataviewer.app'])
    
    # Add main script
    cmd.append('main.py')
    
    print(f"Building with command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print(f"Build failed with code {result.returncode}")
        sys.exit(1)
    
    print("Build complete!")
    
    # Output location
    dist_dir = project_root / 'dist'
    if dist_dir.exists():
        print(f"Output directory: {dist_dir}")
        for f in dist_dir.iterdir():
            print(f"  - {f.name}")


def build_with_spec():
    """Build using the spec file."""
    project_root = get_project_root()
    spec_file = project_root / 'dataviewer.spec'
    
    if not spec_file.exists():
        print("Spec file not found. Creating one...")
        build_pyinstaller()
        return
    
    os.chdir(project_root)
    
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', str(spec_file)]
    
    print(f"Building with spec file: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print(f"Build failed with code {result.returncode}")
        sys.exit(1)
    
    print("Build complete!")


def main():
    parser = argparse.ArgumentParser(description='Build DataViewer')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts first')
    parser.add_argument('--debug', action='store_true', help='Build with console window')
    parser.add_argument('--spec', action='store_true', help='Use spec file if available')
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
    
    if args.spec:
        build_with_spec()
    else:
        build_pyinstaller(debug=args.debug)


if __name__ == '__main__':
    main()
