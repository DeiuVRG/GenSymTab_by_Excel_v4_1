# 🚀 QUICK START - Test Menu Generator V4

## Ce ai în folder?

### 📁 Tools (2 fișiere principale)
```
GenSymb_ConfigVRG.py          → Generează configs din Excel
generate_test_menu_v4.py      → Generează teste din configs
generate_all_tests_v4.ps1     → Batch: generează toate testele
```

### 📁 Configs (3 fișiere)
```
config.hwtp                   → Config complet (toate variantele)
config_DZC.hwtp              → Config variant DZC
config_MAN.hwtp              → Config variant MAN
```

### 📁 Tests V4 (2 fișiere - FINAL)
```
test_DZC_v4.hwtp             → Teste DZC (636 linii, 29 groups)
test_MAN_v4.hwtp             → Teste MAN (511 linii, 25 groups)
```

---

## ⚡ Cum folosești?

### 1️⃣ Generare Configs (din Excel)
```bash
python GenSymb_ConfigVRG.py
```
**Output:** `config.hwtp`, `config_DZC.hwtp`, `config_MAN.hwtp`

### 2️⃣ Generare Teste (din configs)

**Opțiune A - Manual (per config):**
```bash
python generate_test_menu_v4.py config_DZC.hwtp
python generate_test_menu_v4.py config_MAN.hwtp
```

**Opțiune B - Automat (toate config-urile):**
```powershell
.\generate_all_tests_v4.ps1
```

**Output:** `test_DZC_v4.hwtp`, `test_MAN_v4.hwtp`

### 3️⃣ Folosire în ISODiag
1. Deschide ISODiag
2. Încarcă config-ul: `config_DZC.hwtp`
3. Încarcă testele: `test_DZC_v4.hwtp`
4. Selectează numărul testului din meniu
5. Rulează testul

---

## 📊 Ce detectează automat?

| Hardware | DZC | MAN |
|----------|-----|-----|
| **ADC channels** | 7 | **11** ✨ |
| **PWM Outputs** | **14** ✨ | 0 |
| **PWM Inputs** | 2 | **8** ✨ |
| **Digital IN** | 8 | **12** ✨ |
| **Digital OUT** | **20** ✨ | 5 |
| **CAN buses** | 1 (123 sym) | 1 (122 sym) |
| **SPI channels** | 3 | 3 |

**→ Același tool detectează diferite hardware-uri automat!**

---

## 🎯 Caracteristici Teste V4

### Nivel: BALANCED (echilibrat)
- ✅ Nici prea rapid (cum era basic)
- ✅ Nici prea lung (cum era intermediate)
- ✅ **Perfect pentru validare practică**

### Durate:
| Test Type | Durată | Detalii |
|-----------|--------|---------|
| **SPI** | ~12 sec | 3 patterns × 2 cycles |
| **PWM Out** | ~15 sec | 5 steps: 0% → 25% → 50% → 75% → 100% |
| **PWM In** | ~25 sec | 5 readings (Low, High, Period) |
| **ADC** | ~15 sec | 5 consecutive readings |
| **Digital I/O** | ~15 sec | 3 monitoring cycles |

---

## ❓ Întrebări Frecvente

### Q: Cum generez teste pentru un config nou?
```bash
python generate_test_menu_v4.py config_NEW.hwtp --out test_NEW.hwtp
```

### Q: Funcționează cu plăci care au NFC, LIN, I2C?
**Da!** V4 detectează automat ORICE hardware prin pattern matching.

### Q: Funcționează cu 16 CAN buses?
**Da!** Nu există limite hard-coded. Detectează automat CAN_01, CAN_02, ... CAN_16.

### Q: Pot modifica duratele testelor?
**Da!** Editează `generate_test_menu_v4.py`:
- Linia `WA X` = wait X secunde
- Linia `IF N GO TEST_X_LOOP` = număr cicluri

### Q: Ce s-a întâmplat cu basic/intermediate?
**Simplificat!** Acum există doar UN nivel echilibrat care combină avantajele ambelor.

---

## 🔧 Structura Fișier Test

```hwtp
;============================================================
; Auto-Generated Test Menu (V4 - Universal Single-Level)
;============================================================

CL
EC "============================================================"
EC "     Universal Hardware Test Menu"
EC "============================================================"

:MENU
EC "[0] Exit"
EC "[1] ADC: ANA_IN_01"
EC "[2] ADC: ANA_IN_02"
...
IN "Select [0..29]: " #n

; Dispatcher
WO #d (#n - 0.)
IF Z GO EXIT
WO #d (#n - 1.)
IF Z GO TEST_1
...

:TEST_1
EC "=== ANA_IN_01 Test ==="
WO #i 0.
:TEST_1_LOOP
EC "  Value: " DW ANA_IN_01_UC %d
WA 3
WO #i (#i + 1.)
WO #d (#i - 5.)
IF N GO TEST_1_LOOP
EC "Monitor completed (5 readings)"
GO MENU
```

---

## 📈 Progres Versiuni

| Ver | Status | Problema |
|-----|--------|----------|
| V1 | ❌ | Hard-coded, Unicode errors, 2 levels |
| V2 | ❌ | Over-detection, complex logic |
| V3 | ⚠️ | Funcționa dar 2 levels = confuzie |
| **V4** | ✅ **CURRENT** | **1 level, simplu, universal!** |

---

## 🎉 Beneficii V4

✅ **Mai simplu** - 1 comandă, nu 2  
✅ **Mai rapid** - generare instant  
✅ **Mai curat** - 2 fișiere, nu 8  
✅ **Universal** - ORICE placă  
✅ **Extensibil** - adaugă pattern = suport nou  
✅ **Mentinable** - 320 linii cod, clar  

---

**Autor:** VRG Team  
**Data:** 2025-01-03  
**Versiune:** 4.0  
**Status:** ✅ Production Ready
