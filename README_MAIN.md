# ⚙️ VRG Config & Test Generator v4.0

> **Sistem automat de generare a configurațiilor și testelor pentru ISODiag din fișiere Excel**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)](README.md)

---

## 📦 Quick Start

### **🖥️ Pentru utilizatori (fără Python):**

1. **Download executabilul:**
   ```
   dist/ConfigTestGenerator.exe (10.6 MB)
   ```

2. **Dublu-click** pe `.exe` → aplicația pornește imediat!

3. **Folosește GUI-ul:**
   - **STEP 1**: Import Excel → selectezi fișierul
   - **STEP 2**: Generate Configs → alegi folder-ul
   - **STEP 3**: Generate Tests → generează automat

✅ **Nu necesită Python instalat!**  
✅ **Funcționează standalone pe orice Windows!**

### **🐍 Pentru developeri (cu Python):**

```powershell
# Instalează dependențe
pip install pandas openpyxl

# Rulează GUI
python ConfigTestGenerator_GUI.py

# SAU command-line tools:
python GenSymb_ConfigVRG.py excel.xlsx --out config.hwtp --multi
python generate_test_menu_v4.py config_DZC.hwtp --out test_DZC.hwtp
```

---

## 🎯 Ce face aplicația?

### **1. Generare configurații din Excel**
- Citește Excel cu simboluri (Master Symbol Table, Symbol Tables, etc.)
- Generează `config.hwtp` (toate variantele)
- Generează `config_DZC.hwtp`, `config_MAN.hwtp`, etc. (per variantă)

### **2. Generare teste interactive**
- Detectează automat hardware-ul din config
- Generează teste pentru: SPI, CAN, PWM, ADC, Digital I/O, etc.
- Output: `test_DZC_v4.hwtp`, `test_MAN_v4.hwtp`, etc.

### **3. Încărcare în ISODiag**
- Încarcă config: `config_DZC.hwtp`
- Încarcă test: `test_DZC_v4.hwtp`
- Selectează testul din meniu → rulează automat

---

## 📂 Structura proiect

```
AutoGenCOnfigSymTable/
├── dist/
│   └── ConfigTestGenerator.exe        ← Executabil standalone (10.6 MB)
│
├── 📁 COD SURSĂ (Python):
│   ├── ConfigTestGenerator_GUI.py     ← Interfață grafică (GUI)
│   ├── GenSymb_ConfigVRG.py           ← Generator configurații
│   ├── generate_test_menu_v4.py       ← Generator teste
│   └── build_exe.py                   ← Script pentru build .exe
│
├── 📁 DOCUMENTAȚIE:
│   ├── README.md                      ← Acest fișier
│   ├── README_GUI.md                  ← Detalii interfață grafică
│   ├── README_EXECUTABLE.md           ← Detalii build & distribuție
│   ├── README_USER_SIMPLE.txt         ← Ghid simplu pentru utilizatori
│   └── QUICK_START.md                 ← Ghid rapid
│
├── 📁 ASSETS:
│   ├── VRG_Logo.ico                   ← Icon aplicație
│   └── Traton_DZC_SymTab_B0...xlsx    ← Excel exemplu
│
└── .gitignore                         ← Exclude fișiere generate
```

---

## ✨ Features

### **GUI Modern**
- ✅ Dark theme futuristic
- ✅ Responsive layout (scalare automată)
- ✅ 3-step workflow simplu
- ✅ Visual feedback în timp real
- ✅ Custom gradient buttons

### **Generare Config**
- ✅ Multi-variant support (DZC, MAN, TRT, etc.)
- ✅ Auto-detect data types (wo32, wo16, by)
- ✅ Multi-word symbols (split automat)
- ✅ CAN messages (VAR automat)
- ✅ Pointer types ($$$$ wrapper)

### **Generare Test**
- ✅ Auto-detect hardware (SPI, CAN, PWM, ADC, DIO, etc.)
- ✅ Single balanced test level
- ✅ Pattern-based detection (universal)
- ✅ Teste funcționale pentru fiecare hardware

### **Standalone Executable**
- ✅ Single file (10.6 MB)
- ✅ No Python required
- ✅ Portable (USB/network)
- ✅ All dependencies included

---

## 🔧 Hardware Detection

### **Detectat automat:**

| Hardware | Test generat |
|----------|--------------|
| **SPI** | 3 patterns × 2 cycles |
| **CAN** | Oricâte bus-uri (1-16+) |
| **PWM Output** | Sweep 0% → 100% (5 pași × 3s) |
| **PWM Input** | Monitorizare frecvență/duty |
| **ADC** | 5 citiri consecutive |
| **Digital Input** | 3 cicluri monitorizare |
| **Digital Output** | Toggle ON/OFF × 3 |
| **NFC/LIN/I2C** | Pattern-based tests |
| **Watchdog** | Enable/disable test |
| **Flash** | Read/write test |

---

## 📋 Cerințe

### **Pentru executabil (.exe):**
- ✅ Windows 7, 8, 10, 11
- ✅ **NU** trebuie Python
- ✅ **NU** trebuie alte programe

### **Pentru Python scripts:**
- Python 3.8+
- pandas
- openpyxl
- tkinter (inclus în Python)

### **Pentru Excel:**
- Sheets: `Master Symbol Table`, `Symbol Tables`, `Standard Symbol Table`
- Coloane: `Symbol`/`Name`, `Address`, `Type`, `Size`, `Reference`

---

## 🚀 Workflow complet

### **1. Pregătire Excel**
- Asigură-te că Excel-ul are structura corectă
- Sheet-uri: Master Symbol Table, Symbol Tables, etc.
- Coloane: Symbol, Address, Type, Size

### **2. Generare configurații**
```powershell
# GUI: Click "Generate Configs"
# CLI:
python GenSymb_ConfigVRG.py Traton_Excel.xlsx --out config.hwtp --multi
```

**Output:**
- `config.hwtp` (master - toate variantele)
- `config_DZC.hwtp` (doar DZC)
- `config_MAN.hwtp` (doar MAN)
- etc.

### **3. Generare teste**
```powershell
# GUI: Click "Generate Tests"
# CLI:
python generate_test_menu_v4.py config_DZC.hwtp --out test_DZC_v4.hwtp
python generate_test_menu_v4.py config_MAN.hwtp --out test_MAN_v4.hwtp
```

**Output:**
- `test_DZC_v4.hwtp` (teste pentru DZC)
- `test_MAN_v4.hwtp` (teste pentru MAN)
- etc.

### **4. Încărcare în ISODiag**
1. Încarcă config: `config_DZC.hwtp`
2. Încarcă test: `test_DZC_v4.hwtp`
3. Selectează testul din meniu (ex: "Test 1: SPI_00 Pattern Test")
4. Rulează testul → vezi rezultatele

---

## 🛠️ Build executabil

```powershell
# Build .exe cu PyInstaller
python build_exe.py

# Output: dist/ConfigTestGenerator.exe
```

**Rebuild după modificări:**
1. Modifici codul Python (`ConfigTestGenerator_GUI.py`, etc.)
2. Rulezi: `python build_exe.py`
3. Noul `.exe` este în `dist/`

---

## 📚 Documentație detaliată

| Fișier | Descriere |
|--------|-----------|
| **README.md** | Acest fișier (overview general) |
| **README_GUI.md** | Detalii interfață grafică |
| **README_EXECUTABLE.md** | Build & distribuție .exe |
| **README_USER_SIMPLE.txt** | Ghid simplu pentru utilizatori |
| **QUICK_START.md** | Ghid rapid de folosire |

---

## 🎨 Screenshots

### **GUI Principal:**
```
╔════════════════════════════════════════════════════════╗
║  ⚙️ VRG Config & Test Generator                        ║
║  Universal Hardware Test Generator v4.0               ║
╠════════════════════════════════════════════════════════╣
║  STEP 1: Import Excel File                           ║
║  📄 Traton_DZC_SymTab_B0.xlsx                         ║
║  [📁 Select Excel File]                               ║
║                                                        ║
║  STEP 2: Generate Configurations                     ║
║  ✅ Generated 3 config file(s)                        ║
║  [⚙️ Generate Configs]                                ║
║                                                        ║
║  STEP 3: Generate Test Menus                         ║
║  ✅ Generated 3 test file(s)                          ║
║  [🧪 Generate Tests]                                  ║
╠════════════════════════════════════════════════════════╣
║  Ready                                                 ║
╚════════════════════════════════════════════════════════╝
```

---

## ❓ FAQ

### **Aplicația nu pornește?**
→ Verifică că ai Windows actualizat  
→ Dezactivează temporar antivirus (false positive)  
→ Adaugă `.exe` în whitelist

### **Nu generează config-uri?**
→ Verifică structura Excel-ului (sheets și coloane)  
→ Asigură-te că Excel nu este deschis în alt program

### **Nu generează teste?**
→ Trebuie să generezi config-urile mai întâi (STEP 2)  
→ Verifică că există `config_*.hwtp` în folder

### **Testele nu funcționează în ISODiag?**
→ Verifică că ai încărcat config-ul corect  
→ Verifică că simbolurile există în ECU (`MD symbol_name`)  
→ Verifică că hardware-ul este inițializat

---

## 🏆 V4 Changes (Noiembrie 2025)

### **✨ Noutăți:**
- ✅ **GUI standalone** cu dark theme modern
- ✅ **Executabil .exe** (nu mai trebuie Python)
- ✅ **Responsive UI** (scalare automată)
- ✅ **Single test level** (eliminat basic/intermediate)
- ✅ **PWM duty fix** (eliminat bug ISODiag)

### **🔧 Bug Fixes:**
- ✅ PWM duty display corect (nu mai afișează literal `DW #p %d %%`)
- ✅ ISODiag compatibility (EC + DW pe linii separate)

### **📦 Architecture:**
- ✅ Modular design (GUI + CLI tools)
- ✅ PyInstaller integration
- ✅ Resource path handling pentru .exe

---

## 📞 Contact & Support

**Made by:** VRG Team  
**Version:** 4.0  
**Date:** November 2025  
**Status:** ✅ Production Ready

Pentru probleme tehnice, consultă documentația detaliată:
- README_GUI.md (interfață grafică)
- README_EXECUTABLE.md (build & distribuție)
- QUICK_START.md (quick reference)

---

## 📄 License

© 2025 VRG Team. All rights reserved.

---

**🎉 Enjoy automated testing!**
