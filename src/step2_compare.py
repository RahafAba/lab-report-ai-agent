# Clinical context per test: what does high/low mean, what category does it fall under
CLINICAL_CONTEXT = {
    "WBC":            {"full": "White Blood Cells",              "category": "immune",          "high_concern": "infection, inflammation, or immune response",          "low_concern": "viral infection or bone marrow suppression"},
    "RBC":            {"full": "Red Blood Cells",                "category": "anemia_screen",   "high_concern": "dehydration or high altitude",                         "low_concern": "anemia or blood loss"},
    "Hemoglobin":     {"full": "Hemoglobin",                     "category": "anemia_screen",   "high_concern": "dehydration or lung condition",                        "low_concern": "anemia, bleeding, or nutritional deficiency"},
    "Hematocrit":     {"full": "Hematocrit",                     "category": "anemia_screen",   "high_concern": "dehydration",                                         "low_concern": "anemia or blood loss"},
    "MCV":            {"full": "Mean Corpuscular Volume",        "category": "anemia_type",     "high_concern": "B12 or folate deficiency",                             "low_concern": "iron deficiency or thalassemia"},
    "MCH":            {"full": "Mean Corpuscular Hemoglobin",    "category": "anemia_type",     "high_concern": "macrocytic anemia",                                    "low_concern": "iron deficiency or thalassemia"},
    "MCHC":           {"full": "Mean Corpuscular Hemoglobin Concentration", "category": "anemia_type", "high_concern": "hereditary spherocytosis",                    "low_concern": "iron deficiency"},
    "Platelets":      {"full": "Platelets",                      "category": "clotting",        "high_concern": "inflammation or iron deficiency",                      "low_concern": "bleeding risk or immune thrombocytopenia"},
    "Neutrophils":    {"full": "Neutrophils",                    "category": "immune_diff",     "high_concern": "bacterial infection or stress",                        "low_concern": "viral infection or bone marrow suppression"},
    "Lymphocytes":    {"full": "Lymphocytes",                    "category": "immune_diff",     "high_concern": "viral infection",                                      "low_concern": "immune suppression or steroid use"},
    "Monocytes":      {"full": "Monocytes",                      "category": "immune_diff",     "high_concern": "chronic infection or inflammation",                    "low_concern": "bone marrow suppression"},
    "Eosinophils":    {"full": "Eosinophils",                    "category": "immune_diff",     "high_concern": "allergy or parasitic infection",                       "low_concern": "steroid use"},
    "Basophils":      {"full": "Basophils",                      "category": "immune_diff",     "high_concern": "allergic reaction",                                    "low_concern": "rarely significant"},
    "Glucose":        {"full": "Blood Glucose",                  "category": "diabetes_screen", "high_concern": "prediabetes or diabetes",                              "low_concern": "hypoglycemia"},
    "HbA1c":          {"full": "Glycated Hemoglobin",            "category": "diabetes_monitor","high_concern": "prediabetes or diabetes",                              "low_concern": "excellent glucose control or hemolytic anemia"},
    "BUN":            {"full": "Blood Urea Nitrogen",            "category": "kidney",          "high_concern": "kidney disease or dehydration",                        "low_concern": "liver disease or malnutrition"},
    "Creatinine":     {"full": "Creatinine",                     "category": "kidney",          "high_concern": "kidney dysfunction",                                   "low_concern": "low muscle mass"},
    "eGFR":           {"full": "Estimated GFR",                  "category": "kidney_function", "high_concern": "not applicable, higher is better",                    "low_concern": "chronic kidney disease"},
    "Sodium":         {"full": "Sodium",                         "category": "electrolytes",    "high_concern": "dehydration",                                         "low_concern": "overhydration or kidney issue"},
    "Potassium":      {"full": "Potassium",                      "category": "electrolytes",    "high_concern": "kidney dysfunction or medication",                     "low_concern": "poor diet or diarrhea"},
    "Chloride":       {"full": "Chloride",                       "category": "electrolytes",    "high_concern": "dehydration or kidney issue",                          "low_concern": "vomiting or metabolic issue"},
    "ALT":            {"full": "Alanine Aminotransferase",       "category": "liver",           "high_concern": "liver inflammation or fatty liver",                    "low_concern": "rarely significant"},
    "AST":            {"full": "Aspartate Aminotransferase",     "category": "liver",           "high_concern": "liver, heart, or muscle damage",                       "low_concern": "rarely significant"},
    "Total Bilirubin":{"full": "Total Bilirubin",                "category": "liver",           "high_concern": "liver disease or hemolysis",                           "low_concern": "rarely significant"},
    "Total Protein":  {"full": "Total Protein",                  "category": "liver",           "high_concern": "dehydration or chronic inflammation",                  "low_concern": "malnutrition or liver disease"},
    "Albumin":        {"full": "Albumin",                        "category": "liver",           "high_concern": "dehydration",                                         "low_concern": "malnutrition or liver disease"},
    "Calcium":        {"full": "Calcium",                        "category": "minerals",        "high_concern": "hyperparathyroidism or malignancy",                    "low_concern": "vitamin D deficiency or hypoparathyroidism"},
    "NON-HDL":        {"full": "Non-HDL Cholesterol",            "category": "cardiovascular",  "high_concern": "cardiovascular disease risk",                          "low_concern": "malnutrition"},
    "Total Cholesterol":{"full": "Total Cholesterol",            "category": "cardiovascular",  "high_concern": "cardiovascular disease risk",                          "low_concern": "malnutrition or hyperthyroidism"},
    "LDL":            {"full": "LDL Cholesterol",                "category": "cardiovascular",  "high_concern": "atherosclerosis risk",                                 "low_concern": "malnutrition"},
    "HDL":            {"full": "HDL Cholesterol",                "category": "cardiovascular",  "high_concern": "regular exercise and healthy lifestyle, positive sign", "low_concern": "increased cardiovascular risk"},
    "Triglycerides":  {"full": "Triglycerides",                  "category": "cardiovascular",  "high_concern": "metabolic syndrome or insulin resistance",              "low_concern": "malnutrition"},
    "Serum Iron":     {"full": "Serum Iron",                     "category": "iron_status",     "high_concern": "iron overload",                                        "low_concern": "iron deficiency"},
    "Ferritin":       {"full": "Ferritin",                       "category": "iron_status",     "high_concern": "inflammation or iron overload",                        "low_concern": "iron deficiency"},
    "TIBC":           {"full": "Total Iron Binding Capacity",    "category": "iron_status",     "high_concern": "iron deficiency, body increasing absorption capacity",  "low_concern": "iron overload or malnutrition"},
    "Transferrin":    {"full": "Transferrin Saturation",         "category": "iron_status",     "high_concern": "iron overload",                                        "low_concern": "iron deficiency"},
    "Vitamin B12":    {"full": "Vitamin B12",                    "category": "nutrition",       "high_concern": "excess supplementation",                               "low_concern": "B12 deficiency affecting nerves and blood"},
    "Folate":         {"full": "Folate",                         "category": "nutrition",       "high_concern": "excess supplementation",                               "low_concern": "folate deficiency"},
    "TSH":            {"full": "TSH",                            "category": "thyroid",         "high_concern": "underactive thyroid",                                  "low_concern": "overactive thyroid"},
    "Free T4":        {"full": "Free T4",                        "category": "thyroid",         "high_concern": "overactive thyroid",                                   "low_concern": "underactive thyroid"},
    "Free T3":        {"full": "Free T3",                        "category": "thyroid",         "high_concern": "overactive thyroid",                                   "low_concern": "underactive thyroid"},
    "Anti-TPO":       {"full": "Anti-TPO Antibodies",            "category": "thyroid",         "high_concern": "autoimmune thyroid disease",                           "low_concern": "not clinically significant"},
    "Testosterone":   {"full": "Testosterone",                   "category": "hormones",        "high_concern": "hormonal imbalance or supplement use",                 "low_concern": "hormonal deficiency"},
    "DHEA-S":         {"full": "DHEA-S",                         "category": "hormones",        "high_concern": "adrenal overactivity",                                 "low_concern": "adrenal insufficiency"},
    "Cortisol":       {"full": "Cortisol",                       "category": "hormones",        "high_concern": "chronic stress or adrenal disorder",                   "low_concern": "adrenal insufficiency"},
    "Prolactin":      {"full": "Prolactin",                      "category": "hormones",        "high_concern": "pituitary issue or medication effect",                 "low_concern": "pituitary insufficiency"},
    "FSH":            {"full": "FSH",                            "category": "hormones",        "high_concern": "reduced ovarian reserve or menopause",                 "low_concern": "pituitary dysfunction"},
    "LH":             {"full": "LH",                             "category": "hormones",        "high_concern": "ovarian issue or menopause",                           "low_concern": "pituitary dysfunction"},
    "Vitamin D":      {"full": "Vitamin D",                      "category": "nutrition",       "high_concern": "excess supplementation",                               "low_concern": "deficiency affecting bone and immunity"},
    "Magnesium":      {"full": "Magnesium",                      "category": "minerals",        "high_concern": "kidney dysfunction or excess supplements",              "low_concern": "poor diet or malabsorption"},
    "Phosphorus":     {"full": "Phosphorus",                     "category": "minerals",        "high_concern": "kidney disease or hypoparathyroidism",                 "low_concern": "malnutrition or hyperparathyroidism"},
    "Zinc":           {"full": "Zinc",                           "category": "minerals",        "high_concern": "excess supplementation",                               "low_concern": "poor diet or malabsorption"},
    "CRP":            {"full": "C-Reactive Protein",             "category": "inflammation",    "high_concern": "active infection or inflammatory condition",            "low_concern": "not clinically significant"},
    "ESR":            {"full": "ESR",                            "category": "inflammation",    "high_concern": "inflammation, infection, or autoimmune activity",       "low_concern": "not clinically significant"},
    "Uric Acid":      {"full": "Uric Acid",                      "category": "kidney",          "high_concern": "gout risk or reduced kidney excretion",                "low_concern": "low protein diet"},
    "GGT":            {"full": "GGT",                            "category": "liver",           "high_concern": "liver or bile duct disease",                           "low_concern": "rarely significant"},
    "ALP":            {"full": "ALP",                            "category": "liver",           "high_concern": "liver, bile duct, or bone disease",                    "low_concern": "rarely significant"},
    "LDH":            {"full": "LDH",                            "category": "general",         "high_concern": "tissue damage in liver, heart, or muscle",             "low_concern": "rarely significant"},
    "PT":             {"full": "Prothrombin Time",               "category": "coagulation",     "high_concern": "liver disease or vitamin K deficiency",                "low_concern": "rarely significant"},
    "INR":            {"full": "INR",                            "category": "coagulation",     "high_concern": "bleeding risk",                                        "low_concern": "clotting risk in anticoagulated patients"},
    "Fibrinogen":     {"full": "Fibrinogen",                     "category": "coagulation",     "high_concern": "inflammation or clotting risk",                        "low_concern": "liver disease or rare clotting disorder"},
}


def _get_context(test_name: str) -> dict:
    up = test_name.upper()
    # longest key wins to avoid partial matches like HDL matching Non-HDL
    matches = [(k, v) for k, v in CLINICAL_CONTEXT.items() if k.upper() in up]
    if matches:
        return max(matches, key=lambda x: len(x[0]))[1]
    return {"full": test_name, "category": "general", "high_concern": "consult physician", "low_concern": "consult physician"}


def _compute_deviation(result, ref_low, ref_high) -> dict:
    if result is None or (ref_low is None and ref_high is None):
        return {"deviation_pct": None, "severity": "unknown", "position_pct": 50}

    if ref_low is not None and ref_high is not None:
        width = ref_high - ref_low or ref_high * 0.2 or 1
        if result < ref_low:
            dev = (ref_low - result) / width
        elif result > ref_high:
            dev = (result - ref_high) / width
        else:
            dev = 0
        pos = ((result - ref_low) / width) * 100
    elif ref_high is not None:
        width = ref_high * 0.4 or 1
        dev = max(0, (result - ref_high) / width)
        pos = (result / ref_high) * 100
    else:
        width = ref_low * 0.4 or 1
        dev = max(0, (ref_low - result) / width)
        pos = (result / ref_low) * 100 if ref_low else 50

    if dev > 0.60:   severity = "significant"
    elif dev > 0.30: severity = "moderate"
    elif dev > 0.10: severity = "mild"
    else:            severity = "normal"

    return {
        "deviation_pct": round(dev * 100, 1),
        "severity":      severity,
        "position_pct":  round(max(-20, min(120, pos)), 1),
    }


def analyze_tests(extracted: dict) -> dict:
    enriched = []
    flagged   = []
    critical  = []

    for t in extracted["tests"]:
        ctx = _get_context(t["test_name"])
        dev = _compute_deviation(t["result"], t["ref_low"], t["ref_high"])
        concern = ctx["high_concern"] if t["flag"] == "HIGH" else ctx["low_concern"]

        item = {
            **t,
            "full_name":    ctx["full"],
            "category":     ctx["category"],
            "concern":      concern,
            "deviation_pct":dev["deviation_pct"],
            "severity":     dev["severity"],
            "position_pct": dev["position_pct"],
            "needs_followup": t["flag"] in ("HIGH", "LOW") and dev["severity"] in ("moderate", "significant"),
        }
        enriched.append(item)
        if t["flag"] in ("HIGH", "LOW"):
            flagged.append(item)
            if dev["severity"] == "significant":
                critical.append(item)

    summary = {
        "total":         len(enriched),
        "normal":        sum(1 for t in enriched if t["flag"] == "NORMAL"),
        "high":          sum(1 for t in enriched if t["flag"] == "HIGH"),
        "low":           sum(1 for t in enriched if t["flag"] == "LOW"),
        "needs_followup":sum(1 for t in enriched if t["needs_followup"]),
        "critical_count":len(critical),
    }

    return {
        "patient_info": extracted["patient_info"],
        "source_file":  extracted["source_file"],
        "panels_found": extracted["panels_found"],
        "tests":        enriched,
        "total":        len(enriched),
        "flagged":      flagged,
        "critical":     critical,
        "summary":      summary,
    }
