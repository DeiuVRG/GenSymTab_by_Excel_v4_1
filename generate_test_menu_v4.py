#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_test_menu_v4.py
------------------------
UNIVERSAL test menu generator - SINGLE BALANCED TEST LEVEL

Changes from V3:
- Removed basic/intermediate split
- ONE balanced test level (moderate cycles, practical)
- Works with ANY board automatically
- Simplified CLI (no --level parameter)
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def parse_config(config_path: Path) -> Dict[str, List[str]]:
    """Parse config and group symbols by hardware type."""
    groups = defaultdict(list)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            # Extract symbol from wo32/wo16/by lines
            match = re.match(r'^(wo32|wo16|by)\s+(\w+)', line)
            if not match:
                continue
            
            cmd, symbol = match.groups()
            
            # Skip internal references
            if '_g_' in symbol or '_c_' in symbol:
                continue
            
            # Group by hardware pattern
            if symbol.startswith('SPI_'):
                # SPI_00_TxBuf, SPI_01_CAN_RxBuf -> SPI_00, SPI_01_CAN
                match = re.match(r'(SPI_\d+(?:_\w+)?)_(?:TxBuf|RxBuf|Ctrl|TxLim)', symbol)
                if match:
                    groups[f'spi:{match.group(1)}'].append(symbol)
            
            elif symbol.startswith('CAN_'):
                # CAN_01_Tx00, CAN_02_Rx10 -> CAN_01, CAN_02
                match = re.match(r'(CAN_\d+)', symbol)
                if match:
                    groups[f'can:{match.group(1)}'].append(symbol)
            
            elif 'PWM_OUT_' in symbol or 'OUT_PWM_' in symbol:
                # PWM_OUT_01_UC_low, OUT_PWM_02_high -> PWM_OUT_01_UC, OUT_PWM_02
                if '_low' in symbol or '_high' in symbol:
                    base = symbol.replace('_low', '').replace('_high', '')
                    groups[f'pwm_out:{base}'].append(symbol)
            
            elif 'PWM_IN_' in symbol or 'DIG_FREQ_IN_' in symbol:
                # PWM_IN_01_UC_w0 -> PWM_IN_01_UC
                match = re.match(r'((?:PWM_IN|DIG_FREQ_IN)_\d+(?:_\w+)?)_w\d+', symbol)
                if match:
                    groups[f'pwm_in:{match.group(1)}'].append(symbol)
            
            elif symbol.startswith('ANA_IN_') or symbol.startswith('ADC_'):
                # ANA_IN_01_UC, ADC_02 -> ANA_IN_01, ADC_02
                match = re.match(r'((?:ANA_IN|ADC)_\d+)', symbol)
                if match:
                    groups[f'adc:{match.group(1)}'].append(symbol)
            
            elif 'DIG_IN_' in symbol or 'WAKE' in symbol or 'FAULT' in symbol or 'DETECT' in symbol or 'INT' in symbol or 'FB_' in symbol:
                groups['dig_in:DIGITAL_IN'].append(symbol)
            
            elif 'DIG_OUT_' in symbol or '_DO_' in symbol or '_EN' in symbol or '_SEL_' in symbol:
                groups['dig_out:DIGITAL_OUT'].append(symbol)
    
    return groups


def generate_test_menu(groups: Dict[str, List[str]]) -> List[str]:
    """Generate SINGLE balanced test menu."""
    lines = [
        ";============================================================",
        "; Auto-Generated Test Menu (V4 - Universal Single-Level)",
        ";",
        f"; Detected: {len(groups)} hardware groups",
        "; Test Level: BALANCED (moderate cycles, practical testing)",
        ";============================================================",
        "",
        "CL",
        'EC "============================================================"',
        'EC "     Universal Hardware Test Menu"',
        'EC "============================================================"',
        "",
        "; Variables",
        "WO #d 0.",
        "WO #n 0.",
        "WO #i 0.",
        "WO #p 0.",
        "",
    ]
    
    # Generate menu
    lines.append(":MENU")
    lines.append('EC "============================================================"')
    lines.append('EC "[0] Exit"')
    
    option = 1
    menu_items = []
    for group_key in sorted(groups.keys()):
        hw_type, hw_name = group_key.split(':', 1)
        lines.append(f'EC "[{option}] {hw_type.upper()}: {hw_name}"')
        menu_items.append((option, group_key))
        option += 1
    
    lines.append('EC "============================================================"')
    lines.append(f'IN "Select [0..{option-1}]: " #n')
    lines.append("")
    
    # Dispatcher
    lines.append("; Dispatcher")
    lines.append("WO #d (#n - 0.)")
    lines.append("IF Z GO EXIT")
    
    for opt, _ in menu_items:
        lines.append(f"WO #d (#n - {opt}.)")
        lines.append(f"IF Z GO TEST_{opt}")
    
    lines.append("GO MENU")
    lines.append("")
    lines.append(":EXIT")
    lines.append('EC "Exiting."')
    lines.append("")
    
    # Generate tests (BALANCED level - moderate cycles)
    for opt, group_key in menu_items:
        hw_type, hw_name = group_key.split(':', 1)
        symbols = groups[group_key]
        
        lines.append(f"; {hw_type.upper()}: {hw_name}")
        lines.append(f":TEST_{opt}")
        lines.append(f'EC "=== {hw_name} Test ==="')
        
        if hw_type == 'spi':
            # SPI: 3 patterns × 2 cycles
            base = hw_name
            lines.extend([
                "WO #i 0.",
                f":TEST_{opt}_LOOP",
                'EC "  Pattern 1: 0xAA55"',
                f"CB {base}_TxLim_u8 0x02",
                f"CW {base}_TxBuf_pu8 0xAA55",
                f"CW {base}_Ctrl_b16 0x8000",
                "WA 2",
                f"MD {base}_RxBuf_pu8 2 %02x",
                'EC "  Pattern 2: 0xFF00"',
                f"CB {base}_TxLim_u8 0x02",
                f"CW {base}_TxBuf_pu8 0xFF00",
                f"CW {base}_Ctrl_b16 0x8000",
                "WA 2",
                f"MD {base}_RxBuf_pu8 2 %02x",
                'EC "  Pattern 3: 0x5A5A"',
                f"CB {base}_TxLim_u8 0x02",
                f"CW {base}_TxBuf_pu8 0x5A5A",
                f"CW {base}_Ctrl_b16 0x8000",
                "WA 2",
                f"MD {base}_RxBuf_pu8 2 %02x",
                "WO #i (#i + 1.)",
                "WO #d (#i - 2.)",
                f"IF N GO TEST_{opt}_LOOP",
                'EC "Test completed (2 cycles)"',
            ])
        
        elif hw_type == 'pwm_out':
            # PWM: Sweep 0-100% in 25% steps (5 steps × 3 sec = 15 sec)
            base = hw_name
            lines.extend([
                "WO #i 0.",
                f":TEST_{opt}_LOOP",
                "WO #d (#i * 25.)",
                f"CW {base}_low #d",
                "WO #d (100. - #d)",
                f"CW {base}_high #d",
                "WA 3",
                "WO #i (#i + 1.)",
                "WO #d (#i - 5.)",
                f"IF N GO TEST_{opt}_LOOP",
                'EC "Sweep completed: 0%% -> 25%% -> 50%% -> 75%% -> 100%%"',
            ])
        
        elif hw_type == 'pwm_in':
            # PWM Input: Monitor for 5 cycles
            base = hw_name
            lines.extend([
                "WO #i 0.",
                f":TEST_{opt}_LOOP",
                f'EC "  Low: " DW {base}_w0 %d',
                f'EC "  High: " DW {base}_w1 %d',
                f'EC "  Period: " DW {base}_w2 %d',
                "WA 5",
                "WO #i (#i + 1.)",
                "WO #d (#i - 5.)",
                f"IF N GO TEST_{opt}_LOOP",
                'EC "Monitor completed (5 cycles)"',
            ])
        
        elif hw_type == 'adc':
            # ADC: Monitor for 5 readings
            lines.extend([
                "WO #i 0.",
                f":TEST_{opt}_LOOP",
                f'EC "  Value: " DW {hw_name}_UC %d',
                "WA 3",
                "WO #i (#i + 1.)",
                "WO #d (#i - 5.)",
                f"IF N GO TEST_{opt}_LOOP",
                'EC "Monitor completed (5 readings)"',
            ])
        
        elif hw_type in ('dig_in', 'dig_out'):
            # Digital I/O: Monitor first 8 for 3 cycles
            lines.extend([
                "WO #i 0.",
                f":TEST_{opt}_LOOP",
            ])
            for sym in symbols[:8]:
                lines.append(f'EC "  {sym}: " DB {sym} %d')
            lines.extend([
                "WA 5",
                "WO #i (#i + 1.)",
                "WO #d (#i - 3.)",
                f"IF N GO TEST_{opt}_LOOP",
                'EC "Monitor completed (3 cycles)"',
            ])
        
        elif hw_type == 'can':
            # CAN: Show status for 3 cycles
            lines.extend([
                "WO #i 0.",
                f":TEST_{opt}_LOOP",
            ])
            for sym in symbols[:5]:
                lines.append(f'EC "  {sym}"')
            lines.extend([
                "WA 5",
                "WO #i (#i + 1.)",
                "WO #d (#i - 3.)",
                f"IF N GO TEST_{opt}_LOOP",
                'EC "Monitor completed (3 cycles)"',
            ])
        
        else:
            # Generic: Show symbols for 2 cycles
            lines.extend([
                "WO #i 0.",
                f":TEST_{opt}_LOOP",
            ])
            for sym in symbols[:5]:
                lines.append(f'EC "  {sym}"')
            lines.extend([
                "WA 5",
                "WO #i (#i + 1.)",
                "WO #d (#i - 2.)",
                f"IF N GO TEST_{opt}_LOOP",
                'EC "Monitor completed (2 cycles)"',
            ])
        
        lines.append("GO MENU")
        lines.append("")
    
    return lines


def main():
    parser = argparse.ArgumentParser(
        description="Universal test generator V4 - Single balanced test level"
    )
    parser.add_argument("config", help="Config file (.hwtp)")
    parser.add_argument("--out", "-o", default="test_menu.hwtp", help="Output file")
    
    args = parser.parse_args()
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[ERROR] Not found: {config_path}")
        return 1
    
    print(f"[INFO] Parsing: {config_path}")
    groups = parse_config(config_path)
    
    print(f"[INFO] Detected {len(groups)} hardware groups:")
    for key in sorted(groups.keys()):
        hw_type, hw_name = key.split(':', 1)
        print(f"  - {hw_type.upper()}: {hw_name} ({len(groups[key])} symbols)")
    
    print(f"[INFO] Generating balanced tests...")
    lines = generate_test_menu(groups)
    
    output_path = Path(args.out)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"[OK] Generated: {output_path} ({len(lines)} lines)")
    print(f"[INFO] Test level: BALANCED (moderate cycles, practical testing)")
    return 0


if __name__ == "__main__":
    exit(main())
