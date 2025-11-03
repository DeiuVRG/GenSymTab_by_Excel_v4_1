# 🎨 VRG Config & Test Generator GUI

## 📋 Descriere

Aplicație modernă cu interfață grafică pentru generarea automată a:
- **Fișiere de configurare** (.hwtp) din Excel
- **Meniuri de test interactive** pentru ISODiag

## ✨ Caracteristici

### 🎯 **3 Pași Simpli:**

1. **📁 Import Excel**
   - Selectează fișierul Excel cu simbolurile
   - Suportă orice structură cu coloane: Symbol, Address, Type, etc.

2. **⚙️ Generare Configs**
   - Selectează directorul de output
   - Generează automat:
     - `config.hwtp` (master)
     - `config_DZC.hwtp`, `config_MAN.hwtp`, etc. (variante)

3. **🧪 Generare Teste**
   - Generează automat teste pentru TOATE variantele
   - Output: `test_DZC_v4.hwtp`, `test_MAN_v4.hwtp`, etc.

### 🎨 **Design Modern:**
- **Dark theme** futuristic
- **Custom buttons** cu hover effects
- **Progress feedback** în timp real
- **Status bar** cu mesaje colorate

---

## 🚀 Cum folosești?

### **Lansare**

```bash
python ConfigTestGenerator_GUI.py
```

### **Workflow**

1. **Click "📁 Select Excel File"**
   - Navighezi la fișierul Excel
   - Selectezi fișierul (ex: `Traton_DZC_SymTab_B0.xlsx`)

2. **Click "⚙️ Generate Configs"**
   - Selectezi folder-ul unde vrei să salvezi
   - Aplică generează toate config-urile automat

3. **Click "🧪 Generate Tests"**
   - Generează testele automat în același folder cu config-urile
   - Gata! Poți încărca în ISODiag

---

## 📂 Output

### **După Config Generation:**
```
output_folder/
├── config.hwtp              (master - toate variantele)
├── config_DZC.hwtp          (doar DZC)
├── config_MAN.hwtp          (doar MAN)
└── config_TRT.hwtp          (doar TRT)
```

### **După Test Generation:**
```
output_folder/
├── config_DZC.hwtp
├── test_DZC_v4.hwtp         (✨ NEW)
├── config_MAN.hwtp
├── test_MAN_v4.hwtp         (✨ NEW)
├── config_TRT.hwtp
└── test_TRT_v4.hwtp         (✨ NEW)
```

---

## 🎯 Funcții Auto-Detectate

### **Config Generator:**
- ✅ Orice număr de variante (DZC, MAN, TRT, etc.)
- ✅ Simboluri cu orice format (wo32, wo16, by)
- ✅ Multi-word symbols (split automat în _low/_high sau _w0..._w3)
- ✅ CAN messages (generează VAR automat)
- ✅ Pointer types ($$$$() wrapper automat)

### **Test Generator:**
- ✅ **Hardware detectat automat:**
  - SPI channels (orice număr)
  - CAN buses (1-16+)
  - PWM Outputs/Inputs
  - ADC channels
  - Digital I/O
  - NFC, LIN, I2C, Watchdog, Flash

- ✅ **Teste generate:**
  - SPI: 3 patterns × 2 cycles
  - PWM: Sweep 0% → 100% în 5 pași
  - ADC: 5 citiri consecutive
  - Digital I/O: 3 cicluri monitorizare

---

## 🛠️ Cerințe

### **Python Packages:**
```bash
pip install pandas openpyxl
```

### **Fișiere Necesare:**
- `GenSymb_ConfigVRG.py` (config generator)
- `generate_test_menu_v4.py` (test generator)
- `VRG_Logo.ico` (icon - opțional)

---

## 🎨 Screenshot Preview

```
╔════════════════════════════════════════════════════════╗
║  ⚙️ VRG Config & Test Generator                        ║
║  Universal Hardware Test Generator v4.0               ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  STEP 1: Import Excel File                           ║
║  ────────────────────────────────────                 ║
║  📄 Traton_DZC_SymTab_B0_draft_MAN&DZC 4.xlsx        ║
║                                                        ║
║  [ 📁 Select Excel File ]                             ║
║                                                        ║
║  STEP 2: Generate Configurations                     ║
║  ────────────────────────────────────                 ║
║  ✅ Generated 3 config file(s) in:                    ║
║  C:\QMT\AutoQMT\Output                                ║
║                                                        ║
║  [ ⚙️ Generate Configs ]                              ║
║                                                        ║
║  STEP 3: Generate Test Menus                         ║
║  ────────────────────────────────────                 ║
║  ✅ Generated 3 test file(s) in:                      ║
║  C:\QMT\AutoQMT\Output                                ║
║                                                        ║
║  [ 🧪 Generate Tests ]                                ║
║                                                        ║
╠════════════════════════════════════════════════════════╣
║  Ready                                                 ║
╚════════════════════════════════════════════════════════╝
```

---

## 💡 Tips

### **Pentru Excel nou:**
1. Asigură-te că ai sheet-uri:
   - `Master Symbol Table` (sau variante cu `_` sau spații)
   - `Symbol Tables`
   - `Standard Symbol Table`
   - Sheet-uri cu date (ex: `DZC_Data`, `MAN_Data`)

2. Coloane necesare:
   - `Symbol` / `Symbol Name` / `Name`
   - `Address` / `Addr`
   - `Type` / `Data Type`
   - `Size` / `Size(Bytes)`
   - `Hex` sau `Offset`

### **Erori comune:**

**"No config files found"**
→ Verifică că s-au generat config-uri în pasul 2

**"Failed to generate tests"**
→ Verifică că `generate_test_menu_v4.py` există în folder

**"Invalid Excel format"**
→ Verifică că fișierul este `.xlsx` (nu `.xls`)

---

## 🏆 Avantaje

✅ **User-friendly** - Interfață intuitivă, 3 pași simpli
✅ **Rapid** - Generare automată, fără comenzi manual
✅ **Visual feedback** - Vezi progress în timp real
✅ **Universal** - Funcționează cu ORICE placă/Excel
✅ **Portable** - Un singur executabil Python

---

## 📞 Suport

Pentru probleme sau întrebări:
- Verifică README.md principal
- Verifică QUICK_START.md

---

**Versiune:** 4.0 GUI  
**Data:** 2025-01-03  
**Autor:** VRG Team  
**Status:** ✅ Production Ready
