#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GenSymb_ConfigVRG.py
--------------------
Generate a single .hwtp config file from an Excel workbook with multiple sheets.

Rules implemented (summary):
- For any sheet whose name contains "Master" (case-insensitive):
  Use columns: Symbol, Address  ->  wo32 <Symbol> <Address(hex)>
  Also capture the "master symbol" (row whose Symbol contains "SymMaster", else the first non-empty Symbol).

- For sheet named exactly "Symbol Tables" (case-insensitive match ignoring spaces and underscores):
  Use columns: Reference, Offset -> wo32 <Reference> $$$$(<MasterSymbol> + <Offset.>)
  Also detect the "Standard" symtab reference as the row where Reference contains "SymTabStd".

- For sheet named exactly "Standard Symbol Table" (case-insensitive match ignoring spaces/underscores):
  Use columns: Symbol, Hex (preferred) or Offset (fallback) ->
     wo32 <Symbol> $$$$(<StdSymtabRef> + <Hex or Offset>)
  NOTE: "$$$$()" is used ONLY for these special sheets.

- For all *other* sheets having: Symbol, Reference, Size and Hex (preferred) or Offset (fallback):
  - Size == 1  => by  <Symbol> <Reference> + <off>
  - Size == 2  => wo16 <Symbol> <Reference> + <off>
  - Size == 4  => wo32 <Symbol> <Reference> + <off>
  - Size == 8  => split into two 32-bit words suffixed "_low" and "_high",
                  offsets +0 and +4
  - Size == 16 => split into four 32-bit words suffixed "_w0" .. "_w3",
                  offsets +0, +4, +8, +12
  For these generic sheets, *NO* "$$$$()" wrapper is used around expressions.

- Additional CAN rule:
  If a Symbol contains both "CAN" and "MSG" (case-insensitive), also emit:
     var <Symbol> <off>
  using the same offset format as for the main line.

- Offset formatting rules:
  If coming from "Hex" column  => use 0x<HEX>
  If coming from "Offset" col  => use "<dec>." (decimal with a trailing dot)

The script writes a single combined "config.hwtp" file.

Usage:
  python GenSymb_ConfigVRG.py /path/to/workbook.xlsx --out /path/to/config.hwtp
  python GenSymb_ConfigVRG.py /path/to/workbook.xlsx  (outputs to ./config.hwtp)

Author: Modified for VRG requirements
"""

import argparse
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set

import pandas as pd


# --------------------------- Helpers ---------------------------

def normalize_sheet_name(name: str) -> str:
    """Normalize a sheet name for equality checks: lower, strip, collapse spaces/underscores."""
    s = (name or "").strip().lower()
    s = re.sub(r"[\s_]+", " ", s)
    return s


def colmap(df: pd.DataFrame) -> Dict[str, str]:
    """Return a mapping from normalized column name -> real column name in df."""
    mapping = {}
    for c in df.columns:
        k = normalize_col(c)
        if k and k not in mapping:
            mapping[k] = c
    return mapping


def normalize_col(col: str) -> str:
    """Normalize a column header: lower, remove spaces/underscores/dots."""
    if col is None:
        return ""
    c = str(col).strip().lower()
    c = re.sub(r"[\s_.]+", "", c)
    return c


def best_col(cm: Dict[str, str], *candidates: str) -> Optional[str]:
    """Pick the first existing column (by normalized key) from candidates."""
    for cand in candidates:
        key = normalize_col(cand)
        if key in cm:
            return cm[key]
    return None


def as_str(v) -> str:
    if pd.isna(v):
        return ""
    return str(v).strip()


def normalize_symbol_name(name: str) -> str:
    """Replace spaces with underscores in symbol names."""
    return re.sub(r'\s+', '_', name.strip())


def parse_int_from_str(s: str, base: int) -> Optional[int]:
    try:
        return int(s, base)
    except Exception:
        return None


def parse_hex_cell(x) -> Optional[int]:
    """Parse a value coming from a 'Hex' column. Accepts forms like '48', '0x48', 'A', '0xa' etc."""
    if pd.isna(x):
        return None
    s = as_str(x)
    if s == "":
        return None
    s2 = s.lower()
    # if contains non-hex chars (except 0x), try to strip
    s2 = s2.replace("h", "")
    s2 = s2.replace("0x", "")
    s2 = s2.strip()
    if re.fullmatch(r"[0-9a-f]+", s2):
        return parse_int_from_str(s2, 16)
    # last resort: try pure int as decimal
    return parse_int_from_str(s, 10)


def parse_dec_cell(x) -> Optional[int]:
    """Parse a value coming from an 'Offset' column (decimal). Accept '8', '8.', '72d', etc."""
    if pd.isna(x):
        return None
    s = as_str(x).lower().strip()
    s = s.replace("d", "")
    s = s.replace(".", "")
    s = s.strip()
    if re.fullmatch(r"-?\d+", s):
        try:
            return int(s, 10)
        except Exception:
            return None
    return None


def fmt_off_from_hex(val: int) -> str:
    return f"0x{val:X}"


def fmt_off_from_dec(val: int) -> str:
    return f"{val}."


def is_pointer_type(sym: str) -> bool:
    """Check if a symbol is a pointer type (should use $$$$())."""
    # Pointer types typically end with _pu8, _pu16, _pu32, _pu, _ps, etc.
    return bool(re.search(r'_p[us]\d*$', sym, re.IGNORECASE))


def contains_ci(hay: str, needle: str) -> bool:
    return needle.lower() in (hay or "").lower()


def is_master_sheet(sheet_name: str) -> bool:
    return "master" in normalize_sheet_name(sheet_name)


def is_symbol_tables_sheet(sheet_name: str) -> bool:
    s = normalize_sheet_name(sheet_name)
    return s == "symbol tables" or s == "symbol table" or "symbol tables" in s


def is_standard_symbol_table_sheet(sheet_name: str) -> bool:
    s = normalize_sheet_name(sheet_name)
    return s == "standard symbol table" or "standard symbol table" in s


def section_header(title: str, width: int = 60) -> str:
    t = f" {title.strip()} "
    fill_total = max(width - len(t), 0)
    left = fill_total // 2
    right = fill_total - left
    return ";" + "=" * left + t + "=" * right


def extract_suffix_from_section_header(line: str) -> Optional[str]:
    """
    Extract project suffix from a section header line.
    E.g., ';==================== dio_g_DigIn_u8_DZC ====================' -> 'DZC'
          ';==================== pio_g_FreqIn_s_MAN ====================' -> 'MAN'
    
    Returns the suffix if it's 2-4 uppercase characters after the last underscore.
    Returns None if no valid suffix found.
    """
    # Extract the section name between the equals signs
    match = re.search(r';=+\s*(.+?)\s*=+', line)
    if not match:
        return None
    
    section_name = match.group(1).strip()
    
    # Split by underscore and get the last part
    parts = section_name.split('_')
    if len(parts) < 2:
        return None
    
    last_part = parts[-1].strip()
    
    # Check if it's 2-4 characters and ALL uppercase (strict check)
    if 2 <= len(last_part) <= 4 and last_part.isupper():
        return last_part
    
    return None


def get_base_sheet_name(sheet_name: str, suffix: str) -> str:
    """
    Get the base name without the project suffix.
    E.g., 'dio_g_DigIn_u8_MAN' with suffix 'MAN' -> 'dio_g_DigIn_u8'
    """
    if suffix and sheet_name.endswith(f"_{suffix}"):
        return sheet_name[:-len(suffix)-1]
    return sheet_name


def is_common_sheet(sheet_name: str) -> bool:
    """
    Check if a sheet is common to all projects (no project suffix).
    Common sheets: Master, Symbol Tables, Standard Symbol Table, Struct definitions, etc.
    """
    if is_master_sheet(sheet_name):
        return True
    if is_symbol_tables_sheet(sheet_name):
        return True
    if is_standard_symbol_table_sheet(sheet_name):
        return True
    # Check for sheets without project suffixes - not used anymore
    return False


@dataclass
class Context:
    master_symbol: Optional[str] = None
    std_symtab_ref: Optional[str] = None  # e.g., main_c_SymtabStd_u32
    defined_symbols: set = None  # Set of all defined symbols
    
    def __post_init__(self):
        if self.defined_symbols is None:
            self.defined_symbols = set()


# --------------------------- Processors ---------------------------

def process_master(df: pd.DataFrame, ctx: Context) -> List[str]:
    lines: List[str] = []
    cm = colmap(df)
    c_symbol = best_col(cm, "Symbol")
    c_addr = best_col(cm, "Address", "Adress")  # tolerate misspelling
    if not c_symbol or not c_addr:
        return lines  # nothing to do

    # Determine master symbol (prefer row whose symbol contains SymMaster)
    candidate_master = None
    first_symbol = None

    for _, row in df.iterrows():
        sym = as_str(row.get(c_symbol))
        addr_raw = as_str(row.get(c_addr))
        if not sym or not addr_raw:
            continue

        # Pick first non-empty for fallback
        if first_symbol is None:
            first_symbol = sym

        if contains_ci(sym, "SymMaster") and candidate_master is None:
            candidate_master = sym

        # Normalize address: ensure 0x prefix if looks like hex/decimal
        addr = addr_raw.strip()
        if re.fullmatch(r"0x[0-9A-Fa-f]+", addr):
            addr_fmt = addr.upper()
        elif re.fullmatch(r"[0-9A-Fa-f]+", addr):
            # assume hex if letters A-F appear; else assume decimal
            if re.search(r"[A-Fa-f]", addr):
                addr_fmt = f"0x{addr.upper()}"
            else:
                # decimal -> convert to hex with 0x
                try:
                    dec = int(addr, 10)
                    addr_fmt = f"0x{dec:X}"
                except Exception:
                    addr_fmt = addr  # fallback
        else:
            # keep as-is
            addr_fmt = addr

        lines.append(f"wo32 {sym:<28} {addr_fmt}")

    # set ctx.master_symbol
    ctx.master_symbol = candidate_master or first_symbol
    # Add master symbol to defined symbols
    if ctx.master_symbol:
        ctx.defined_symbols.add(ctx.master_symbol)
    return lines


def process_symbol_tables(df: pd.DataFrame, ctx: Context) -> List[str]:
    lines: List[str] = []
    cm = colmap(df)
    c_sym = best_col(cm, "Symbol")  # Symbol este numele să-l scriem
    c_ref = best_col(cm, "Reference")  # Reference este baza (main_c_SymMaster_u32)
    c_off = best_col(cm, "Offset")

    if not c_sym or not c_ref or not c_off or not ctx.master_symbol:
        return lines

    for _, row in df.iterrows():
        sym = as_str(row.get(c_sym))
        ref = as_str(row.get(c_ref))
        if not sym or not ref:
            continue
        off_dec = parse_dec_cell(row.get(c_off))
        if off_dec is None:
            continue
        off_fmt = fmt_off_from_dec(off_dec)

        # Detect standard symtab reference
        if ctx.std_symtab_ref is None and re.search(r"symtabstd", sym, flags=re.IGNORECASE):
            ctx.std_symtab_ref = sym

        # Add symbol to defined symbols
        ctx.defined_symbols.add(sym)
        
        lines.append(f"wo32 {sym:<28} $$$$({ref} +  {off_fmt})")
    return lines


def process_standard_symbol_table(df: pd.DataFrame, ctx: Context) -> List[str]:
    lines: List[str] = []
    if not ctx.std_symtab_ref:
        # We cannot format without knowing the std symtab ref; skip gracefully.
        return lines

    cm = colmap(df)
    c_sym = best_col(cm, "Symbol")
    c_hex = best_col(cm, "Hex")
    c_off = best_col(cm, "Offset")
    if not c_sym or not (c_hex or c_off):
        return lines

    for _, row in df.iterrows():
        sym_raw = as_str(row.get(c_sym))
        if not sym_raw:
            continue

        # Normalize symbol name (replace spaces with underscores)
        sym = normalize_symbol_name(sym_raw)

        val_int = None
        val_src = None
        if c_hex:
            v = parse_hex_cell(row.get(c_hex))
            if v is not None:
                val_int = v
                val_src = "hex"
        if val_int is None and c_off:
            v = parse_dec_cell(row.get(c_off))
            if v is not None:
                val_int = v
                val_src = "dec"
        if val_int is None:
            continue

        off_fmt = fmt_off_from_hex(val_int) if val_src == "hex" else fmt_off_from_dec(val_int)
        
        # Add symbol to defined symbols
        ctx.defined_symbols.add(sym)
        
        lines.append(f"wo32 {sym:<28} $$$$({ctx.std_symtab_ref} +  {off_fmt})")
    return lines


def op_for_size(size: int) -> Optional[str]:
    if size == 1:
        return "by"
    if size == 2:
        return "wo16"
    if size == 4:
        return "wo32"
    return None  # handled separately for multi-word


def needs_split_words(size: int) -> int:
    """Return number of 32-bit words if splitting is required; otherwise 0."""
    if size and size % 4 == 0 and size > 4:
        return size // 4
    return 0


def process_generic(df: pd.DataFrame, ctx: Context = None) -> List[str]:
    lines: List[str] = []
    cm = colmap(df)
    c_sym = best_col(cm, "Symbol")
    c_ref = best_col(cm, "Reference")
    c_size = best_col(cm, "Size", "SizeBytes", "Size(Bytes)")
    c_hex = best_col(cm, "Hex")
    c_off = best_col(cm, "Offset")

    if not c_sym or not c_ref or not c_size or not (c_hex or c_off):
        return lines

    for _, row in df.iterrows():
        sym_raw = as_str(row.get(c_sym))
        base_raw = as_str(row.get(c_ref))
        if not sym_raw or not base_raw:
            continue

        # Normalize symbol name (replace spaces with underscores)
        sym = normalize_symbol_name(sym_raw)
        base = normalize_symbol_name(base_raw)
        
        # Detect circular reference (symbol references itself)
        # This happens when Excel has errors like psu_g_Control_b16 -> psu_g_Control_b16
        # Skip these entries as they are invalid
        if sym == base:
            continue
        
        # Check if base symbol is defined (exists in context)
        # If not, skip this entry to avoid "Error : ???" in ISODiag
        if ctx and base not in ctx.defined_symbols:
            continue

        # size
        size_raw = row.get(c_size)
        try:
            size = int(str(size_raw).strip().split()[0])
        except Exception:
            # try to infer from symbol suffix (_u8, _u16, _u32) if Size missing/bad
            m = re.search(r"_u(8|16|32)\b", sym, flags=re.IGNORECASE)
            if m:
                size = int(m.group(1)) // 8 if int(m.group(1)) in (8, 16, 32) else 4
            else:
                # default to 4 bytes
                size = 4

        # offset
        off_int = None
        off_src = None  # 'hex' or 'dec'
        if c_hex:
            v = parse_hex_cell(row.get(c_hex))
            if v is not None:
                off_int = v
                off_src = "hex"
        if off_int is None and c_off:
            v = parse_dec_cell(row.get(c_off))
            if v is not None:
                off_int = v
                off_src = "dec"
        if off_int is None:
            continue

        # prepare formatter for offsets
        def fmt_off(v: int) -> str:
            return fmt_off_from_hex(v) if off_src == "hex" else fmt_off_from_dec(v)

        # Check if this symbol is a pointer type OR if the base reference is a pointer type
        # If either is true, we need to use $$$$() for address indirection
        use_dollar_wrapper = is_pointer_type(sym) or is_pointer_type(base)

        # simple sizes
        op = op_for_size(size)
        if op:
            # Use $$$$() wrapper for pointer types or when referencing through pointers
            if use_dollar_wrapper:
                lines.append(f"{op:<4} {sym:<28} $$$$({base} +  {fmt_off(off_int)})")
            else:
                lines.append(f"{op:<4} {sym:<28} {base} +  {fmt_off(off_int)}")

            # CAN+MSG additional rule (emit VAR line with same offset format)
            if re.search(r"can", sym, re.IGNORECASE) and re.search(r"msg", sym, re.IGNORECASE):
                lines.append(f"var  {sym:<28} {fmt_off(off_int)}")

            # Add symbol to defined symbols so it can be referenced by other symbols
            if ctx:
                ctx.defined_symbols.add(sym)

            continue

        # multi-word (size % 4 == 0 and > 4)
        words = needs_split_words(size)
        if words > 0:
            # First, declare the base symbol (without suffix) so it can be referenced
            lines.append(f"wo32 {sym:<28} {base} +  {fmt_off(off_int)}")
            
            # Add base symbol to defined symbols
            if ctx:
                ctx.defined_symbols.add(sym)
            
            # naming strategy:
            #  - if words == 2 -> _low, _high
            #  - else -> _w0, _w1, ...
            for i in range(words):
                if words == 2:
                    suffix = "_low" if i == 0 else "_high"
                else:
                    suffix = f"_w{i}"
                sym_i = f"{sym}{suffix}"
                off_i = off_int + 4 * i
                if off_src == "hex":
                    # also add a nice decimal comment
                    dec_comment = f" ; {off_i}d"
                    lines.append(f"wo32 {sym_i:<28} {base} +  {fmt_off(off_i)}{dec_comment}")
                else:
                    lines.append(f"wo32 {sym_i:<28} {base} +  {fmt_off(off_i)}")
                
                # Add split symbol to defined symbols
                if ctx:
                    ctx.defined_symbols.add(sym_i)

            # CAN+MSG rule for base symbol (one VAR at base offset)
            if re.search(r"can", sym, re.IGNORECASE) and re.search(r"msg", sym, re.IGNORECASE):
                lines.append(f"var  {sym:<28} {fmt_off(off_int)}")

    return lines


# --------------------------- Orchestrator ---------------------------

def generate_from_excel(xlsx_path: str) -> Tuple[str, Dict[str, List[str]]]:
    """
    Returns:
      combined_text (str)
      per_sheet_lines: dict of sheet_name -> list(lines)
    """
    xls = pd.ExcelFile(xlsx_path, engine="openpyxl")
    sheet_names = xls.sheet_names

    ctx = Context()

    # First pass: find master symbol + build "Master" and "Symbol Tables" right away
    per_sheet: Dict[str, List[str]] = {}

    # Capture "Master" + "Symbol Tables" first
    for sname in sheet_names:
        df = xls.parse(sname, dtype=object)
        if is_master_sheet(sname):
            lines = [section_header(sname)]
            lines += process_master(df, ctx)
            per_sheet[sname] = lines
        elif is_symbol_tables_sheet(sname):
            lines = [section_header(sname)]
            lines += process_symbol_tables(df, ctx)
            per_sheet[sname] = lines

    # Second pass: process "Standard Symbol Table" and others
    for sname in sheet_names:
        if sname in per_sheet:
            continue
        df = xls.parse(sname, dtype=object)
        if is_standard_symbol_table_sheet(sname):
            lines = [section_header(sname)]
            lines += process_standard_symbol_table(df, ctx)
            per_sheet[sname] = lines
        else:
            # generic - process all sheets even if they produce no output
            lines = [section_header(sname)]
            glines = process_generic(df, ctx)
            lines += glines  # Add even if empty to preserve sheet structure
            per_sheet[sname] = lines

    # Combine in original Excel sheet order
    combined_lines: List[str] = []
    for s in sheet_names:
        combined_lines.extend(per_sheet.get(s, []))

    combined_text = "\n".join(combined_lines) + "\n"
    return combined_text, per_sheet


def generate_multi_configs(xlsx_path: str, output_dir: str, base_name: str = "config"):
    """
    Generate multiple config files by analyzing the generated master config.
    
    Process:
    1. Generate complete master config with all symbols
    2. Analyze master config to identify project suffixes (DZC, MAN, TRT, etc.)
    3. For each suffix, create a config containing:
       - All general blocks (without suffix)
       - Only blocks with that specific suffix
       - Excluding blocks with other suffixes
    """
    # Step 1: Generate complete master config
    print("[INFO] Generating master config...")
    combined_text, _ = generate_from_excel(xlsx_path)
    
    # Write master config
    master_path = os.path.join(output_dir, f"{base_name}.hwtp")
    os.makedirs(output_dir, exist_ok=True)
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(combined_text)
    print(f"[OK] Master config generated: {master_path}")
    
    # Step 2: Analyze master config to find suffixes and categorize sections
    lines = combined_text.split('\n')
    suffixes_found = set()
    sections = []  # List of (header_line, suffix_or_none, section_lines)
    
    current_section_header = None
    current_section_suffix = None
    current_section_lines = []
    
    for line in lines:
        # Check if this is a section header
        if line.startswith(';='):
            # Save previous section if exists
            if current_section_header is not None:
                sections.append((current_section_header, current_section_suffix, current_section_lines[:]))
            
            # Start new section
            current_section_header = line
            current_section_suffix = extract_suffix_from_section_header(line)
            current_section_lines = [line]
            
            # Track suffix
            if current_section_suffix:
                suffixes_found.add(current_section_suffix)
        else:
            # Add line to current section
            if current_section_header is not None:
                current_section_lines.append(line)
    
    # Don't forget the last section
    if current_section_header is not None:
        sections.append((current_section_header, current_section_suffix, current_section_lines))
    
    # If no suffixes found, we're done
    if not suffixes_found:
        print("[INFO] No project suffixes detected in master config.")
        return
    
    print(f"[INFO] Detected {len(suffixes_found)} project variants: {', '.join(sorted(suffixes_found))}")
    
    # Step 3: Generate config for each suffix
    for suffix in sorted(suffixes_found):
        output_path = os.path.join(output_dir, f"{base_name}_{suffix}.hwtp")
        print(f"[INFO] Generating {base_name}_{suffix}.hwtp...")
        
        config_lines = []
        for header, section_suffix, section_lines in sections:
            # Include if:
            # - Section has no suffix (general block) OR
            # - Section has THIS suffix
            if section_suffix is None or section_suffix == suffix:
                config_lines.extend(section_lines)
        
        # Write config
        with open(output_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(config_lines))
        
        print(f"[OK] Generated: {output_path}")


def write_outputs(out_dir: str, combined_text: str, per_sheet_lines: Dict[str, List[str]], one_file: bool, per_sheet: bool):
    # Deprecated - kept for compatibility but not used anymore
    pass


def main():
    ap = argparse.ArgumentParser(description="Generate .hwtp config from Excel workbook.")
    ap.add_argument("excel", help="Path to the Excel workbook (.xlsx)")
    ap.add_argument("--out", "-o", default="./config.hwtp", help="Output file path (default: ./config.hwtp)")
    ap.add_argument("--multi", action="store_true", help="Generate multiple configs based on sheet name suffixes (e.g., MAN, DZC)")
    args = ap.parse_args()

    xlsx_path = args.excel
    out_path = args.out

    if args.multi:
        # Multi-config mode: generate separate configs for each project suffix
        out_dir = os.path.dirname(out_path) or "."
        base_name = os.path.splitext(os.path.basename(out_path))[0]
        generate_multi_configs(xlsx_path, out_dir, base_name)
    else:
        # Single config mode (original behavior)
        combined_text, per_sheet_lines = generate_from_excel(xlsx_path)

        # Write single combined file
        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(combined_text)

        # Summary
        print(f"[OK] Generated config from: {xlsx_path}")
        print(f" - Output file: {out_path}")


if __name__ == "__main__":
    main()
