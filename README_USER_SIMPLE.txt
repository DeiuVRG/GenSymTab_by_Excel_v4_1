# ⚙️ VRG Config & Test Generator

## 📋 Ce face această aplicație?

Generează automat fișiere de configurare și teste pentru ISODiag din fișiere Excel.

---

## 🚀 Cum să folosești

### **1️⃣ Deschide aplicația**

Dublu-click pe `ConfigTestGenerator.exe` → aplicația pornește imediat!

### **2️⃣ Importă fișierul Excel**

- Click pe butonul **"📁 Select Excel File"**
- Navighează la fișierul Excel (ex: `Traton_DZC_SymTab_B0.xlsx`)
- Selectează fișierul → numele va apărea în interfață

### **3️⃣ Generează configurații**

- Click pe butonul **"⚙️ Generate Configs"**
- Alege folder-ul unde vrei să salvezi fișierele
- Așteaptă procesul de generare
- Vei vedea mesaj: "✅ Generated X config file(s)"

### **4️⃣ Generează teste**

- Click pe butonul **"🧪 Generate Tests"**
- Testele se generează automat pentru toate variantele
- Vei vedea mesaj: "✅ Generated X test file(s)"

### **5️⃣ Gata! 🎉**

Fișierele generate sunt în folder-ul pe care l-ai ales:
- `config_DZC.hwtp`
- `config_MAN.hwtp`
- `test_DZC_v4.hwtp`
- `test_MAN_v4.hwtp`
- etc.

---

## 📂 Ce primești

După generare, vei avea:

```
📁 Folder-ul tău/
  ├── config.hwtp              (toate variantele)
  ├── config_DZC.hwtp          (doar DZC)
  ├── config_MAN.hwtp          (doar MAN)
  ├── test_DZC_v4.hwtp         (teste pentru DZC)
  ├── test_MAN_v4.hwtp         (teste pentru MAN)
  └── ...
```

---

## ✅ Cerințe

- **Windows** (7, 8, 10, 11)
- **NU trebuie Python instalat!**
- **NU trebuie alte programe!**
- Doar dublu-click pe `.exe` și funcționează!

---

## 💡 Tips

### **Excel-ul tău trebuie să aibă:**
- Sheet: `Master Symbol Table` (sau variante)
- Sheet: `Symbol Tables`
- Sheet: `Standard Symbol Table`
- Coloane: `Symbol`, `Address`, `Type`, `Size`

### **Dacă ai erori:**
- Verifică că Excel-ul este `.xlsx` (nu `.xls` vechi)
- Verifică că Excel-ul nu este deschis în alt program
- Verifică că ai permisiuni de scriere în folder-ul de output

---

## 🎯 Ce detectează automat?

✅ **Hardware:**
- SPI channels
- CAN buses (oricâte)
- PWM outputs/inputs
- ADC channels
- Digital I/O (inputs/outputs)
- NFC, LIN, I2C, Watchdog, Flash

✅ **Teste generate:**
- **SPI**: 3 patterns × 2 cycles
- **PWM**: Sweep 0% → 100% (5 pași)
- **ADC**: 5 citiri consecutive
- **Digital I/O**: 3 cicluri monitorizare

---

## ❓ Întrebări frecvente

### **Aplicația nu pornește?**
→ Verifică că ai Windows actualizat  
→ Verifică că nu este blocată de antivirus (adaugă în whitelist)

### **Nu generează config-uri?**
→ Verifică structura Excel-ului (sheet-uri și coloane)  
→ Verifică că ai selectat corect fișierul Excel

### **Nu generează teste?**
→ Trebuie să generezi config-urile mai întâi (STEP 2)  
→ Verifică că există fișiere `config_*.hwtp` în folder

### **Testele nu funcționează în ISODiag?**
→ Verifică că ai încărcat config-ul corect (`config_DZC.hwtp` pentru DZC)  
→ Verifică că simbolurile există în ECU  
→ Rulează `MD symbol_name` pentru verificare

---

## 📞 Suport

Pentru probleme sau întrebări:
- Verifică **README_GUI.md** (detalii tehnice)
- Verifică **README_EXECUTABLE.md** (detalii build)

---

## 🏆 Avantaje

✅ **Simplu** → 3 click-uri și gata!  
✅ **Rapid** → generare automată în secunde  
✅ **Universal** → funcționează cu orice placă/Excel  
✅ **Portabil** → rulează de pe USB stick  
✅ **Fără instalare** → dublu-click și funcționează!  

---

**Versiune:** 4.0  
**Status:** ✅ Ready to use  
**Made by:** VRG Team  
**Data:** 2025-01-03
