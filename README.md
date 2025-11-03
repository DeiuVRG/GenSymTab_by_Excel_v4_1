# 🚀 Universal Test Menu Generator V4

## Ce face?
Generează automat meniuri de test interactive pentru **ORICE placă** din fișierele `.hwtp`.

## ✨ Nou în V4
- **UN SINGUR nivel de test** (nu mai există basic/intermediate)
- **Echilibrat**: nici prea scurt, nici prea lung
- **Mai simplu de folosit**: fără parametrul `--level`
- **Universal**: funcționează identic pentru orice placă

---

## 🚀 Folosire

### Generare Test
```bash
python generate_test_menu_v4.py config_DZC.hwtp --out test_DZC.hwtp
python generate_test_menu_v4.py config_MAN.hwtp --out test_MAN.hwtp
```

### Încărcare în ISODiag
1. Încarcă config-ul (`config_DZC.hwtp`)
2. Încarcă testul (`test_DZC.hwtp`)
3. Selectează numărul testului din meniu

---

## 📊 Ce Detectează Automat?

| Hardware | Exemplu Pattern | Detectat ca |
|----------|----------------|-------------|
| **SPI** | `SPI_00_TxBuf`, `SPI_01_CAN_RxBuf` | `SPI_00`, `SPI_01_CAN` |
| **CAN** | `CAN_01_Tx00`, `CAN_02_Rx10` | `CAN_01`, `CAN_02` |
| **PWM Out** | `PWM_OUT_01_UC_low`, `OUT_PWM_02_high` | `PWM_OUT_01_UC`, `OUT_PWM_02` |
| **PWM In** | `PWM_IN_01_UC_w0`, `DIG_FREQ_IN_02_w1` | `PWM_IN_01_UC`, `DIG_FREQ_IN_02` |
| **ADC** | `ANA_IN_03_UC`, `ADC_04` | `ANA_IN_03`, `ADC_04` |
| **Digital In** | `DIG_IN_01`, `WAKE_01`, `FAULT` | `DIGITAL_IN` |
| **Digital Out** | `DIG_OUT_02`, `_EN`, `_SEL` | `DIGITAL_OUT` |

**Funcționează cu:** NFC, LIN, I2C, Watchdog, Flash, și **ORICE** hardware nou!

---

## 🧪 Tipuri de Teste Generate

| Hardware | Test Generat | Durată |
|----------|-------------|---------|
| **SPI** | 3 pattern-uri × 2 cicluri<br>(0xAA55, 0xFF00, 0x5A5A) | ~12 sec |
| **PWM Out** | Sweep în 5 pași<br>(0% → 25% → 50% → 75% → 100%) | ~15 sec |
| **PWM In** | 5 citiri (Low, High, Period) | ~25 sec |
| **ADC** | 5 citiri consecutive | ~15 sec |
| **Digital I/O** | 3 cicluri de monitorizare | ~15 sec |
| **CAN** | 3 cicluri status | ~15 sec |

---

## 📈 Rezultate Concrete

### DZC Config
```
✓ Detectat: 29 hardware groups
  - 7 ADC
  - 14 PWM outputs  
  - 2 PWM inputs
  - 8 DIG_IN, 20 DIG_OUT
  - 1 CAN (123 symbols)
  - 3 SPI

→ Fișier generat: 636 linii (~13 KB)
```

### MAN Config
```
✓ Detectat: 25 hardware groups
  - 11 ADC (MAI MULTE decât DZC!)
  - 0 PWM outputs
  - 8 PWM inputs (MAI MULTE decât DZC!)
  - 12 DIG_IN, 5 DIG_OUT
  - 1 CAN (122 symbols)
  - 3 SPI

→ Fișier generat: 511 linii (~10 KB)
```

**→ Același tool, plăci diferite, adaptare automată! ✨**

---

## 💡 Exemple de Test

### SPI Test
```hwtp
:TEST_27
EC "=== SPI_00 Test ==="
WO #i 0.
:TEST_27_LOOP
EC "  Pattern 1: 0xAA55"
CB SPI_00_TxLim_u8 0x02
CW SPI_00_TxBuf_pu8 0xAA55
CW SPI_00_Ctrl_b16 0x8000
WA 2
MD SPI_00_RxBuf_pu8 2 %02x
EC "  Pattern 2: 0xFF00"
...
WO #i (#i + 1.)
WO #d (#i - 2.)
IF N GO TEST_27_LOOP
EC "Test completed (2 cycles)"
GO MENU
```

### PWM Sweep Test
```hwtp
:TEST_19
EC "=== PWM_OUT_01_UC Test ==="
WO #i 0.
:TEST_19_LOOP
WO #d (#i * 25.)
CW PWM_OUT_01_UC_low #d
WO #d (100. - #d)
CW PWM_OUT_01_UC_high #d
WA 3
WO #p (#i * 25.)
EC "  Duty: " DW #p %d "%%"
WO #i (#i + 1.)
WO #d (#i - 5.)
IF N GO TEST_19_LOOP
EC "Sweep: 0% -> 25% -> 50% -> 75% -> 100%"
GO MENU
```

**Rezultat:** Afișează "Duty: 0%", "Duty: 25%", ... , "Duty: 100%"

---

## 🎯 Avantaje V4

| Caracteristică | V3 | V4 |
|----------------|----|----|
| **Niveluri test** | 2 (basic + intermediate) | 1 (balanced) |
| **Comenzi necesare** | 2 per config | 1 per config |
| **Parametru --level** | Necesar | ❌ Nu mai există |
| **Complexitate** | Alegere dificilă | Simplu! |
| **Fișiere generate** | 2 per config (8 total) | 1 per config (2 total) |
| **Durată test** | 2-5 sec sau 30-60 sec | 15-25 sec (optim) |
| **Linii cod** | ~400 | ~320 |

---

## 🔧 Cum Funcționează?

1. **Parse config** - citește linie cu linie
2. **Grupează** - SPI_00_TxBuf + SPI_00_RxBuf → grup SPI_00
3. **Generează teste** - pattern-uri specifice pentru fiecare tip
4. **Salvează** - fișier .hwtp gata de încărcat

---

## 📌 CLI Complet

```bash
python generate_test_menu_v4.py <config.hwtp> [--out OUTPUT.hwtp]

Argumente:
  config.hwtp       Fișier config de analizat
  --out, -o FILE    Fișier output (default: test_menu.hwtp)
  -h, --help        Ajutor

Exemplu:
  python generate_test_menu_v4.py config_DZC.hwtp
  python generate_test_menu_v4.py config_MAN.hwtp --out test_MAN.hwtp
```

---

## ✅ Caracteristici Tehnice

- ✅ **ASCII-only** (nu mai există erori Unicode)
- ✅ **Fără linii goale EC ""** (ISODiag compatible)
- ✅ **Display variabile corect** (`DW #p %d` nu `#p` literal)
- ✅ **Pattern-based grouping** (nu over-detection)
- ✅ **Extensibil** (adaugă pattern nou = suport hardware nou)
- ✅ **Fără hard-coding** (funcționează cu 1 sau 16 CAN-uri)

---

## 🎉 Cazuri de Folosire

### 1. Bring-up Placă Nouă
```bash
python generate_test_menu_v4.py new_board.hwtp
# → Test rapid pentru toate hardware-urile detectate
```

### 2. Validare Pre-Deployment
```bash
python generate_test_menu_v4.py production_config.hwtp
# → Test echilibrat pentru validare completă
```

### 3. Plăci Multi-Variant
```bash
python generate_test_menu_v4.py config_DZC.hwtp
python generate_test_menu_v4.py config_MAN.hwtp
python generate_test_menu_v4.py config_TRT.hwtp
# → Teste specifice pentru fiecare variant
```

### 4. Plăci Complexe
Funcționează automat cu:
- 16+ CAN buses
- Multiple canale NFC
- Watchdog
- Flash
- LIN, I2C
- Orice hardware nou!

---

## 🏆 Progres V1 → V2 → V3 → V4

| Versiune | Status | Problema |
|----------|--------|----------|
| **V1** | ❌ Deprecated | Hard-coded hardware, Unicode errors, 2 levels |
| **V2** | ❌ Deprecated | Over-detection (324 digital I/O!), complex logic |
| **V3** | ⚠️ Deprecat | Funcționa bine dar 2 nivele = confuzie |
| **V4** | ✅ **FINAL** | **1 nivel, simplu, universal, perfect!** |

---

## 📂 Fișiere Generate

```
test_DZC_v4.hwtp         636 linii    ~13 KB
test_MAN_v4.hwtp         511 linii    ~10 KB
```

---

**Generator:** `generate_test_menu_v4.py`  
**Versiune:** 4.0  
**Data:** 2025-01-03  
**Status:** ✅ Production Ready
