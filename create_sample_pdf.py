"""Creates a realistic two page sample blood test PDF covering all major panels."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
import os

def make_table(data, col_widths):
    flag_col = 4
    flag_map = {"H": colors.HexColor('#fff3cd'), "L": colors.HexColor('#fde8ea'), "Normal": colors.HexColor('#d4edda')}
    t = Table(data, colWidths=col_widths)
    style = [
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 8),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('BACKGROUND',  (0,0), (-1,0),  colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR',   (0,0), (-1,0),  colors.white),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor('#ccddee')),
        ('ALIGN',       (1,0), (-1,-1), 'CENTER'),
        ('PADDING',     (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f9fbfd'), colors.white]),
    ]
    for i, row in enumerate(data[1:], 1):
        flag = str(row[4]) if len(row) > 4 else ""
        bg = flag_map.get("H" if "H" in flag or "↑" in flag else ("L" if "L" in flag or "↓" in flag else "Normal"), colors.white)
        style.append(('BACKGROUND', (flag_col,i), (flag_col,i), bg))
    t.setStyle(TableStyle(style))
    return t

def create_sample_lab_report():
    os.makedirs("sample_data", exist_ok=True)
    doc = SimpleDocTemplate("sample_data/sample_blood_test.pdf", pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)

    styles = getSampleStyleSheet()
    title_s  = ParagraphStyle('T', parent=styles['Normal'], fontSize=16, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#1a3a5c'), spaceAfter=2*mm)
    sub_s    = ParagraphStyle('S', parent=styles['Normal'], fontSize=10, fontName='Helvetica', alignment=TA_CENTER, textColor=colors.HexColor('#555555'), spaceAfter=1*mm)
    sec_s    = ParagraphStyle('Sec', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a3a5c'), spaceAfter=2*mm, spaceBefore=4*mm)
    disc_s   = ParagraphStyle('D', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Oblique', textColor=colors.grey, alignment=TA_CENTER)

    HDR = ["Test / الفحص","Result / النتيجة","Unit / الوحدة","Reference Range / المرجع","Flag / تنبيه"]
    CW5 = [65*mm, 25*mm, 22*mm, 45*mm, 22*mm]

    story = []

    # HEADER 
    story.append(Paragraph("King Fahad Medical City — مدينة الملك فهد الطبية", title_s))
    story.append(Paragraph("Laboratory & Pathology Department | قسم المختبرات", sub_s))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a3a5c')))
    story.append(Spacer(1,4*mm))

    # PATIENT INFO 
    pt = Table([
        ["Patient Name / اسم المريض:","Ahmed Mohammed Al-Rashidi","Report Date / تاريخ التقرير:","2025-11-15"],
        ["Patient ID / رقم المريض:","KF-2025-084721","Collection Time / وقت الأخذ:","07:30 AM"],
        ["Date of Birth / تاريخ الميلاد:","1985-04-22 (Age: 40)","Ordering Physician:","Dr. Layla Mansour"],
        ["Gender / الجنس:","Male / ذكر","Clinical Notes:","Annual check, fatigue, low energy"],
    ], colWidths=[50*mm,60*mm,50*mm,45*mm])
    pt.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8),
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.HexColor('#e8f0f7'),colors.HexColor('#f5f8fc')]),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#ccddee')),('PADDING',(0,0),(-1,-1),4),
    ]))
    story.append(pt); story.append(Spacer(1,5*mm))

    # CBC
    story.append(Paragraph("COMPLETE BLOOD COUNT (CBC) — فحص الدم الكامل", sec_s))
    story.append(make_table([HDR,
        ["WBC — كريات الدم البيضاء","11.8","×10³/μL","4.5 – 11.0","H ↑"],
        ["RBC — كريات الدم الحمراء","4.20","×10⁶/μL","4.50 – 5.90","L ↓"],
        ["Hemoglobin — الهيموجلوبين","11.2","g/dL","13.5 – 17.5","L ↓"],
        ["Hematocrit — الهيماتوكريت","34.5","%","41.0 – 53.0","L ↓"],
        ["MCV — متوسط حجم الكريات","72.4","fL","80.0 – 100.0","L ↓"],
        ["MCH — متوسط هيموجلوبين الكرية","24.1","pg","27.0 – 33.0","L ↓"],
        ["MCHC — تركيز هيموجلوبين الكرية","32.5","g/dL","32.0 – 36.0","Normal"],
        ["Platelets — الصفائح الدموية","215","×10³/μL","150 – 400","Normal"],
        ["Neutrophils %","72.0","%","50 – 70","H ↑"],
        ["Lymphocytes %","20.0","%","20 – 40","Normal"],
        ["Monocytes %","6.0","%","2 – 8","Normal"],
        ["Eosinophils %","1.5","%","1 – 4","Normal"],
        ["Basophils %","0.5","%","0 – 1","Normal"],
    ], CW5)); story.append(Spacer(1,4*mm))

    #  METABOLIC
    story.append(Paragraph("COMPREHENSIVE METABOLIC PANEL — لوحة التحليل الأيضي الشاملة", sec_s))
    story.append(make_table([HDR,
        ["Glucose (Fasting) — سكر الصيام","112","mg/dL","70 – 100","H ↑"],
        ["HbA1c — السكر التراكمي","6.1","%","< 5.7","H ↑"],
        ["BUN — نيتروجين اليوريا","18","mg/dL","7 – 25","Normal"],
        ["Creatinine — الكرياتينين","0.95","mg/dL","0.74 – 1.35","Normal"],
        ["eGFR — معدل الترشيح الكبيبي","88","mL/min/1.73m²","> 60","Normal"],
        ["Sodium — الصوديوم","139","mEq/L","136 – 145","Normal"],
        ["Potassium — البوتاسيوم","4.1","mEq/L","3.5 – 5.1","Normal"],
        ["Chloride — الكلوريد","101","mEq/L","98 – 107","Normal"],
        ["ALT (SGPT) — إنزيم الكبد","52","U/L","7 – 40","H ↑"],
        ["AST (SGOT) — إنزيم الكبد","45","U/L","10 – 40","H ↑"],
        ["Total Bilirubin — البيليروبين الكلي","1.1","mg/dL","0.2 – 1.2","Normal"],
        ["Total Protein — البروتين الكلي","7.2","g/dL","6.0 – 8.3","Normal"],
        ["Albumin — الألبومين","4.1","g/dL","3.5 – 5.0","Normal"],
        ["Calcium — الكالسيوم","9.4","mg/dL","8.5 – 10.5","Normal"],
    ], CW5)); story.append(Spacer(1,4*mm))

    #  LIPID
    story.append(Paragraph("LIPID PANEL — لوحة الدهون", sec_s))
    story.append(make_table([["Test / الفحص","Result / النتيجة","Unit / الوحدة","Desirable / المستهدف","Flag / تنبيه"],
        ["Total Cholesterol — الكوليسترول الكلي","218","mg/dL","< 200","H ↑"],
        ["LDL Cholesterol — الكوليسترول الضار","145","mg/dL","< 100","H ↑"],
        ["HDL Cholesterol — الكوليسترول النافع","38","mg/dL","> 40 (Male)","L ↓"],
        ["Triglycerides — الدهون الثلاثية","175","mg/dL","< 150","H ↑"],
        ["Non-HDL Cholesterol","180","mg/dL","< 130","H ↑"],
    ], CW5)); story.append(Spacer(1,4*mm))

    #  IRON
    story.append(Paragraph("IRON STUDIES — دراسات الحديد", sec_s))
    story.append(make_table([HDR,
        ["Serum Iron — حديد المصل","45","μg/dL","60 – 170","L ↓"],
        ["Ferritin — الفيريتين","8","ng/mL","24 – 336","L ↓"],
        ["TIBC — السعة الكلية لربط الحديد","420","μg/dL","250 – 370","H ↑"],
        ["Transferrin Saturation","10.7","%","20 – 50","L ↓"],
        ["Vitamin B12 — فيتامين ب١٢","198","pg/mL","200 – 900","L ↓"],
        ["Folate — حمض الفوليك","4.2","ng/mL","3.1 – 17.5","Normal"],
    ], CW5))

    # PAGE 2 
    story.append(PageBreak())
    story.append(Paragraph("King Fahad Medical City — Continued / تكملة التقرير", title_s))
    story.append(Paragraph("Patient: Ahmed Mohammed Al-Rashidi  |  ID: KF-2025-084721  |  Date: 2025-11-15", sub_s))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a3a5c')))
    story.append(Spacer(1,5*mm))

    # THYROID
    story.append(Paragraph("THYROID PANEL — فحوصات الغدة الدرقية", sec_s))
    story.append(make_table([HDR,
        ["TSH — هرمون الغدة الدرقية المحفز","6.8","mIU/L","0.4 – 4.0","H ↑"],
        ["Free T4 — الثيروكسين الحر","0.72","ng/dL","0.8 – 1.8","L ↓"],
        ["Free T3 — الثرييودوثيرونين الحر","2.4","pg/mL","2.3 – 4.2","Normal"],
        ["Anti-TPO — أجسام مضادة للغدة","142","IU/mL","< 35","H ↑"],
    ], CW5)); story.append(Spacer(1,4*mm))

    #  HORMONES
    story.append(Paragraph("HORMONES — الهرمونات", sec_s))
    story.append(make_table([HDR,
        ["Testosterone — التستوستيرون","9.2","nmol/L","9.9 – 27.8","L ↓"],
        ["DHEA-S — هرمون الغدة الكظرية","180","μg/dL","160 – 449","Normal"],
        ["Cortisol (Morning) — الكورتيزول","18.5","μg/dL","6.2 – 19.4","Normal"],
        ["Prolactin — البرولاكتين","8.2","ng/mL","2.0 – 18.0","Normal"],
        ["FSH — هرمون منشط للجريب","3.8","mIU/mL","1.5 – 12.4","Normal"],
        ["LH — هرمون ملوتن","4.1","mIU/mL","1.7 – 8.6","Normal"],
    ], CW5)); story.append(Spacer(1,4*mm))

    #  VITAMINS & MINERALS
    story.append(Paragraph("VITAMINS & MINERALS — الفيتامينات والمعادن", sec_s))
    story.append(make_table([HDR,
        ["Vitamin D (25-OH) — فيتامين د","18","ng/mL","30 – 100","L ↓"],
        ["Magnesium — المغنيسيوم","0.72","mmol/L","0.75 – 1.00","L ↓"],
        ["Phosphorus — الفوسفور","3.4","mg/dL","2.5 – 4.5","Normal"],
        ["Zinc — الزنك","72","μg/dL","70 – 120","Normal"],
        ["Calcium — الكالسيوم","9.4","mg/dL","8.5 – 10.5","Normal"],
    ], CW5)); story.append(Spacer(1,4*mm))

    #  INFLAMMATION
    story.append(Paragraph("INFLAMMATION MARKERS — مؤشرات الالتهاب", sec_s))
    story.append(make_table([HDR,
        ["CRP — بروتين سي التفاعلي","18.4","mg/L","< 5.0","H ↑"],
        ["ESR — سرعة ترسب الدم","34","mm/hr","0 – 15","H ↑"],
        ["Uric Acid — حمض اليوريك","7.8","mg/dL","3.5 – 7.2","H ↑"],
    ], CW5)); story.append(Spacer(1,4*mm))

    # LIVER ADVANCED 
    story.append(Paragraph("LIVER PANEL (ADVANCED) — فحوصات الكبد المتقدمة", sec_s))
    story.append(make_table([HDR,
        ["GGT — جاما جلوتاميل ترانسفيراز","62","U/L","8 – 61","H ↑"],
        ["ALP — الفوسفاتاز القلوية","88","U/L","44 – 147","Normal"],
        ["LDH — نازعة هيدروجين اللاكتات","195","U/L","140 – 280","Normal"],
    ], CW5)); story.append(Spacer(1,4*mm))

    # COAGULATION 
    story.append(Paragraph("COAGULATION — فحوصات التجلط", sec_s))
    story.append(make_table([HDR,
        ["PT — وقت البروثرومبين","12.4","seconds","11.0 – 13.5","Normal"],
        ["INR","1.1","ratio","0.8 – 1.2","Normal"],
        ["Fibrinogen — الفيبرينوجين","420","mg/dL","200 – 400","H ↑"],
    ], CW5))

    story.append(Spacer(1,6*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#aaaaaa')))
    story.append(Spacer(1,2*mm))
    story.append(Paragraph("⚠ This report is for physician use only. SAMPLE/DEMO document for educational purposes.", disc_s))

    doc.build(story)
    print("Sample PDF created: sample_data/sample_blood_test.pdf")

create_sample_lab_report()
