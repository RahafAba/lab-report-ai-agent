# Main entry point. Runs the four steps in sequence and writes the HTML report.

import sys, json, os, re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from step1_extract import extract_from_pdf
from step2_compare import analyze_tests
from step3_explain import generate_explanations
from step4_escalate import generate_escalation


def run_agent(pdf_path: str) -> dict:
    print(f"\n{'─'*55}")
    print(f"  Lab Report AI Agent")
    print(f"  File: {pdf_path}")
    print(f"{'─'*55}")

    print("  Step 1/4  Extracting lab values from PDF ...")
    extracted = extract_from_pdf(pdf_path)
    print(f"            {extracted['total_extracted']} tests extracted from {len(extracted['panels_found'])} panels")

    print("  Step 2/4  Comparing values to reference ranges ...")
    analysis = analyze_tests(extracted)
    s = analysis["summary"]
    print(f"            Normal: {s['normal']}  High: {s['high']}  Low: {s['low']}")

    print("  Step 3/4  Generating bilingual explanations ...")
    explained = generate_explanations(analysis)
    print(f"            Explanations ready for {len(explained['panels_order'])} panels")

    print("  Step 4/4  Running responsible AI checks ...")
    final = generate_escalation(explained)
    print(f"            Escalation level: {final['escalation_level'].upper()}")
    print(f"            Confidence: {final['confidence_report']['mean']:.0%} average")
    print(f"{'─'*55}")
    return final


def save_outputs(result: dict, pdf_path: str):
    os.makedirs("output", exist_ok=True)
    stem = Path(pdf_path).stem
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = f"output/{stem}_{ts}.json"
    json_out = {k: v for k, v in result.items() if k != "categories"}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_out, f, indent=2, ensure_ascii=False)

    html_path = f"output/{stem}_{ts}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(result))

    print(f"\n  JSON  {json_path}")
    print(f"  HTML  {html_path}")
    print(f"\n  Open the HTML file in your browser to view the report.")
    return json_path, html_path



HIJRI_MONTHS = ['محرم','صفر','ربيع الأول','ربيع الآخر','جمادى الأولى','جمادى الآخرة',
                'رجب','شعبان','رمضان','شوال','ذو القعدة','ذو الحجة']

def gregorian_to_hijri(year, month, day):
    """Convert Gregorian date to Hijri using the Kuwaiti algorithm."""
    if month < 3:
        year -= 1; month += 12
    a = int(year / 100)
    b = 2 - a + int(a / 4)
    jd = int(365.25*(year+4716)) + int(30.6001*(month+1)) + day + b - 1524
    l = jd - 1948440 + 10632
    n = int((l-1) / 10631)
    l = l - 10631*n + 354
    j = int((10985-l)/5316)*int(50*l/17719) + int(l/5670)*int(43*l/15238)
    l = l - int((30-j)/15)*int(17719*j/50) - int(j/16)*int(15238*j/43) + 29
    m = int(24*l/709)
    d = l - int(709*m/24)
    y = 30*n + j - 30
    return y, m, d

def to_arabic_numerals(n: int) -> str:
    """Convert integer to Arabic-Indic numerals."""
    eastern = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
    return str(n).translate(eastern)

def format_hijri(date_str: str) -> str:
    """Parse a date string like 2025-11-15 and return formatted Hijri date with Arabic numerals."""
    try:
        parts = date_str.strip().split("-")
        if len(parts) == 3:
            y, m, d = gregorian_to_hijri(int(parts[0]), int(parts[1]), int(parts[2]))
            return f"{to_arabic_numerals(d)} {HIJRI_MONTHS[m-1]} {to_arabic_numerals(y)} هـ"
    except Exception:
        pass
    return ""

def hijri_today() -> str:
    from datetime import date
    t = date.today()
    y, m, d = gregorian_to_hijri(t.year, t.month, t.day)
    return f"{to_arabic_numerals(d)} {HIJRI_MONTHS[m-1]} {to_arabic_numerals(y)} هـ"


FLAG_COLOR  = {"HIGH": "#b91c1c", "LOW": "#1d4ed8", "NORMAL": "#15803d"}
FLAG_BG     = {"HIGH": "#fef2f2", "LOW": "#eff6ff", "NORMAL": "#f0fdf4"}
FLAG_BORDER = {"HIGH": "#fecaca", "LOW": "#bfdbfe", "NORMAL": "#bbf7d0"}
SEV_COLOR   = {"significant": "#b91c1c", "moderate": "#c2410c", "mild": "#b45309", "normal": "#15803d", "unknown": "#6b7280"}
SEV_LABEL   = {"significant": "Significant", "moderate": "Moderate", "mild": "Mild", "normal": "Normal", "unknown": "Unknown"}

def _md(text: str) -> str:
    """Minimal markdown to HTML: **bold**, ## h2, ### h3, - list, --- hr."""
    lines = []
    for line in str(text).splitlines():
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        if line.startswith("### "): lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "): lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("- "): lines.append(f"<li>{line[2:]}</li>")
        elif line.startswith("---"): lines.append("<hr>")
        elif line.strip(): lines.append(f"<p>{line}</p>")
        else: lines.append("")
    return "\n".join(lines)

def _gauge(pos_pct, flag):
    pos = max(2, min(98, float(pos_pct or 50)))
    color = FLAG_COLOR.get(flag, "#6b7280")
    return f'<div class="gauge"><div class="gauge-fill"></div><div class="gauge-dot" style="left:{pos}%;background:{color}"></div></div>'

def _panel_rows(tests):
    rows = []
    for t in tests:
        flag = t["flag"]
        sev  = t.get("severity", "normal") if flag != "NORMAL" else "normal"
        fc   = FLAG_COLOR.get(flag, "#374151")
        fb   = FLAG_BG.get(flag, "#f9fafb")
        fbd  = FLAG_BORDER.get(flag, "#e5e7eb")
        sc   = SEV_COLOR.get(sev, "#6b7280")
        sl   = SEV_LABEL.get(sev, sev.title())
        flag_ar = {"HIGH": "مرتفع", "LOW": "منخفض", "NORMAL": "معدل طبيعي"}.get(flag, flag)
        name = t.get("full_name") or t["test_name"].split("—")[0].strip()
        rows.append(f"""
          <tr>
            <td class="td-name">
              <span class="test-name">{name}</span>
            </td>
            <td class="td-val" style="color:{fc};font-weight:600">{t['result_raw']} <span class="unit">{t['unit']}</span></td>
            <td class="td-range">{t['ref_raw']}</td>
            <td><span class="flag-pill" style="color:{fc};background:{fb};border-color:{fbd}">{flag_ar}</span></td>
            <td style="color:{sc};font-size:.82rem;font-weight:500">{sl}</td>
            <td class="td-gauge">{_gauge(t.get('position_pct',50), flag)}</td>
            <td class="td-conf">{t['confidence']:.0%}</td>
          </tr>""")
    return "".join(rows)

def _panel_section(panel, ptests, en_text, ar_text):
    return f"""
    <section class="panel">
      <div class="panel-header">{panel}</div>
      <div class="panel-body">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Test</th><th>Result</th><th>Normal Range</th>
                <th>Flag / النتيجة</th><th>Severity</th><th>Position</th><th>Confidence</th>
              </tr>
            </thead>
            <tbody>{_panel_rows(ptests)}</tbody>
          </table>
        </div>
        <div class="explain-grid">
          <div class="explain-card">
            <div class="lang-label">English Explanation</div>
            <div class="explain-text">{_md(en_text)}</div>
          </div>
          <div class="explain-card">
            <div class="lang-label">التوضيح</div>
            <div class="explain-text rtl">{_md(ar_text)}</div>
          </div>
        </div>
      </div>
    </section>"""

def build_html(r: dict) -> str:
    patient  = r.get("patient_info", {})
    summary  = r.get("summary", {})
    tests    = r.get("tests", [])
    panels_o = r.get("panels_order", [])
    conf     = r.get("confidence_report", {})
    ts       = r.get("report_timestamp", "")
    esc_lvl  = r.get("escalation_level", "all_normal")
    sev_c    = r.get("severity_counts", {})

    panels = {p: [t for t in tests if t["panel"] == p] for p in panels_o}
    panel_html = "".join(
        _panel_section(p, panels[p],
                       r.get("panels_en",{}).get(p,""),
                       r.get("panels_ar",{}).get(p,""))
        for p in panels_o
    )

    esc_colors = {"urgent":"#b91c1c","schedule":"#c2410c","monitor":"#b45309","all_normal":"#15803d"}
    esc_bg     = {"urgent":"#fef2f2","schedule":"#fff7ed","monitor":"#fffbeb","all_normal":"#f0fdf4"}
    esc_border = {"urgent":"#fecaca","schedule":"#fed7aa","monitor":"#fde68a","all_normal":"#bbf7d0"}
    ec = esc_colors.get(esc_lvl, "#6b7280")
    eb = esc_bg.get(esc_lvl, "#f9fafb")
    ebd= esc_border.get(esc_lvl, "#e5e7eb")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Lab Report — {patient.get('name','Patient')}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {{
    --sand:    #faf7f2;
    --cream:   #f5f0e8;
    --teal:    #0f766e;
    --teal-d:  #0d5f59;
    --teal-l:  #e6f4f3;
    --navy:    #1e3a4a;
    --slate:   #475569;
    --muted:   #94a3b8;
    --border:  #e2d9cc;
    --white:   #ffffff;
    --radius:  8px;
    --shadow:  0 1px 4px rgba(0,0,0,.07), 0 4px 16px rgba(0,0,0,.05);
  }}

  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--sand); color:var(--navy); font-family:'Inter',sans-serif; font-size:14px; line-height:1.6; }}

  /* ── HEADER ── */
  .header {{
    background: var(--navy);
    color: #fff;
    padding: 36px 48px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 32px;
    flex-wrap: wrap;
  }}
  .header-brand {{ font-size:1.5rem; font-weight:700; letter-spacing:-.5px; }}
  .header-sub {{ color:#93c5d8; font-size:.85rem; font-weight:300; margin-top:4px; }}
  .header-badge {{
    display:inline-block; margin-top:12px;
    background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.18);
    border-radius:4px; padding:4px 10px; font-size:.75rem; color:#bae6fd; letter-spacing:.3px;
  }}
  .patient-block {{ text-align:right; }}
  .patient-block .label {{ font-size:.72rem; color:#93c5d8; font-weight:500; text-transform:uppercase; letter-spacing:.8px; margin-bottom:8px; }}
  .patient-grid {{ display:grid; grid-template-columns:auto auto; gap:4px 20px; font-size:.84rem; }}
  .patient-grid .k {{ color:#93c5d8; font-weight:500; text-align:right; }}
  .patient-grid .v {{ color:#e2f0f5; }}
  .patient-ts {{ font-size:.72rem; color:#64748b; margin-top:10px; text-align:right; }}

  /* ── LAYOUT ── */
  .main {{ max-width:1320px; margin:0 auto; padding:36px 32px; }}

  /* ── SUMMARY CARDS ── */
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:14px; margin-bottom:28px; }}
  .card {{
    background:var(--white); border-radius:var(--radius);
    border:1px solid var(--border); box-shadow:var(--shadow);
    padding:20px 16px; text-align:center;
  }}
  .card .num {{ font-size:2rem; font-weight:700; line-height:1; }}
  .card .lbl {{ font-size:.72rem; color:var(--slate); margin-top:5px; font-weight:500; text-transform:uppercase; letter-spacing:.6px; }}
  .card-normal .num {{ color:#15803d; }}
  .card-high   .num {{ color:#b91c1c; }}
  .card-low    .num {{ color:#1d4ed8; }}
  .card-fu     .num {{ color:#b45309; }}
  .card-conf   .num {{ color:var(--teal); font-size:1.5rem; }}

  /* ── ESCALATION BOX ── */
  .esc-box {{
    background:{eb}; border:1px solid {ebd}; border-left:4px solid {ec};
    border-radius:var(--radius); padding:22px 28px; margin-bottom:24px;
    box-shadow:var(--shadow);
  }}
  .esc-label {{ font-size:.72rem; font-weight:600; color:{ec}; text-transform:uppercase; letter-spacing:1px; margin-bottom:14px; }}
  .bilingual {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
  @media(max-width:700px){{ .bilingual {{ grid-template-columns:1fr; }} }}
  .col-ar {{ direction:rtl; font-family:'Noto Sans Arabic',sans-serif; }}

  /* ── PANELS ── */
  .panel {{ background:var(--white); border:1px solid var(--border); border-radius:var(--radius); box-shadow:var(--shadow); margin-bottom:24px; overflow:hidden; }}
  .panel-header {{ background:var(--teal); color:#fff; padding:14px 24px; font-size:.95rem; font-weight:600; letter-spacing:.2px; }}
  .panel-body {{ padding:24px; }}

  /* ── TABLE ── */
  .table-wrap {{ overflow-x:auto; margin-bottom:24px; }}
  table {{ width:100%; border-collapse:collapse; font-size:.84rem; }}
  thead tr {{ background:var(--cream); border-bottom:2px solid var(--border); }}
  th {{ padding:10px 14px; text-align:left; font-weight:600; font-size:.72rem; color:var(--slate); text-transform:uppercase; letter-spacing:.6px; white-space:nowrap; }}
  td {{ padding:10px 14px; border-bottom:1px solid #f0ebe3; vertical-align:middle; }}
  tr:last-child td {{ border-bottom:none; }}
  tr:hover td {{ background:#fdf9f5; }}
  .td-name {{ min-width:170px; }}
  .test-name {{ display:block; font-weight:500; color:var(--navy); }}
  .td-val {{ font-family:'JetBrains Mono',monospace; font-size:.9rem; white-space:nowrap; }}
  .unit {{ font-weight:400; font-size:.78rem; color:var(--muted); }}
  .td-range {{ font-family:'JetBrains Mono',monospace; font-size:.8rem; color:var(--slate); }}
  .flag-pill {{ padding:2px 10px; border-radius:20px; font-size:.72rem; font-weight:700; letter-spacing:.5px; border:1px solid; }}
  .td-gauge {{ min-width:90px; }}
  .td-conf {{ font-family:'JetBrains Mono',monospace; font-size:.8rem; color:var(--teal); }}

  /* ── GAUGE ── */
  .gauge {{ position:relative; height:6px; background:#e9e4dc; border-radius:3px; margin:4px 0; }}
  .gauge-fill {{ position:absolute; left:15%; right:15%; top:0; bottom:0; background:rgba(15,118,110,.15); border-radius:3px; }}
  .gauge-dot {{ position:absolute; width:10px; height:10px; border-radius:50%; top:-2px; transform:translateX(-50%); box-shadow:0 1px 3px rgba(0,0,0,.25); }}

  /* ── EXPLANATIONS ── */
  .explain-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
  @media(max-width:860px){{ .explain-grid {{ grid-template-columns:1fr; }} }}
  .explain-card {{ background:var(--sand); border:1px solid var(--border); border-radius:var(--radius); padding:18px 20px; }}
  .lang-label {{ font-size:.72rem; font-weight:700; color:var(--teal); text-transform:uppercase; letter-spacing:.8px; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid var(--border); }}
  .explain-text {{ font-size:.875rem; line-height:1.75; color:#334155; }}
  .explain-text p {{ margin-bottom:8px; }}
  .explain-text li {{ margin-bottom:4px; padding-left:2px; }}
  .explain-text h2,.explain-text h3 {{ color:var(--navy); font-size:.95rem; margin:14px 0 8px; }}
  .explain-text hr {{ border:none; border-top:1px solid var(--border); margin:14px 0; }}
  .rtl {{ direction:rtl; text-align:right; font-family:'Noto Sans Arabic',sans-serif; }}

  /* ── SECONDARY SECTIONS ── */
  .section-card {{ background:var(--white); border:1px solid var(--border); border-radius:var(--radius); box-shadow:var(--shadow); margin-bottom:24px; overflow:hidden; }}
  .section-title {{ background:var(--cream); border-bottom:1px solid var(--border); padding:14px 24px; font-size:.9rem; font-weight:600; color:var(--navy); letter-spacing:.2px; }}
  .section-body {{ padding:24px; }}

  /* ── EMERGENCY ── */
  .emergency {{ background:#fef2f2; border:1px solid #fecaca; border-radius:var(--radius); padding:22px 28px; margin-bottom:24px; }}
  .emergency h3 {{ color:#b91c1c; margin-bottom:10px; font-size:.9rem; }}
  .emergency li {{ margin-bottom:4px; font-size:.875rem; }}
  .emergency p {{ font-size:.82rem; color:#7f1d1d; margin-top:12px; font-style:italic; }}

  /* ── DISCLAIMER ── */
  .disclaimer {{ background:#fffbeb; border:1px solid #fde68a; border-radius:var(--radius); padding:22px 28px; margin-bottom:24px; font-size:.84rem; }}
  .disclaimer h2 {{ color:#92400e; margin-bottom:10px; font-size:.9rem; }}
  .disclaimer li {{ margin-bottom:5px; }}
  .disclaimer p {{ margin-bottom:8px; }}
  .disclaimer hr {{ border:none; border-top:1px solid #fde68a; margin:14px 0; }}

  /* ── CONFIDENCE REPORT ── */
  .conf-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:14px; margin-bottom:18px; }}
  .conf-item {{ text-align:center; padding:14px; background:var(--teal-l); border-radius:var(--radius); }}
  .conf-item .val {{ font-family:'JetBrains Mono',monospace; font-size:1.6rem; font-weight:700; color:var(--teal-d); }}
  .conf-item .lbl {{ font-size:.72rem; color:var(--slate); margin-top:4px; font-weight:500; }}

  footer {{ text-align:center; padding:24px; font-size:.75rem; color:var(--muted); border-top:1px solid var(--border); margin-top:12px; }}
</style>
</head>
<body>

<header class="header">
  <div>
    <div class="header-brand">Lab Report — AI Agent</div>
    <div class="header-sub">Bilingual Patient Explanation &nbsp;|&nbsp; شرح نتائج التحاليل</div>
    <div class="header-badge">4-Step Agentic Pipeline &nbsp;·&nbsp; Responsible AI Design &nbsp;·&nbsp; No External API</div>
  </div>
  <div class="patient-block">
    <div class="label">Patient Information</div>
    <div class="patient-grid">
      <span class="k">Name / الاسم</span>          <span class="v">{patient.get('name','—')}</span>
      <span class="k">ID / الرقم</span>             <span class="v">{patient.get('id','—')}</span>
      <span class="k">DOB / تاريخ الميلاد</span>   <span class="v">{patient.get('dob','—')}</span>
      <span class="k">Gender / الجنس</span>         <span class="v">{patient.get('gender','—')}</span>
      <span class="k">التاريخ الهجري</span>         <span class="v">{format_hijri(patient.get('report_date',''))}</span>
      <span class="k">التاريخ الميلادي</span>       <span class="v">{patient.get('report_date','—')}</span>
      <span class="k">Physician / الطبيب</span>     <span class="v">{patient.get('physician','—')}</span>
    </div>
    <div class="patient-ts">Report generated: {ts} | {hijri_today()}</div>
  </div>
</header>

<div class="main">

  <div class="cards">
    <div class="card card-normal"><div class="num">{summary.get('normal',0)}</div><div class="lbl">معدل طبيعي</div></div>
    <div class="card card-high">  <div class="num">{summary.get('high',0)}</div>  <div class="lbl">مرتفع</div></div>
    <div class="card card-low">   <div class="num">{summary.get('low',0)}</div>   <div class="lbl">منخفض</div></div>
    <div class="card card-fu">    <div class="num">{summary.get('needs_followup',0)}</div><div class="lbl">يحتاج متابعة</div></div>
    <div class="card card-conf">  <div class="num">{conf.get('mean',0):.0%}</div> <div class="lbl">دقة النظام</div></div>
  </div>

  <div class="esc-box">
    <div class="esc-label">Medical Guidance</div>
    <div class="bilingual">
      <div class="col-en">{_md(r.get('escalation_en',''))}</div>
      <div class="col-ar">{_md(r.get('escalation_ar',''))}</div>
    </div>
  </div>

  {panel_html}

  <div class="section-card">
    <div class="section-title">اقتراحات للمشورة الطبية &nbsp;|&nbsp; Medical Consultation Suggestions</div>
    <div class="section-body">
      <div class="bilingual">
        <div class="col-en">{_md(r.get('followup_en',''))}</div>
        <div class="col-ar">{_md(r.get('followup_ar',''))}</div>
      </div>
    </div>
  </div>

  <div class="emergency">
    <div class="bilingual">
      <div class="col-en">{_md(r.get('emergency_en',''))}</div>
      <div class="col-ar">{_md(r.get('emergency_ar',''))}</div>
    </div>
  </div>

  <div class="section-card">
    <div class="section-title">AI Confidence Report — Responsible AI Transparency</div>
    <div class="section-body">
      <div class="conf-grid">
        <div class="conf-item"><div class="val">{conf.get('mean',0):.0%}</div><div class="lbl">Average Confidence</div></div>
        <div class="conf-item"><div class="val">{conf.get('min',0):.0%}</div><div class="lbl">Minimum</div></div>
        <div class="conf-item"><div class="val">{conf.get('max',0):.0%}</div><div class="lbl">Maximum</div></div>
        <div class="conf-item"><div class="val">{conf.get('total_tests',0)}</div><div class="lbl">Tests Analyzed</div></div>
      </div>
      <p style="font-size:.84rem;color:#475569;padding:14px 16px;background:var(--teal-l);border-radius:var(--radius);line-height:1.7">
        <strong>Methodology:</strong> {conf.get('interpretation','')}
        Confidence is computed by cross-validating the PDF flag field (H/L markers) against an independent
        mathematical comparison of the result to its reference range. Agreement between both sources = high confidence.
        Disagreement is flagged for review.
      </p>
    </div>
  </div>

  <div class="disclaimer">
    <div class="bilingual">
      <div class="col-en">{_md(r.get('disclaimer_en',''))}</div>
      <div class="col-ar">{_md(r.get('disclaimer_ar',''))}</div>
    </div>
  </div>

</div>

<footer>
  Lab Report AI Agent &nbsp;·&nbsp; Built with Python and pdfplumber &nbsp;·&nbsp; No external API &nbsp;·&nbsp;
  Portfolio project: PDF parsing · NLP · Agentic pipelines · Bilingual NLG · Responsible AI
</footer>
</body>
</html>"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/agent.py <path_to_lab_report.pdf>")
        sys.exit(1)
    result = run_agent(sys.argv[1])
    save_outputs(result, sys.argv[1])
