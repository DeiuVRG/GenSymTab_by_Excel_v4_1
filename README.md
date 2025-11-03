# ⚙️ VRG Config & Test Generator v4.0

> Automatic generation of ISODiag configuration and test files from Excel

---

## 🚀 Quick Start

### **GUI Application (Recommended)**

```powershell
pip install pandas openpyxl
python ConfigTestGenerator_GUI.py
```

**3 simple steps:**
1. 📁 Import Excel
2. ⚙️ Generate Configs
3. 🧪 Generate Tests

### **Command Line**

```powershell
# Generate configs
python GenSymb_ConfigVRG.py input.xlsx --out config.hwtp --multi

# Generate tests
python generate_test_menu_v4.py config_DZC.hwtp --out test_DZC_v4.hwtp
```

---

## ✨ Features

- **Modern GUI** with dark theme
- **Universal** - works with any Excel/hardware
- **Auto-detect** - SPI, CAN, PWM, ADC, Digital I/O, etc.
- **Multi-variant** - generates separate configs (DZC, MAN, TRT, etc.)
- **Standalone .exe** - build with `python build_exe.py`

---

## 📋 Requirements

- Python 3.8+
- pandas, openpyxl

**Excel structure:**
- Sheets: `Master Symbol Table`, `Symbol Tables`, `Standard Symbol Table`
- Columns: `Symbol`, `Address`, `Type`, `Size`, `Reference`

---

## 🔧 Hardware Detection

Auto-generates tests for:
- SPI (3 patterns × 2 cycles)
- CAN (any number of buses)
- PWM (0% → 100% sweep)
- ADC (5 readings)
- Digital I/O (toggle tests)
- NFC, LIN, I2C, Watchdog, Flash

---

## 📦 Build Standalone Executable

```powershell
pip install pyinstaller
python build_exe.py
# Output: dist/ConfigTestGenerator.exe (~10 MB)
```

---

**Made by VRG Team | v4.0 | November 2025**
