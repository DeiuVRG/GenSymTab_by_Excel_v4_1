#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_exe.py
------------
Script for building standalone .exe for VRG Config & Test Generator GUI.

This creates a single executable that includes:
- ConfigTestGenerator_GUI.py
- GenSymb_ConfigVRG.py
- generate_test_menu_v4.py
- VRG_Logo.ico (if exists)
- All Python dependencies

Usage:
    python build_exe.py

Output:
    dist/ConfigTestGenerator.exe
"""

import subprocess
import sys
from pathlib import Path
import shutil


def build_exe():
    """Build standalone executable."""
    
    print("\n" + "="*60)
    print("  VRG Config & Test Generator - EXE Builder")
    print("="*60 + "\n")
    
    # Check if required files exist
    required_files = [
        "ConfigTestGenerator_GUI.py",
        "GenSymb_ConfigVRG.py",
        "generate_test_menu_v4.py"
    ]
    
    print("Checking required files...")
    for file in required_files:
        if not Path(file).exists():
            print(f"  ❌ Missing: {file}")
            return False
        print(f"  ✅ Found: {file}")
    
    # Check if icon exists
    icon_path = Path("VRG_Logo.ico")
    has_icon = icon_path.exists()
    if has_icon:
        print(f"  ✅ Found: VRG_Logo.ico")
    else:
        print(f"  ⚠️  Missing: VRG_Logo.ico (will build without icon)")
    
    print("\n" + "-"*60)
    print("Building executable with PyInstaller...")
    print("-"*60 + "\n")
    
    # PyInstaller command (modules are imported directly; no add-data for scripts)
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",                          # Single .exe file
        "--windowed",                         # No console window (GUI only)
        "--name=ConfigTestGenerator",         # Output name
        "--clean",                            # Clean cache
        "--noconfirm",
        "--collect-all", "pandas",
        "--collect-all", "numpy",
        "--collect-all", "openpyxl",
        "--collect-all", "et_xmlfile",
    ]
    
    # Add icon if exists
    if has_icon:
        cmd.extend(["--icon=VRG_Logo.ico"])
    
    # Add main script
    cmd.append("ConfigTestGenerator_GUI.py")
    
    print(f"Command: {' '.join(cmd)}\n")
    
    # Run PyInstaller
    try:
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "="*60)
        print("  ✅ BUILD SUCCESSFUL!")
        print("="*60)
        
        # Check output
        exe_path = Path("dist") / "ConfigTestGenerator.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n📦 Executable created:")
            print(f"   Location: {exe_path.absolute()}")
            print(f"   Size: {size_mb:.1f} MB")
            
            print("\n📋 How to use:")
            print("   1. Copy 'dist/ConfigTestGenerator.exe' to any computer")
            print("   2. Double-click to run (no Python required!)")
            print("   3. Use the 3-step workflow:")
            print("      - Import Excel file")
            print("      - Generate configs")
            print("      - Generate tests")
            
            print("\n💡 Tips:")
            print("   - No installation needed")
            print("   - Works on any Windows PC")
            print("   - All dependencies included")
            print("   - Portable (can run from USB stick)")
            
            # Cleanup recommendation
            print("\n🧹 Cleanup (optional):")
            print("   - Delete 'build/' folder (temporary files)")
            print("   - Keep 'dist/ConfigTestGenerator.exe' (final executable)")
            print("   - Delete 'ConfigTestGenerator.spec' (build config)")
            
            return True
        else:
            print("\n❌ ERROR: Executable not found in dist/")
            return False
            
    except subprocess.CalledProcessError as e:
        print("\n" + "="*60)
        print("  ❌ BUILD FAILED!")
        print("="*60)
        print(f"\nError: {e}")
        return False
    except Exception as e:
        print("\n" + "="*60)
        print("  ❌ BUILD FAILED!")
        print("="*60)
        print(f"\nUnexpected error: {e}")
        return False


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
