#!/usr/bin/env python3
"""
XLSX → LLM-friendly exports (stdlib-only).

Outputs:
- workbook.json (sheet list + export metadata)
- sheets/<sheet_slug>/grid.csv (rectangular used-range grid of values)
- sheets/<sheet_slug>/cells.jsonl (one JSON record per populated cell: value/type/formula/style/date)
- sheets/<sheet_slug>/sheet.json (sheet-level metadata)

Design goals:
- Deterministic filenames (slugified sheet names)
- Preserve both computed values and formulas (when present)
- Provide typed values where possible (number/bool/string/date)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple
import xml.etree.ElementTree as ET


NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


_A1_RE = re.compile(r"^([A-Z]+)([0-9]+)$")


def slugify(name: str) -> str:
    s = name.strip().lower()
    # German + common diacritics
    s = (
        s.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
        .replace("á", "a")
        .replace("à", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
    )
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "sheet"


def a1_to_rc(a1: str) -> Tuple[int, int]:
    """
    Convert A1 reference to 1-based (row, col).
    """
    m = _A1_RE.match(a1)
    if not m:
        raise ValueError(f"Unsupported cell reference: {a1!r}")
    letters, row_s = m.group(1), m.group(2)
    col = 0
    for ch in letters:
        col = col * 26 + (ord(ch) - ord("A") + 1)
    return int(row_s), col


def rc_to_a1(row: int, col: int) -> str:
    """
    Convert 1-based (row, col) to A1 reference.
    """
    if row < 1 or col < 1:
        raise ValueError(f"Invalid rc: {(row, col)}")
    letters = []
    x = col
    while x:
        x, rem = divmod(x - 1, 26)
        letters.append(chr(ord("A") + rem))
    return "".join(reversed(letters)) + str(row)


def parse_range(ref: str) -> Tuple[int, int, int, int]:
    """
    Parse Excel range like "A1:D10" or single cell "B2".
    Returns (min_row, min_col, max_row, max_col) all 1-based inclusive.
    """
    if ":" in ref:
        a, b = ref.split(":", 1)
        r1, c1 = a1_to_rc(a)
        r2, c2 = a1_to_rc(b)
        return min(r1, r2), min(c1, c2), max(r1, r2), max(c1, c2)
    r, c = a1_to_rc(ref)
    return r, c, r, c


def excel_serial_to_datetime(serial: float) -> datetime:
    """
    Convert Excel 1900-date-system serial to datetime (UTC, naive-to-UTC).
    Handles Excel's 1900 leap year bug by subtracting one day for serial >= 60.
    """
    days = int(serial)
    frac = float(serial) - days
    if days >= 60:
        days -= 1
    base = datetime(1899, 12, 31, tzinfo=timezone.utc)
    dt = base + timedelta(days=days, seconds=round(frac * 86400))
    return dt


def is_likely_date_format(num_fmt_id: Optional[int], fmt_code: Optional[str]) -> bool:
    """
    Heuristic date/time format detection.
    """
    if num_fmt_id is None:
        return False
    # Built-in Excel date/time formats commonly used
    if num_fmt_id in {14, 15, 16, 17, 18, 19, 20, 21, 22, 45, 46, 47}:
        return True
    if fmt_code:
        c = fmt_code.lower()
        # Avoid treating elapsed-time formats like "[h]" as dates.
        if "[h]" in c or "[m]" in c or "[s]" in c:
            return False
        return any(tok in c for tok in ("yy", "yyyy", "mm", "dd", "hh", "ss"))
    return False


def read_xml(z: zipfile.ZipFile, name: str) -> Optional[ET.Element]:
    try:
        data = z.read(name)
    except KeyError:
        return None
    return ET.fromstring(data)


def parse_shared_strings(z: zipfile.ZipFile) -> List[str]:
    root = read_xml(z, "xl/sharedStrings.xml")
    if root is None:
        return []
    out: List[str] = []
    for si in root.findall("m:si", NS):
        # sharedStrings can contain rich text: multiple <t> nodes
        parts = []
        for t in si.findall(".//m:t", NS):
            parts.append(t.text or "")
        out.append("".join(parts))
    return out


@dataclass(frozen=True)
class Styles:
    cell_xfs_num_fmt_id: List[int]
    num_fmts: Dict[int, str]

    def get_num_fmt(self, style_idx: Optional[int]) -> Tuple[Optional[int], Optional[str]]:
        if style_idx is None:
            return None, None
        if style_idx < 0 or style_idx >= len(self.cell_xfs_num_fmt_id):
            return None, None
        num_fmt_id = self.cell_xfs_num_fmt_id[style_idx]
        return num_fmt_id, self.num_fmts.get(num_fmt_id)


def parse_styles(z: zipfile.ZipFile) -> Styles:
    root = read_xml(z, "xl/styles.xml")
    if root is None:
        return Styles(cell_xfs_num_fmt_id=[0], num_fmts={})

    # Custom number formats live in <numFmts><numFmt numFmtId="165" formatCode="..."/>
    num_fmts: Dict[int, str] = {}
    num_fmts_node = root.find("m:numFmts", NS)
    if num_fmts_node is not None:
        for nf in num_fmts_node.findall("m:numFmt", NS):
            try:
                i = int(nf.attrib.get("numFmtId", "0"))
            except ValueError:
                continue
            code = nf.attrib.get("formatCode")
            if code is not None:
                num_fmts[i] = code

    # Cell formats are in <cellXfs><xf numFmtId="..."/>
    cell_xfs_num_fmt_id: List[int] = []
    cell_xfs = root.find("m:cellXfs", NS)
    if cell_xfs is not None:
        for xf in cell_xfs.findall("m:xf", NS):
            try:
                cell_xfs_num_fmt_id.append(int(xf.attrib.get("numFmtId", "0")))
            except ValueError:
                cell_xfs_num_fmt_id.append(0)
    if not cell_xfs_num_fmt_id:
        cell_xfs_num_fmt_id = [0]

    return Styles(cell_xfs_num_fmt_id=cell_xfs_num_fmt_id, num_fmts=num_fmts)


def parse_workbook_sheets(z: zipfile.ZipFile) -> List[Tuple[str, str]]:
    """
    Returns list of (sheet_name, worksheet_xml_path).
    """
    wb = read_xml(z, "xl/workbook.xml")
    rels = read_xml(z, "xl/_rels/workbook.xml.rels")
    if wb is None or rels is None:
        raise RuntimeError("Invalid XLSX: missing workbook.xml or workbook.xml.rels")

    rid_to_target: Dict[str, str] = {}
    # workbook.xml.rels uses a different default namespace
    rels_ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    for rel in rels.findall("r:Relationship", rels_ns):
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if rid and target:
            # Targets are relative to xl/
            rid_to_target[rid] = "xl/" + target.lstrip("/")

    sheets: List[Tuple[str, str]] = []
    for s in wb.findall(".//m:sheets/m:sheet", NS):
        name = s.attrib.get("name") or "Sheet"
        rid = s.attrib.get(f"{{{NS['r']}}}id")
        if rid and rid in rid_to_target:
            sheets.append((name, rid_to_target[rid]))
    return sheets


def cell_value_from_xml(
    c: ET.Element,
    shared_strings: List[str],
    styles: Styles,
) -> Dict[str, Any]:
    """
    Extract value + typing from a <c> cell element.
    """
    a1 = c.attrib.get("r")
    t = c.attrib.get("t")  # s, b, str, inlineStr
    s_raw = c.attrib.get("s")
    style_idx = int(s_raw) if s_raw and s_raw.isdigit() else None

    f_node = c.find("m:f", NS)
    v_node = c.find("m:v", NS)
    is_node = c.find("m:is", NS)

    formula = (f_node.text or "").strip() if f_node is not None and f_node.text else None
    raw_v = (v_node.text or "") if v_node is not None else ""

    num_fmt_id, fmt_code = styles.get_num_fmt(style_idx)

    if t == "s":
        # shared string table index
        try:
            idx = int(raw_v)
            val = shared_strings[idx] if 0 <= idx < len(shared_strings) else ""
        except ValueError:
            val = ""
        return {
            "a1": a1,
            "value_type": "string",
            "value": val,
            "raw": raw_v,
            "formula": formula,
            "style_idx": style_idx,
            "num_fmt_id": num_fmt_id,
            "num_fmt_code": fmt_code,
        }

    if t == "inlineStr":
        parts = []
        if is_node is not None:
            for tn in is_node.findall(".//m:t", NS):
                parts.append(tn.text or "")
        return {
            "a1": a1,
            "value_type": "string",
            "value": "".join(parts),
            "raw": raw_v,
            "formula": formula,
            "style_idx": style_idx,
            "num_fmt_id": num_fmt_id,
            "num_fmt_code": fmt_code,
        }

    if t == "b":
        val = True if raw_v == "1" else False
        return {
            "a1": a1,
            "value_type": "boolean",
            "value": val,
            "raw": raw_v,
            "formula": formula,
            "style_idx": style_idx,
            "num_fmt_id": num_fmt_id,
            "num_fmt_code": fmt_code,
        }

    if t == "str":
        # result of formula as string
        return {
            "a1": a1,
            "value_type": "string",
            "value": raw_v,
            "raw": raw_v,
            "formula": formula,
            "style_idx": style_idx,
            "num_fmt_id": num_fmt_id,
            "num_fmt_code": fmt_code,
        }

    # Default: numeric (or empty)
    if raw_v == "":
        return {
            "a1": a1,
            "value_type": "empty",
            "value": None,
            "raw": raw_v,
            "formula": formula,
            "style_idx": style_idx,
            "num_fmt_id": num_fmt_id,
            "num_fmt_code": fmt_code,
        }

    try:
        num = float(raw_v)
    except ValueError:
        return {
            "a1": a1,
            "value_type": "string",
            "value": raw_v,
            "raw": raw_v,
            "formula": formula,
            "style_idx": style_idx,
            "num_fmt_id": num_fmt_id,
            "num_fmt_code": fmt_code,
        }

    out: Dict[str, Any] = {
        "a1": a1,
        "value_type": "number",
        "value": int(num) if num.is_integer() else num,
        "raw": raw_v,
        "formula": formula,
        "style_idx": style_idx,
        "num_fmt_id": num_fmt_id,
        "num_fmt_code": fmt_code,
    }

    if is_likely_date_format(num_fmt_id, fmt_code):
        dt = excel_serial_to_datetime(num)
        # include time only if non-midnight
        iso = dt.isoformat().replace("+00:00", "Z")
        out["value_type"] = "date"
        out["value_iso8601"] = iso
        out["value"] = iso

    return out


def iter_sheet_cells(
    sheet_root: ET.Element,
    shared_strings: List[str],
    styles: Styles,
) -> Iterable[Dict[str, Any]]:
    for c in sheet_root.findall(".//m:sheetData/m:row/m:c", NS):
        a1 = c.attrib.get("r")
        if not a1:
            continue
        rec = cell_value_from_xml(c, shared_strings=shared_strings, styles=styles)
        row, col = a1_to_rc(a1)
        rec["row"] = row
        rec["col"] = col
        rec["col_a1"] = rc_to_a1(1, col).rstrip("1")
        yield rec


def export_sheet(
    *,
    z: zipfile.ZipFile,
    sheet_name: str,
    sheet_xml_path: str,
    out_dir: str,
    shared_strings: List[str],
    styles: Styles,
) -> Dict[str, Any]:
    root = read_xml(z, sheet_xml_path)
    if root is None:
        raise RuntimeError(f"Missing worksheet xml: {sheet_xml_path}")

    dimension_node = root.find("m:dimension", NS)
    dim_ref = dimension_node.attrib.get("ref") if dimension_node is not None else None

    cells = list(iter_sheet_cells(root, shared_strings=shared_strings, styles=styles))
    cell_count = len(cells)

    if dim_ref:
        min_r, min_c, max_r, max_c = parse_range(dim_ref)
    else:
        if cells:
            min_r = min(c["row"] for c in cells)
            min_c = min(c["col"] for c in cells)
            max_r = max(c["row"] for c in cells)
            max_c = max(c["col"] for c in cells)
        else:
            min_r = min_c = max_r = max_c = 1

    sheet_slug = slugify(sheet_name)
    sheet_out = os.path.join(out_dir, "sheets", sheet_slug)
    os.makedirs(sheet_out, exist_ok=True)

    # Write cells.jsonl
    cells_path = os.path.join(sheet_out, "cells.jsonl")
    with open(cells_path, "w", encoding="utf-8") as f:
        for rec in cells:
            rec2 = dict(rec)
            rec2["sheet_name"] = sheet_name
            rec2["sheet_slug"] = sheet_slug
            f.write(json.dumps(rec2, ensure_ascii=False) + "\n")

    # Build a sparse lookup for grid export
    by_rc: Dict[Tuple[int, int], Dict[str, Any]] = {(c["row"], c["col"]): c for c in cells}

    # Write grid.csv (values only)
    grid_path = os.path.join(sheet_out, "grid.csv")
    with open(grid_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        header = ["_row"] + [rc_to_a1(1, c).rstrip("1") for c in range(min_c, max_c + 1)]
        w.writerow(header)
        for r in range(min_r, max_r + 1):
            row_vals: List[Any] = [r]
            for c in range(min_c, max_c + 1):
                rec = by_rc.get((r, c))
                if not rec or rec.get("value_type") == "empty":
                    row_vals.append("")
                else:
                    v = rec.get("value")
                    row_vals.append("" if v is None else v)
            w.writerow(row_vals)

    sheet_meta = {
        "sheet_name": sheet_name,
        "sheet_slug": sheet_slug,
        "source_xml": sheet_xml_path,
        "dimension_ref": dim_ref,
        "used_range": {
            "min_row": min_r,
            "min_col": min_c,
            "max_row": max_r,
            "max_col": max_c,
            "a1": f"{rc_to_a1(min_r, min_c)}:{rc_to_a1(max_r, max_c)}",
        },
        "cell_count": cell_count,
        "artifacts": {
            "grid_csv": os.path.relpath(grid_path, out_dir),
            "cells_jsonl": os.path.relpath(cells_path, out_dir),
        },
        "notes": {
            "date_detection": "Heuristic based on numFmtId and/or formatCode; see value_type=date + value_iso8601.",
        },
    }
    with open(os.path.join(sheet_out, "sheet.json"), "w", encoding="utf-8") as f:
        json.dump(sheet_meta, f, ensure_ascii=False, indent=2)

    return sheet_meta


def main() -> int:
    p = argparse.ArgumentParser(description="Export XLSX into LLM-friendly CSV/JSON artifacts (stdlib-only).")
    p.add_argument("xlsx_path", help="Path to .xlsx")
    p.add_argument(
        "--out",
        required=True,
        help="Output directory (will be created). Recommended: business/financing/Gründungszuschuss/llm_exports/business-case-sheet/",
    )
    args = p.parse_args()

    xlsx_path = os.path.abspath(args.xlsx_path)
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    exported_at = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")

    with zipfile.ZipFile(xlsx_path) as z:
        shared_strings = parse_shared_strings(z)
        styles = parse_styles(z)
        sheets = parse_workbook_sheets(z)

        sheet_metas: List[Dict[str, Any]] = []
        for sheet_name, sheet_xml in sheets:
            sheet_metas.append(
                export_sheet(
                    z=z,
                    sheet_name=sheet_name,
                    sheet_xml_path=sheet_xml,
                    out_dir=out_dir,
                    shared_strings=shared_strings,
                    styles=styles,
                )
            )

    workbook = {
        "source": {
            "xlsx_path": xlsx_path,
            "xlsx_filename": os.path.basename(xlsx_path),
        },
        "export": {
            "exported_at_utc": exported_at,
            "tool": "business/financing/tools/xlsx_to_llm.py",
            "format_version": 1,
        },
        "sheets": sheet_metas,
    }
    with open(os.path.join(out_dir, "workbook.json"), "w", encoding="utf-8") as f:
        json.dump(workbook, f, ensure_ascii=False, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

