# Lab Report AI Agent

A 4-step AI agent that reads a blood test PDF and explains every result in plain English and Arabic, built for people who receive lab reports with no guidance on what the numbers actually mean.

---

## The Problem

Lab reports are dense. Most patients walk away with a document they cannot fully interpret, and not everyone has immediate access to someone who can explain it. This project is an attempt to close that gap, not to replace clinical advice, but to make the information more accessible.

---

## What It Does

The agent processes a blood test PDF through four steps.

**Step 1** extracts every test result from the PDF, including the value, unit, reference range, and flag, and assigns a confidence score to each one.

**Step 2** compares each result against its reference range and calculates how far outside normal it falls, assigning a severity level of mild, moderate, or significant.

**Step 3** generates a plain-language explanation for every result in both English and Arabic, with causes that are appropriate to the severity level. A mildly elevated result gets a different explanation than a significantly elevated one.

**Step 4** produces escalation guidance, a follow-up list, a full confidence report, and a mandatory medical disclaimer in both languages.

The output is a bilingual HTML report.

---

## Panels Covered

Complete Blood Count, Metabolic Panel, Lipid Panel, Iron Studies, Thyroid Panel, Hormones, Vitamins and Minerals, Inflammation Markers, Liver Panel, Coagulation, Cardiac Markers, Tumor Markers, Hepatitis Panel.

---

## Quick Start

```bash
pip install -r requirements.txt
python create_sample_pdf.py
python src/agent.py sample_data/sample_blood_test.pdf
```

Open the HTML file generated in the `output/` folder in your browser.

To use with your own report:

```bash
python src/agent.py path/to/your_report.pdf
```

---

## Project Structure

```
lab-report-ai-agent/
├── src/
│   ├── agent.py            Main orchestrator, runs all four steps and builds the HTML report
│   ├── step1_extract.py    PDF table parser with dual-source confidence scoring
│   ├── step2_compare.py    Clinical comparison and severity classification
│   ├── step3_explain.py    Bilingual explanation generation, English and Arabic
│   └── step4_escalate.py   Responsible AI layer, escalation, disclaimers, confidence report
├── sample_data/
│   └── sample_blood_test.pdf    Two-page demo report covering all major panels
├── create_sample_pdf.py    Generates the demo PDF
├── requirements.txt
└── .gitignore
```

---

## Design Decisions

**No external API.** The entire pipeline runs offline. This is a deliberate choice for healthcare contexts where sending patient data to a third-party service is not appropriate.

**Confidence scoring.** Every extracted result is validated by cross-checking the PDF flag against an independent calculation. When the two sources agree, confidence is high. When they disagree, the result is flagged for review.

**Tiered causes.** The possible causes shown for an abnormal result depend on how far outside the normal range it falls. This avoids presenting worst-case explanations for borderline results.

**Responsible AI layer.** Every report includes a mandatory medical disclaimer in both languages, an escalation recommendation based on severity, and explicit guidance on when to seek medical attention.

---

## Limitations

The extraction works best with structured, table based PDFs. Scanned documents require OCR which is not included. Reference ranges are general population standards and may not apply to every individual. This tool is for informational purposes only and does not constitute medical advice.

---

## Requirements

Python 3.10 or above. Dependencies are listed in `requirements.txt` and are minimal: pdfplumber for extraction and reportlab for generating the demo PDF.
