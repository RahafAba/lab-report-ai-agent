import re
import json
import pdfplumber
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class LabTest:
    panel: str
    test_name: str
    result: Optional[float]
    result_raw: str
    unit: str
    ref_low: Optional[float]
    ref_high: Optional[float]
    ref_raw: str
    flag: str
    confidence: float


def _clean(text):
    if not text:
        return ""
    # Arabic renders as "nnn" placeholders in some PDFs, strip them
    t = re.sub(r'\bn+\b', '', str(text))
    return " ".join(t.split()).strip()


def _parse_numeric(val):
    if not val:
        return None
    m = re.search(r"[-+]?\d+\.?\d*", str(val).replace(",", "."))
    return float(m.group()) if m else None


def _parse_range(ref):
    if not ref:
        return None, None
    ref = str(ref).replace("\u2013", "-").replace("\u2014", "-")
    m = re.match(r"([\d.]+)\s*-\s*([\d.]+)", ref)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"<\s*([\d.]+)", ref)
    if m:
        return None, float(m.group(1))
    m = re.search(r">\s*([\d.]+)", ref)
    if m:
        return float(m.group(1)), None
    return None, None


def _infer_flag(result, ref_low, ref_high, raw_flag):
    raw = str(raw_flag).upper() if raw_flag else ""

    # compute flag from math
    computed = "NORMAL"
    if result is not None:
        if ref_high and result > ref_high:
            computed = "HIGH"
        elif ref_low and result < ref_low:
            computed = "LOW"

    # read flag from PDF
    pdf_flag = "UNKNOWN"
    if ("H" in raw or "\u203a" in raw) and "LOW" not in raw and len(raw) < 6:
        pdf_flag = "HIGH"
    elif "FL" in raw or (raw.startswith("L") and len(raw) < 6):
        pdf_flag = "LOW"
    elif "NORMAL" in raw or not raw.strip():
        pdf_flag = "NORMAL"

    # confidence goes up when both sources agree
    if pdf_flag == computed and computed != "NORMAL":
        return computed, 0.97
    if pdf_flag == computed:
        return computed, 0.92
    if pdf_flag == "UNKNOWN":
        return computed, 0.78
    return pdf_flag, 0.65


# ordered by specificity so longer keys match before shorter ones
PANEL_MAP = [
    ("COMPLETE BLOOD COUNT", "Complete Blood Count"),
    ("COMPREHENSIVE METABOLIC", "Metabolic Panel"),
    ("METABOLIC PANEL", "Metabolic Panel"),
    ("LIPID PANEL", "Lipid Panel"),
    ("IRON STUDIES", "Iron Studies"),
    ("THYROID PANEL", "Thyroid Panel"),
    ("THYROID", "Thyroid Panel"),
    ("HORMONES", "Hormones"),
    ("VITAMINS & MINERALS", "Vitamins & Minerals"),
    ("VITAMINS", "Vitamins & Minerals"),
    ("INFLAMMATION MARKERS", "Inflammation Markers"),
    ("INFLAMMATION", "Inflammation Markers"),
    ("LIVER PANEL", "Liver Panel (Advanced)"),
    ("COAGULATION", "Coagulation"),
    ("CARDIAC MARKERS", "Cardiac Markers"),
    ("CARDIAC", "Cardiac Markers"),
    ("TUMOR MARKERS", "Tumor Markers"),
    ("HEPATITIS", "Hepatitis Panel"),
    ("DIABETES", "Diabetes Panel"),
    ("KIDNEY", "Kidney Panel"),
]


def _detect_panel(text):
    up = str(text).upper()
    for k, v in PANEL_MAP:
        if k in up:
            return v
    return None


def _is_header(row):
    if not row or not row[0]:
        return False
    first = re.sub(r'\bn+\b', '', str(row[0])).strip().lower()
    return re.match(r'^(test|desirable)\b', first) is not None


def _is_patient_row(row):
    if not row or not row[0]:
        return False
    return "/" in str(row[0]) and len(str(row[0])) > 25


def _patient_info(all_tables):
    info = {}
    for table in all_tables:
        if not table or not table[0] or len(table[0]) != 4:
            continue
        if "patient" not in str(table[0][0]).lower():
            continue
        for row in table:
            if not row or len(row) < 2:
                continue
            for i in range(0, min(len(row), 4), 2):
                lbl = _clean(str(row[i])) if row[i] else ""
                val = _clean(str(row[i + 1])) if i + 1 < len(row) and row[i + 1] else ""
                if not val:
                    continue
                ll = lbl.lower()
                if "patient name" in ll:    info["name"] = val
                elif "patient id" in ll:    info["id"] = val
                elif "date of birth" in ll: info["dob"] = val
                elif "gender" in ll:        info["gender"] = val.replace(" /", "").strip()
                elif "report date" in ll:   info["report_date"] = val
                elif "physician" in ll:     info["physician"] = val
                elif "clinical" in ll:      info["clinical_notes"] = val
    return info


def extract_from_pdf(pdf_path: str) -> dict:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    all_tests = []
    all_tables_flat = []

    last_known_panel = "General"

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            tables = page.extract_tables() or []

            # collect panel headers in the order they appear on the page
            page_panels = []
            for line in page_text.splitlines():
                p = _detect_panel(line)
                if p and len(line.strip()) < 100:
                    if not page_panels or page_panels[-1] != p:
                        page_panels.append(p)

            # first table on page 0 is usually the patient info block
            start_ti = 0
            if tables and tables[0] and len(tables[0]) > 0 and tables[0][0] and len(tables[0][0]) == 4:
                if tables[0][0][0] and "patient" in str(tables[0][0][0]).lower():
                    all_tables_flat.append(tables[0])
                    start_ti = 1

            # If page has no detected panels, infer from test names in the text
            if not page_panels:
                upper_text = page_text.upper()
                if any(k in upper_text for k in ["PROTHROMBIN", "FIBRINOGEN", "INR", " PT "]):
                    page_panels = ["Coagulation"]
                elif any(k in upper_text for k in ["TROPONIN", "BNP"]):
                    page_panels = ["Cardiac Markers"]

            data_tables = tables[start_ti:]
            for ti, table in enumerate(data_tables):
                if ti < len(page_panels):
                    panel = page_panels[ti]
                elif page_panels:
                    panel = page_panels[-1]
                else:
                    panel = last_known_panel
                last_known_panel = panel
                all_tables_flat.append(table)

                for row in table:
                    if not row or not any(row):
                        continue
                    if _is_header(row) or _is_patient_row(row):
                        continue
                    if len(row) < 4:
                        continue

                    name = _clean(str(row[0])) if row[0] else ""
                    if not name or len(name) < 2:
                        continue

                    result_raw = str(row[1]).strip() if row[1] else ""
                    unit       = _clean(str(row[2])) if row[2] else ""
                    ref_raw    = _clean(str(row[3])) if row[3] else ""
                    flag_raw   = _clean(str(row[4])) if len(row) > 4 and row[4] else ""

                    result_val = _parse_numeric(result_raw)
                    if result_val is None:
                        continue

                    ref_low, ref_high = _parse_range(ref_raw)
                    flag, conf = _infer_flag(result_val, ref_low, ref_high, flag_raw)

                    all_tests.append(LabTest(
                        panel=panel, test_name=name,
                        result=result_val, result_raw=result_raw,
                        unit=unit, ref_low=ref_low, ref_high=ref_high,
                        ref_raw=ref_raw, flag=flag, confidence=conf
                    ))

    patient_info  = _patient_info(all_tables_flat)
    panels_found  = list(dict.fromkeys(t.panel for t in all_tests))

    return {
        "patient_info":    patient_info,
        "tests":           [asdict(t) for t in all_tests],
        "total_extracted": len(all_tests),
        "source_file":     str(pdf_path),
        "panels_found":    panels_found,
        "abnormal_count":  sum(1 for t in all_tests if t.flag in ("HIGH", "LOW")),
        "normal_count":    sum(1 for t in all_tests if t.flag == "NORMAL"),
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_data/sample_blood_test.pdf"
    data = extract_from_pdf(path)
    print(json.dumps(data, indent=2, ensure_ascii=False))
