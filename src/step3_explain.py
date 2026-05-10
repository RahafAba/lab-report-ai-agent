# Generates plain language explanations for each lab result in English and Arabic.
# Causes shown depend on severity, so mild results get mild explanations.

from datetime import datetime

# Arabic number agreement rules
def _ar_count(n: int, singular: str, dual: str, plural: str) -> str:
    """Return the correct Arabic form for a number."""
    if n == 1:   return f"نتيجة {singular}"
    if n == 2:   return f"{dual}"
    if n <= 10:  return f"{n} {plural}"
    return f"{n} {plural}"

def _ar_results_count(n: int) -> str:
    # Arabic number-noun rules: 1=واحدة, 2=dual, 3-10=plural نتائج, 11+=singular نتيجة
    if n == 1:  return "نتيجة واحدة"
    if n == 2:  return "نتيجتين"
    if n <= 10: return f"{n} نتائج"
    return f"{n} نتيجة"

# Panel intro text shown at the top of each section
EN_PANEL_INTRO = {
    "Complete Blood Count":
        "Your **Complete Blood Count (CBC)** is a general screening test for the cells in your blood: "
        "red blood cells which carry oxygen, white blood cells which fight infection, "
        "and platelets which help blood clot.",
    "Metabolic Panel":
        "Your **Metabolic Panel** is a routine blood test that measures various chemicals "
        "to assess the health of your kidneys, liver, blood sugar, protein levels, and mineral balance.",
    "Lipid Panel":
        "Your **Lipid Panel** is a comprehensive test measuring the fats in your blood "
        "and their effect on your heart health.",
    "Iron Studies":
        "Your **Iron Studies** measure iron levels in the blood, checking whether your body "
        "has enough iron stored and is using it correctly.",
    "Thyroid Panel":
        "Your **Thyroid Panel** checks the thyroid gland, which controls metabolism, energy, "
        "weight, heart rate, and body temperature.",
    "Hormones":
        "Your **Hormone Tests** measure key hormones that regulate energy, growth, "
        "fertility, and mood.",
    "Vitamins & Minerals":
        "Your **Vitamins & Minerals** panel checks essential nutrients needed for bone health, "
        "nerve function, immunity, and energy.",
    "Inflammation Markers":
        "Your **Inflammation Markers** detect whether your body is experiencing inflammation, "
        "infection, or an immune response.",
    "Liver Panel (Advanced)":
        "Your **Advanced Liver Panel** provides a detailed picture of liver cell health "
        "and bile duct function.",
    "Coagulation":
        "Your **Coagulation Tests** measure how well your blood clots and stops bleeding.",
    "Cardiac Markers":
        "Your **Cardiac Markers** assess heart muscle health and clotting risk.",
    "Tumor Markers":
        "Your **Tumor Markers** are used to monitor certain medical conditions. "
        "An elevated result does not by itself confirm a diagnosis.",
    "Hepatitis Panel":
        "Your **Hepatitis Panel** screens for viral hepatitis infections.",
    "Diabetes Panel":
        "Your **Diabetes Panel** provides detailed insulin and glucose metabolism information.",
    "Kidney Panel":
        "Your **Kidney Panel** gives an advanced picture of how well your kidneys are filtering.",
}

AR_PANEL_INTRO = {
    "Complete Blood Count":
        "صورة الدم الكاملة (CBC) فحص عام لخلايا الدم المكونة من: الكريات الحمراء وهي المسؤولة عن حمل الأكسجين، "
        "والكريات البيضاء المسؤولة عن محاربة العدوى، والصفائح الدموية التي تساعد في تجلط الدم.",
    "Metabolic Panel":
        "فحص دم روتيني يقيس مستويات مواد كيميائية مختلفة لتقييم صحة الكلى، الكبد، مستويات السكر، "
        "مستويات البروتين، الأحماض، توازن السوائل والمعادن.",
    "Lipid Panel":
        "فحص الدهون الشامل الذي يقيس نسبة الدهون في الدم وتأثيرها على صحة القلب.",
    "Iron Studies":
        "فحص مستويات الحديد في الدم، يفحص هل جسمك يحتوي على كمية كافية من الحديد وهل يستخدمه بصورة صحيحة.",
    "Thyroid Panel":
        "فحوصات الغدة الدرقية التي تتحكم في معدل الأيض والطاقة والوزن وضربات القلب ودرجة الحرارة.",
    "Hormones":
        "فحوصات الهرمونات التي تنظم وظائف الجسم المختلفة من الطاقة والنمو إلى الخصوبة والمزاج.",
    "Vitamins & Minerals":
        "فحوصات الفيتامينات والمعادن الضرورية لصحة العظام والأعصاب والمناعة والطاقة.",
    "Inflammation Markers":
        "مؤشرات الالتهاب التي تكشف ما إذا كان الجسم يعاني من التهاب أو عدوى أو استجابة مناعية.",
    "Liver Panel (Advanced)":
        "فحوصات متقدمة لوظائف الكبد تكشف عن صحة خلايا الكبد والقنوات الصفراوية.",
    "Coagulation":
        "فحوصات التجلط التي تقيس قدرة الدم على الانعقاد والتوقف عن النزيف.",
    "Cardiac Markers":
        "مؤشرات القلب التي تكشف عن صحة عضلة القلب وخطر الجلطات.",
    "Tumor Markers":
        "مؤشرات تُستخدم لمتابعة بعض الحالات الطبية وليست تشخيصاً قاطعاً بالضرورة.",
    "Hepatitis Panel":
        "فحوصات التهاب الكبد الفيروسي للكشف عن الإصابة بفيروسات الكبد المختلفة.",
    "Diabetes Panel":
        "فحوصات متخصصة للسكري تقيس مستويات الأنسولين ومقاومته.",
    "Kidney Panel":
        "فحوصات متقدمة لوظائف الكلى تكشف عن كفاءة الكلى في تصفية الدم.",
}


# Arabic names for each test, written as "test name, indicator of X"
AR_TEST_NAMES = {
    "WBC":                   "كريات الدم البيضاء، مؤشر على مقاومة العدوى",
    "RBC":                   "كريات الدم الحمراء، مؤشر على حمل الأكسجين",
    "Hemoglobin":            "الهيموغلوبين، مؤشر على كمية الأكسجين في الدم",
    "Hematocrit":            "الهيماتوكريت، مؤشر على نسبة كريات الدم الحمراء",
    "MCV":                   "MCV، مؤشر على حجم كريات الدم الحمراء",
    "MCH":                   "MCH، مؤشر على كمية الهيموغلوبين في كل كرية",
    "MCHC":                  "MCHC، مؤشر على تركيز الهيموغلوبين في الكريات",
    "Platelets":             "الصفائح الدموية، مؤشر على قدرة تجلط الدم",
    "Neutrophils":           "النيوتروفيل، مؤشر على مقاومة البكتيريا",
    "Lymphocytes":           "الليمفوسايت، مؤشر على مقاومة الفيروسات",
    "Monocytes":             "المونوسايت، مؤشر على الاستجابة المناعية",
    "Eosinophils":           "الإيزينوفيل، مؤشر على الحساسية والطفيليات",
    "Basophils":             "الباسوفيل، مؤشر على الاستجابة التحسسية",
    "Glucose":               "سكر الدم، مؤشر على مستوى الطاقة وخطر السكري",
    "HbA1c":                 "السكر التراكمي، مؤشر على معدل السكر خلال 3 أشهر",
    "BUN":                   "BUN، مؤشر على وظائف الكلى وتكسير البروتين",
    "Creatinine":            "الكرياتينين، مؤشر على كفاءة الكلى",
    "eGFR":                  "معدل ترشيح الكلى، مؤشر على قدرة الكلى على تنقية الدم",
    "Sodium":                "الصوديوم، مؤشر على توازن السوائل في الجسم",
    "Potassium":             "البوتاسيوم، مؤشر على صحة القلب والعضلات",
    "Chloride":              "الكلوريد، مؤشر على توازن الأحماض في الجسم",
    "ALT":                   "إنزيم ALT، مؤشر على صحة خلايا الكبد",
    "AST":                   "إنزيم AST، مؤشر على صحة الكبد والقلب والعضلات",
    "Total Bilirubin":       "البيليروبين، مؤشر على معالجة الكبد لخلايا الدم القديمة",
    "Total Protein":         "البروتين الكلي، مؤشر على التغذية ووظائف الكبد",
    "Albumin":               "الألبومين، مؤشر على التغذية وصحة الكبد",
    "Calcium":               "الكالسيوم، مؤشر على صحة العظام والأعصاب والقلب",
    "Total Cholesterol":     "الكوليسترول الكلي، مؤشر على صحة الشرايين",
    "LDL Cholesterol":       "الكوليسترول الضار LDL، مؤشر على خطر انسداد الشرايين",
    "HDL Cholesterol":       "الكوليسترول النافع HDL، مؤشر على حماية القلب",
    "Triglycerides":         "الدهون الثلاثية، مؤشر على معالجة الجسم للدهون والسكريات",
    "Non-HDL Cholesterol":   "الكوليسترول الضار الكلي، مؤشر على خطر أمراض القلب",
    "Serum Iron":            "الحديد في الدم، مؤشر على كمية الحديد المتاح للجسم",
    "Ferritin":              "الفيريتين، مؤشر على مخزون الحديد في الجسم",
    "TIBC":                  "TIBC، مؤشر على قدرة الجسم على امتصاص الحديد",
    "Transferrin Saturation":"نسبة تشبع الحديد، مؤشر على مدى استخدام الجسم للحديد",
    "Vitamin B12":           "فيتامين ب12، مؤشر على صحة الأعصاب وإنتاج كريات الدم",
    "Folate":                "حمض الفوليك، مؤشر على صحة الدم وتكوين الخلايا",
    "White Blood Cells":     "كريات الدم البيضاء، مؤشر على مقاومة العدوى",
    "Red Blood Cells":       "كريات الدم الحمراء، مؤشر على حمل الأكسجين",
    "Mean Corpuscular Volume":         "MCV، مؤشر على حجم كريات الدم الحمراء",
    "Mean Corpuscular Hemoglobin":     "MCH، مؤشر على كمية الهيموغلوبين في كل كرية",
    "Blood Glucose":                   "سكر الدم، مؤشر على مستوى الطاقة وخطر السكري",
    "Glycated Hemoglobin":             "السكر التراكمي، مؤشر على معدل السكر خلال 3 أشهر",
    "Blood Urea Nitrogen":             "BUN، مؤشر على وظائف الكلى وتكسير البروتين",
    "Alanine Aminotransferase":        "إنزيم ALT، مؤشر على صحة خلايا الكبد",
    "Aspartate Aminotransferase":      "إنزيم AST، مؤشر على صحة الكبد والقلب والعضلات",
    "Iron Stores":                     "مخزون الحديد، مؤشر على احتياطي الحديد في الجسم",
    "Estimated GFR":                   "معدل ترشيح الكلى، مؤشر على قدرة الكلى على تنقية الدم",
    "Total Iron Binding Capacity":     "TIBC، مؤشر على قدرة الجسم على امتصاص الحديد",
    "HDL Cholesterol":                 "الكوليسترول النافع HDL، مؤشر على حماية القلب",
    "Non-HDL Cholesterol":             "الكوليسترول الضار الكلي، مؤشر على خطر أمراض القلب",
    "TSH":                             "TSH، مؤشر على نشاط الغدة الدرقية",
    "T3":                              "T3، مؤشر على هرمون الغدة الدرقية النشط",
    "T4":                              "T4، مؤشر على إنتاج الغدة الدرقية للهرمون",
    "Free T3":                         "T3 الحر، مؤشر على مستوى هرمون الغدة الدرقية النشط",
    "Free T4":                         "T4 الحر، مؤشر على نشاط الغدة الدرقية",
    "Anti-TPO":                        "أجسام مضادة للغدة الدرقية، مؤشر على أمراض المناعة الذاتية للغدة",
    "Thyroid Peroxidase":              "أجسام مضادة للغدة الدرقية، مؤشر على أمراض المناعة الذاتية للغدة",
    "Testosterone":                    "هرمون التستوستيرون، مؤشر على الصحة الجنسية والعضلية",
    "Total Testosterone":              "هرمون التستوستيرون الكلي، مؤشر على الصحة الجنسية والعضلية",
    "Free Testosterone":               "هرمون التستوستيرون الحر، مؤشر على مستوى الهرمون النشط",
    "Estrogen":                        "هرمون الإستروجين، مؤشر على التوازن الهرموني",
    "Estradiol":                       "الإستراديول، مؤشر على صحة المبايض والتوازن الهرموني",
    "Progesterone":                    "البروجستيرون، مؤشر على صحة الدورة الشهرية والإباضة",
    "FSH":                             "هرمون FSH، مؤشر على صحة المبايض والخصيتين",
    "LH":                              "هرمون LH، مؤشر على الإباضة وصحة الجهاز التناسلي",
    "Prolactin":                       "البرولاكتين، مؤشر على صحة الغدة النخامية",
    "DHEA-S":                          "DHEA-S، مؤشر على نشاط الغدة الكظرية",
    "Cortisol":                        "الكورتيزول، مؤشر على استجابة الجسم للضغط وصحة الغدة الكظرية",
    "AMH":                             "هرمون AMH، مؤشر على الاحتياطي المبيضي والخصوبة",
    "SHBG":                            "SHBG، مؤشر على بروتين ربط الهرمونات الجنسية",
    "Vitamin D":                       "فيتامين د، مؤشر على صحة العظام والمناعة والمزاج",
    "25-OH Vitamin D":                 "فيتامين د، مؤشر على صحة العظام والمناعة والمزاج",
    "Vitamin B1":                      "فيتامين ب1، مؤشر على صحة الأعصاب والطاقة",
    "Thiamine":                        "فيتامين ب1، مؤشر على صحة الأعصاب والطاقة",
    "Magnesium":                       "المغنيسيوم، مؤشر على صحة العضلات والأعصاب والقلب",
    "Phosphorus":                      "الفوسفور، مؤشر على صحة العظام والطاقة",
    "Zinc":                            "الزنك، مؤشر على المناعة والتئام الجروح والخصوبة",
    "Copper":                          "النحاس، مؤشر على صحة الدم والأعصاب",
    "Insulin":                         "الأنسولين، مؤشر على استجابة الجسم لسكر الدم",
    "Fasting Insulin":                 "الأنسولين الصيامي، مؤشر على مقاومة الأنسولين",
    "C-Peptide":                       "الببتيد C، مؤشر على إنتاج البنكرياس للأنسولين",
    "HOMA-IR":                         "HOMA-IR، مؤشر على درجة مقاومة الأنسولين",
    "Troponin":                        "التروبونين، مؤشر على تلف عضلة القلب",
    "Troponin I":                      "التروبونين، مؤشر على تلف عضلة القلب",
    "Troponin T":                      "التروبونين، مؤشر على تلف عضلة القلب",
    "CK-MB":                           "إنزيم CK-MB، مؤشر على صحة عضلة القلب",
    "CK":                              "إنزيم CK، مؤشر على صحة العضلات والقلب",
    "CPK":                             "إنزيم CPK، مؤشر على صحة العضلات والقلب",
    "BNP":                             "BNP، مؤشر على ضغط عضلة القلب وقصور القلب",
    "NT-proBNP":                       "NT-proBNP، مؤشر على ضغط عضلة القلب وقصور القلب",
    "D-Dimer":                         "D-داي مر، مؤشر على وجود جلطات في الجسم",
    "D-dimer":                         "D-داي مر، مؤشر على وجود جلطات في الجسم",
    "Homocysteine":                    "الهوموسيستئين، مؤشر على خطر أمراض القلب والأوعية",
    "Uric Acid":                       "حمض اليوريك، مؤشر على خطر النقرس وصحة الكلى",
    "Cystatin C":                      "السيستاتين C، مؤشر دقيق على وظائف الكلى",
    "Microalbumin":                    "الألبومين الدقيق، مؤشر على صحة الكلى في مرضى السكري",
    "Urine Albumin":                   "الألبومين في البول، مؤشر على صحة الكلى",
    "GGT":                             "إنزيم GGT، مؤشر على صحة الكبد والقنوات الصفراوية",
    "ALP":                             "إنزيم ALP، مؤشر على صحة الكبد والعظام",
    "LDH":                             "إنزيم LDH، مؤشر على تلف الخلايا في الجسم",
    "Ammonia":                         "الأمونيا، مؤشر على قدرة الكبد على التخلص من السموم",
    "CRP":                             "بروتين CRP، مؤشر على الالتهاب في الجسم",
    "hs-CRP":                          "CRP عالي الحساسية، مؤشر دقيق على التهابات القلب والأوعية",
    "ESR":                             "سرعة ترسب الدم، مؤشر عام على الالتهاب في الجسم",
    "Procalcitonin":                   "البروكالسيتونين، مؤشر على العدوى البكتيرية الشديدة",
    "ANA":                             "الأجسام المضادة النووية، مؤشر على أمراض المناعة الذاتية",
    "RF":                              "عامل الروماتويد، مؤشر على التهاب المفاصل الروماتويدي",
    "Anti-CCP":                        "أجسام مضادة CCP، مؤشر دقيق على الروماتويد",
    "Complement C3":                   "مكمل C3، مؤشر على نشاط الجهاز المناعي",
    "Complement C4":                   "مكمل C4، مؤشر على نشاط الجهاز المناعي",
    "PT":                              "وقت البروثرومبين، مؤشر على قدرة الدم على التجلط",
    "PTT":                             "وقت الثرومبوبلاستين الجزئي، مؤشر على مسار التجلط",
    "APTT":                            "وقت الثرومبوبلاستين الجزئي، مؤشر على مسار التجلط",
    "INR":                             "معدل INR، مؤشر على قدرة الدم على التجلط",
    "Fibrinogen":                      "الفيبرينوجين، مؤشر على عوامل التجلط والالتهاب",
    "Reticulocytes":                   "الخلايا الشبكية، مؤشر على إنتاج النخاع لكريات الدم الجديدة",
    "G6PD":                            "إنزيم G6PD، مؤشر على نقص إنزيم يحمي كريات الدم من التكسر",
    "HGH":                             "هرمون النمو، مؤشر على نشاط الغدة النخامية",
    "Growth Hormone":                  "هرمون النمو، مؤشر على نشاط الغدة النخامية",
    "IGF-1":                           "IGF-1، مؤشر على تأثير هرمون النمو على الأنسجة",
    "PTH":                             "هرمون الجار درقية، مؤشر على توازن الكالسيوم وصحة العظام",
    "Parathyroid Hormone":             "هرمون الجار درقية، مؤشر على توازن الكالسيوم وصحة العظام",
    "Aldosterone":                     "الألدوستيرون، مؤشر على توازن الصوديوم وضغط الدم",
    "Renin":                           "الرينين، مؤشر على تنظيم ضغط الدم",
    "PSA":                             "PSA، مؤشر على صحة غدة البروستاتا",
    "CEA":                             "CEA، مؤشر يُستخدم لمتابعة بعض أنواع السرطان",
    "CA-125":                          "CA-125، مؤشر يُستخدم لمتابعة صحة المبايض",
    "CA 19-9":                         "CA 19-9، مؤشر يُستخدم لمتابعة صحة البنكرياس والقولون",
    "AFP":                             "ألفا فيتوبروتين، مؤشر على صحة الكبد",
    "Beta HCG":                        "هرمون الحمل HCG، مؤشر على الحمل أو بعض الأورام",
    "Beta-HCG":                        "هرمون الحمل HCG، مؤشر على الحمل أو بعض الأورام",
    "HBsAg":                           "مستضد التهاب الكبد B، مؤشر على الإصابة بالتهاب الكبد B",
    "Anti-HCV":                        "أجسام مضادة لالتهاب الكبد C، مؤشر على التعرض لفيروس C",
    "HCV RNA":                         "RNA فيروس الكبد C، مؤشر على وجود الفيروس النشط",
    "HBV DNA":                         "DNA فيروس الكبد B، مؤشر على نشاط فيروس الكبد B",
}

def _ar_test_name(en_name: str) -> str:
    """Return Arabic translation for a test name, or the original if not found."""
    clean = en_name.strip()
    # 1. Exact match
    if clean in AR_TEST_NAMES:
        return AR_TEST_NAMES[clean]
    # 2. Partial match, longest key wins to avoid "HDL" matching "Non-HDL"
    matches = [(key, ar) for key, ar in AR_TEST_NAMES.items() if key.lower() in clean.lower()]
    if matches:
        return max(matches, key=lambda x: len(x[0]))[1]
    return clean  # fallback to English

# Sentence templates for each result state 
EN_NORMAL = "**{name}** — Your result of **{result} {unit}** is within the normal range ({ref}). This is a healthy result."

EN_HIGH = {
    "mild":        "**{name}** — Your result of **{result} {unit}** is slightly above the normal range ({ref}). This is a mild elevation. Possible causes include: {concern}.",
    "moderate":    "**{name}** — Your result of **{result} {unit}** is moderately above the normal range ({ref}). This warrants attention. Common reasons include: {concern}.",
    "significant": "**{name}** — Your result of **{result} {unit}** is significantly above the normal range ({ref}). Please discuss this with your doctor promptly. This could relate to: {concern}.",
}
EN_LOW = {
    "mild":        "**{name}** — Your result of **{result} {unit}** is slightly below the normal range ({ref}). This is a mild decrease. Possible causes include: {concern}.",
    "moderate":    "**{name}** — Your result of **{result} {unit}** is moderately below the normal range ({ref}). This warrants attention. Common reasons include: {concern}.",
    "significant": "**{name}** — Your result of **{result} {unit}** is significantly below the normal range ({ref}). Please discuss this with your doctor promptly. This could relate to: {concern}.",
}

AR_NORMAL = "**{name}**: نتيجتك {result} {unit} ضمن المعدل الطبيعي ({ref}). نتيجة سليمة."
AR_HIGH = {
    "mild":        "**{name}**: نتيجتك {result} {unit} أعلى قليلاً من المعدل الطبيعي ({ref}). ارتفاع طفيف. الأسباب المحتملة تشمل: {concern}.",
    "moderate":    "**{name}**: نتيجتك {result} {unit} أعلى من المعدل الطبيعي ({ref})، يفضل استشارة طبيب. الأسباب الشائعة: {concern}.",
    "significant": "**{name}**: نتيجتك {result} {unit} أعلى بدرجة كبيرة من المعدل الطبيعي ({ref}). يرجى مراجعة طبيبك في أقرب وقت. قد يرتبط ذلك بـ: {concern}.",
}
AR_LOW = {
    "mild":        "**{name}**: نتيجتك {result} {unit} أقل قليلاً من المعدل الطبيعي ({ref}). انخفاض طفيف. من الأسباب المحتملة: {concern}.",
    "moderate":    "**{name}**: نتيجتك {result} {unit} أقل من المعدل الطبيعي ({ref})، يفضل استشارة طبيب. الأسباب الشائعة: {concern}.",
    "significant": "**{name}**: نتيجتك {result} {unit} أقل بشكل كبير من المعدل الطبيعي ({ref}). يرجى مراجعة طبيبك في أقرب وقت. قد يرتبط ذلك بـ: {concern}.",
}

# Causes per test, broken down by severity level
# Each entry: { "mild": "...", "moderate": "...", "significant": "..." }
# Mild = common benign causes. Significant = adds serious possibilities.

EN_CAUSES = {
    "WBC_HIGH": {
        "mild":        "minor infection, stress, vigorous exercise, or recent illness",
        "moderate":    "bacterial infection, inflammation, or use of certain medications",
        "significant": "severe infection, chronic inflammatory condition, or blood disorder requiring evaluation",
    },
    "WBC_LOW": {
        "mild":        "viral infection, or normal variation in some individuals",
        "moderate":    "viral infection, certain medications, or nutritional deficiency",
        "significant": "severe viral illness, bone marrow suppression, or immune disorder",
    },
    "RBC_HIGH": {
        "mild":        "dehydration or living at high altitude",
        "moderate":    "chronic dehydration or lung condition causing low oxygen",
        "significant": "blood disorder causing overproduction of red cells",
    },
    "RBC_LOW": {
        "mild":        "mild nutritional deficiency or natural variation",
        "moderate":    "iron deficiency, vitamin B12 deficiency, or chronic blood loss",
        "significant": "significant anemia requiring investigation of cause",
    },
    "HGB_HIGH": {
        "mild":        "dehydration or living at high altitude",
        "moderate":    "chronic dehydration or a lung condition reducing oxygen levels",
        "significant": "blood disorder requiring evaluation",
    },
    "HGB_LOW": {
        "mild":        "mild iron or nutritional deficiency, or natural variation",
        "moderate":    "iron deficiency anemia, vitamin B12 or folate deficiency",
        "significant": "significant anemia from iron deficiency, bleeding, or chronic disease",
    },
    "HCT_HIGH": {
        "mild":        "dehydration",
        "moderate":    "significant dehydration or reduced oxygen levels",
        "significant": "blood disorder or chronic lung disease",
    },
    "HCT_LOW": {
        "mild":        "mild anemia or nutritional deficiency",
        "moderate":    "iron deficiency anemia or blood loss",
        "significant": "significant anemia requiring investigation",
    },
    "MCV_HIGH": {
        "mild":        "vitamin B12 or folate deficiency",
        "moderate":    "vitamin B12 or folate deficiency causing enlarged red cells",
        "significant": "significant B12 or folate deficiency, or liver disease",
    },
    "MCV_LOW": {
        "mild":        "mild iron deficiency or thalassemia trait",
        "moderate":    "iron deficiency anemia or thalassemia",
        "significant": "significant iron deficiency or inherited blood condition",
    },
    "MCH_HIGH": {
        "mild":        "vitamin B12 or folate deficiency",
        "moderate":    "significant B12 or folate deficiency",
        "significant": "marked nutritional deficiency or blood disorder",
    },
    "MCH_LOW": {
        "mild":        "mild iron deficiency or thalassemia trait",
        "moderate":    "iron deficiency or thalassemia",
        "significant": "significant iron deficiency or inherited hemoglobin condition",
    },
    "PLT_HIGH": {
        "mild":        "recent infection, inflammation, or iron deficiency",
        "moderate":    "active inflammation, infection, or iron deficiency",
        "significant": "significant inflammatory condition or blood disorder requiring evaluation",
    },
    "PLT_LOW": {
        "mild":        "viral infection or normal variation in some individuals",
        "moderate":    "viral infection, certain medications, or immune reaction",
        "significant": "immune platelet disorder, severe infection, or medication effect",
    },
    "NEUT_HIGH": {
        "mild":        "physical or emotional stress, recent exercise, or minor infection",
        "moderate":    "bacterial infection or use of corticosteroids",
        "significant": "significant bacterial infection or inflammatory condition",
    },
    "NEUT_LOW": {
        "mild":        "viral infection or natural variation",
        "moderate":    "viral illness or certain medications",
        "significant": "severe viral infection, medication effect, or immune condition",
    },
    "LYMPH_HIGH": {
        "mild":        "recent or recovering viral infection",
        "moderate":    "active viral infection such as influenza or Epstein-Barr",
        "significant": "significant viral illness or chronic infection requiring evaluation",
    },
    "LYMPH_LOW": {
        "mild":        "physical stress or corticosteroid use",
        "moderate":    "corticosteroid medication, recent illness, or immune suppression",
        "significant": "significant immune suppression requiring evaluation",
    },
    "GLUC_HIGH": {
        "mild":        "prediabetes, high carbohydrate intake before the test, or stress",
        "moderate":    "prediabetes or early diabetes, especially if fasting was not complete",
        "significant": "diabetes or severely uncontrolled blood sugar",
    },
    "GLUC_LOW": {
        "mild":        "extended fasting, skipping a meal, or vigorous exercise",
        "moderate":    "excessive fasting or medication effect",
        "significant": "significant hypoglycemia requiring prompt evaluation",
    },
    "HBA1C_HIGH": {
        "mild":        "prediabetes range (5.7 to 6.4%), with diet and lifestyle adjustments often sufficient",
        "moderate":    "prediabetes or early diabetes requiring lifestyle changes and monitoring",
        "significant": "diabetes range (6.5% and above) requiring medical management",
    },
    "HBA1C_LOW": {
        "mild":        "excellent blood sugar control",
        "moderate":    "very tight blood sugar control or certain types of anemia",
        "significant": "very aggressive glucose control, worth discussing with your doctor",
    },
    "BUN_HIGH": {
        "mild":        "dehydration, high protein intake, or normal variation",
        "moderate":    "dehydration, kidney stress, or high protein diet",
        "significant": "reduced kidney function requiring evaluation",
    },
    "BUN_LOW": {
        "mild":        "low protein intake or overhydration",
        "moderate":    "poor nutrition or liver condition",
        "significant": "significant liver disease or severe malnutrition",
    },
    "CREAT_HIGH": {
        "mild":        "high muscle mass, high protein diet, or intense exercise",
        "moderate":    "reduced kidney filtration or dehydration",
        "significant": "significant reduction in kidney function requiring evaluation",
    },
    "CREAT_LOW": {
        "mild":        "low muscle mass or low protein intake",
        "moderate":    "low muscle mass or poor nutrition",
        "significant": "very low muscle mass or severe malnutrition",
    },
    "ALT_HIGH": {
        "mild":        "fatty liver, vigorous exercise, or certain medications or supplements",
        "moderate":    "fatty liver disease or medication effect on the liver",
        "significant": "significant liver inflammation requiring evaluation",
    },
    "AST_HIGH": {
        "mild":        "vigorous exercise, muscle strain, or fatty liver",
        "moderate":    "liver or muscle condition, or medication effect",
        "significant": "significant liver or muscle damage requiring evaluation",
    },
    "CHOL_HIGH": {
        "mild":        "diet high in saturated fat, lack of physical activity, or genetic tendency",
        "moderate":    "dietary factors, reduced physical activity, or familial tendency",
        "significant": "significant cardiovascular risk factor requiring medical attention",
    },
    "CHOL_LOW": {
        "mild":        "low fat diet or normal variation",
        "moderate":    "very low fat intake, malnutrition, or overactive thyroid",
        "significant": "malnutrition or significant thyroid condition",
    },
    "LDL_HIGH": {
        "mild":        "diet high in saturated fat or genetic tendency",
        "moderate":    "dietary factors, sedentary lifestyle, or hereditary elevated cholesterol",
        "significant": "significant cardiovascular risk requiring dietary changes and medical review",
    },
    "HDL_LOW": {
        "mild":        "sedentary lifestyle, smoking, or diet high in refined carbohydrates",
        "moderate":    "lack of physical activity, smoking, or diet high in refined carbohydrates",
        "significant": "significant cardiovascular risk factor, particularly if combined with high LDL",
    },
    "HDL_HIGH": {
        "mild":        "regular physical activity, healthy diet, or genetic advantage. High HDL is generally a positive sign.",
        "moderate":    "regular exercise and a healthy lifestyle. Elevated HDL is considered protective for heart health.",
        "significant": "very active lifestyle or genetic factors. This is generally favorable, though extremely high levels are rare.",
    },
    "TRIG_HIGH": {
        "mild":        "high carbohydrate or sugar intake, or test not done while fully fasting",
        "moderate":    "high carbohydrate intake or insulin resistance",
        "significant": "metabolic syndrome or significant insulin resistance requiring medical attention",
    },
    "IRON_HIGH": {
        "mild":        "recent iron supplementation or normal variation",
        "moderate":    "excess iron supplementation or repeated blood transfusions",
        "significant": "hereditary iron overload condition requiring evaluation",
    },
    "IRON_LOW": {
        "mild":        "mild iron deficiency or low dietary iron intake",
        "moderate":    "iron deficiency anemia or poor dietary iron absorption",
        "significant": "significant iron deficiency requiring supplementation and evaluation of cause",
    },
    "FERR_HIGH": {
        "mild":        "recent infection, inflammation, or excess iron supplementation",
        "moderate":    "active inflammation or liver condition",
        "significant": "significant inflammatory condition, liver disease, or iron overload",
    },
    "FERR_LOW": {
        "mild":        "low iron stores, often early stage before anemia develops",
        "moderate":    "iron deficiency with depleted stores, supplement likely needed",
        "significant": "severely depleted iron stores, investigation and supplementation required",
    },
    "TIBC_HIGH": {
        "mild":        "mildly low iron, the body increasing capacity to absorb more",
        "moderate":    "iron deficiency causing the body to increase iron binding capacity",
        "significant": "significant iron deficiency",
    },
    "TIBC_LOW": {
        "mild":        "normal variation or chronic illness",
        "moderate":    "iron overload, chronic disease, or malnutrition",
        "significant": "significant iron overload or severe chronic disease",
    },
    "B12_HIGH": {
        "mild":        "recent B12 supplementation",
        "moderate":    "high-dose supplementation or liver condition",
        "significant": "high-dose supplementation or liver disease requiring evaluation",
    },
    "B12_LOW": {
        "mild":        "low dietary intake, especially in those who eat little meat or dairy",
        "moderate":    "B12 deficiency from poor absorption or low dietary intake",
        "significant": "significant B12 deficiency that can affect nerves and blood cell production",
    },
    "FOL_LOW": {
        "mild":        "low dietary intake of leafy vegetables or legumes",
        "moderate":    "folate deficiency from poor diet or absorption problem",
        "significant": "significant folate deficiency affecting red blood cell production",
    },
    "TSH_HIGH": {"mild": "mild underactive thyroid or normal variation","moderate": "underactive thyroid (hypothyroidism) requiring evaluation","significant": "significant underactive thyroid needing medical management"},
    "TSH_LOW":  {"mild": "mild overactive thyroid or stress","moderate": "overactive thyroid (hyperthyroidism) requiring evaluation","significant": "significant overactive thyroid needing prompt attention"},
    "FT4_HIGH": {"mild": "slightly overactive thyroid or medication","moderate": "overactive thyroid (hyperthyroidism)","significant": "significant hyperthyroidism requiring evaluation"},
    "FT4_LOW":  {"mild": "mildly underactive thyroid","moderate": "underactive thyroid (hypothyroidism)","significant": "significant hypothyroidism needing treatment"},
    "FT3_HIGH": {"mild": "slightly elevated thyroid hormone or stress","moderate": "overactive thyroid","significant": "significant hyperthyroidism"},
    "FT3_LOW":  {"mild": "mild thyroid deficiency","moderate": "underactive thyroid or severe illness","significant": "significant thyroid deficiency"},
    "TEST_HIGH": {"mild": "normal variation, high physical activity, or supplements","moderate": "supplement use or hormonal imbalance","significant": "anabolic steroid use or hormonal disorder requiring evaluation"},
    "TEST_LOW":  {"mild": "stress, poor sleep, or low physical activity","moderate": "hormonal deficiency, chronic stress, or age-related decline","significant": "hypogonadism or pituitary disorder requiring evaluation"},
    "PROL_HIGH": {"mild": "stress, exercise, or certain medications","moderate": "certain medications or mild pituitary issue","significant": "pituitary adenoma or significant medication effect requiring evaluation"},
    "PROL_LOW":  {"mild": "normal variation","moderate": "pituitary insufficiency","significant": "significant pituitary disorder"},
    "CORT_HIGH": {"mild": "stress, poor sleep, or morning measurement","moderate": "chronic stress or adrenal gland activity","significant": "adrenal disorder or Cushing syndrome requiring evaluation"},
    "CORT_LOW":  {"mild": "normal variation or evening measurement","moderate": "adrenal insufficiency","significant": "significant adrenal insufficiency requiring evaluation"},
    "FSH_HIGH":  {"mild": "normal variation or early menopause","moderate": "reduced ovarian reserve or menopause","significant": "ovarian failure or primary hypogonadism"},
    "FSH_LOW":   {"mild": "normal variation","moderate": "pituitary or hypothalamic issue","significant": "pituitary disorder affecting reproductive hormones"},
    "LH_HIGH":   {"mild": "normal variation around ovulation","moderate": "early menopause or ovarian issue","significant": "ovarian failure or pituitary disorder"},
    "LH_LOW":    {"mild": "normal variation","moderate": "pituitary or hypothalamic dysfunction","significant": "significant pituitary disorder"},
    "VITD_HIGH": {"mild": "high-dose supplementation","moderate": "excessive vitamin D supplementation","significant": "vitamin D toxicity requiring dose reduction"},
    "VITD_LOW":  {"mild": "limited sun exposure or low dietary intake","moderate": "vitamin D deficiency, common in indoor lifestyles","significant": "severe deficiency affecting bone and immune health"},
    "MAG_HIGH":  {"mild": "magnesium supplementation or kidney issue","moderate": "kidney dysfunction or excessive supplements","significant": "significant kidney dysfunction requiring evaluation"},
    "MAG_LOW":   {"mild": "low dietary intake or stress","moderate": "poor dietary intake, diarrhea, or medication effect","significant": "significant deficiency affecting muscle and heart function"},
    "ZINC_HIGH": {"mild": "zinc supplementation","moderate": "excessive supplementation","significant": "zinc toxicity from prolonged high-dose supplements"},
    "ZINC_LOW":  {"mild": "low dietary intake of meat or seafood","moderate": "poor absorption or low dietary zinc","significant": "significant zinc deficiency affecting immunity and wound healing"},
    "PHOS_HIGH": {"mild": "high dietary intake or mild kidney issue","moderate": "kidney dysfunction or hypoparathyroidism","significant": "significant kidney disease or parathyroid disorder"},
    "PHOS_LOW":  {"mild": "low dietary intake or antacid use","moderate": "malnutrition, malabsorption, or hyperparathyroidism","significant": "severe deficiency affecting energy and bone health"},
    # Cardiac
    "TROP_HIGH": {"mild": "mild heart muscle stress or strenuous exercise","moderate": "cardiac stress or minor heart muscle injury","significant": "significant heart muscle damage requiring urgent evaluation"},
    "BNP_HIGH":  {"mild": "mild cardiac stress or kidney issue","moderate": "heart under increased pressure or early heart failure","significant": "significant heart failure requiring urgent evaluation"},
    "DDIM_HIGH": {"mild": "recent infection, surgery, or inflammation","moderate": "possible clotting abnormality or recent procedure","significant": "significant clotting risk, possible deep vein thrombosis or pulmonary embolism"},
    "URICA_HIGH": {"mild": "high purine diet, red meat, or seafood intake","moderate": "gout risk, high dietary purines, or reduced kidney excretion","significant": "significant gout risk or kidney excretion problem"},
    "URICA_LOW":  {"mild": "low protein diet or normal variation","moderate": "very low protein intake or liver issue","significant": "liver disease or rare metabolic condition"},
    "GGT_HIGH":   {"mild": "fatty liver, certain medications, or high fat diet","moderate": "liver or bile duct issue, or medication effect","significant": "significant liver or bile duct disease requiring evaluation"},
    "ALP_HIGH":   {"mild": "bone growth, healing fracture, or mild liver issue","moderate": "liver, bile duct, or bone disease","significant": "significant liver disease or bone disorder"},
    "LDH_HIGH":   {"mild": "strenuous exercise or minor tissue damage","moderate": "liver, heart, or muscle damage","significant": "significant organ damage requiring investigation"},
    # Inflammation
    "CRP_HIGH":   {"mild": "minor infection, physical stress, or lifestyle factors","moderate": "active infection or inflammatory condition","significant": "significant infection or inflammatory disease requiring evaluation"},
    "ESR_HIGH":   {"mild": "minor infection, anemia, or normal variation in older adults","moderate": "active inflammation, infection, or autoimmune activity","significant": "significant inflammatory or autoimmune disease requiring evaluation"},
    "INR_HIGH":   {"mild": "borderline anticoagulation or mild liver issue","moderate": "over-anticoagulation or liver dysfunction","significant": "significant bleeding risk requiring urgent evaluation"},
    "INR_LOW":    {"mild": "normal variation","moderate": "under-anticoagulation in patients on warfarin","significant": "clotting risk in anticoagulated patients"},
    "PT_HIGH":    {"mild": "mild liver issue or vitamin K deficiency","moderate": "liver dysfunction or significant vitamin K deficiency","significant": "significant liver disease or severe coagulation disorder"},
    # Uric Acid
    "UA_HIGH":    {"mild": "high purine diet or mild dehydration","moderate": "gout risk or reduced kidney excretion","significant": "active gout or significant kidney excretion problem"},
}

AR_CAUSES = {
    "WBC_HIGH": {
        "mild":        "عدوى بسيطة أو مجهود بدني أو ضغط نفسي",
        "moderate":    "عدوى بكتيرية أو التهاب أو تناول بعض الأدوية",
        "significant": "عدوى شديدة أو حالة التهابية مزمنة تحتاج تقييم طبي",
    },
    "WBC_LOW": {
        "mild":        "عدوى فيروسية أو تفاوت طبيعي عند بعض الأشخاص",
        "moderate":    "عدوى فيروسية أو بعض الأدوية أو نقص في التغذية",
        "significant": "عدوى فيروسية شديدة أو تثبيط نخاع العظم يحتاج تقييم",
    },
    "RBC_HIGH": {
        "mild":        "جفاف أو السكن على ارتفاعات عالية",
        "moderate":    "جفاف مزمن أو مشكلة في الرئة تقلل الأكسجين",
        "significant": "اضطراب دموي يسبب إنتاجاً زائداً للكريات الحمراء",
    },
    "RBC_LOW": {
        "mild":        "نقص في التغذية بسيط أو تفاوت طبيعي",
        "moderate":    "نقص الحديد أو فيتامين ب12 أو فقدان دم مزمن",
        "significant": "فقر دم يحتاج تحديد السبب ومعالجته",
    },
    "HGB_HIGH": {
        "mild":        "جفاف أو السكن على ارتفاعات عالية",
        "moderate":    "جفاف مزمن أو حالة في الرئة تقلل مستوى الأكسجين",
        "significant": "اضطراب دموي يحتاج تقييم",
    },
    "HGB_LOW": {
        "mild":        "نقص بسيط في الحديد أو التغذية",
        "moderate":    "أنيميا نقص الحديد أو نقص فيتامين ب12 أو حمض الفوليك",
        "significant": "أنيميا واضحة بسبب نقص الحديد أو النزيف أو مرض مزمن",
    },
    "HCT_HIGH": {
        "mild":        "جفاف",
        "moderate":    "جفاف شديد أو انخفاض مستوى الأكسجين",
        "significant": "اضطراب دموي أو مرض رئوي مزمن",
    },
    "HCT_LOW": {
        "mild":        "أنيميا خفيفة أو نقص في التغذية",
        "moderate":    "أنيميا نقص الحديد أو فقدان دم",
        "significant": "أنيميا واضحة تحتاج تحديد السبب",
    },
    "MCV_HIGH": {
        "mild":        "نقص فيتامين ب12 أو حمض الفوليك",
        "moderate":    "نقص فيتامين ب12 أو حمض الفوليك يسبب تضخم كريات الدم",
        "significant": "نقص واضح في ب12 أو الفوليك أو مرض كبدي",
    },
    "MCV_LOW": {
        "mild":        "نقص بسيط في الحديد أو صفة أنيميا البحر المتوسط",
        "moderate":    "أنيميا نقص الحديد أو أنيميا البحر المتوسط",
        "significant": "نقص حديد واضح أو حالة وراثية في الهيموغلوبين",
    },
    "MCH_HIGH": {
        "mild":        "نقص فيتامين ب12 أو حمض الفوليك",
        "moderate":    "نقص واضح في ب12 أو الفوليك",
        "significant": "نقص حاد في التغذية أو اضطراب دموي",
    },
    "MCH_LOW": {
        "mild":        "نقص بسيط في الحديد أو صفة أنيميا البحر المتوسط",
        "moderate":    "نقص الحديد أو أنيميا البحر المتوسط",
        "significant": "نقص حديد واضح أو حالة وراثية في الهيموغلوبين",
    },
    "PLT_HIGH": {
        "mild":        "عدوى حديثة أو التهاب أو نقص الحديد",
        "moderate":    "التهاب نشط أو عدوى أو نقص الحديد",
        "significant": "حالة التهابية واضحة أو اضطراب دموي يحتاج تقييم",
    },
    "PLT_LOW": {
        "mild":        "عدوى فيروسية أو تفاوت طبيعي",
        "moderate":    "عدوى فيروسية أو بعض الأدوية أو تفاعل مناعي",
        "significant": "اضطراب مناعي في الصفائح أو عدوى شديدة أو تأثير دواء",
    },
    "NEUT_HIGH": {
        "mild":        "ضغط نفسي أو بدني أو مجهود حديث أو عدوى بسيطة",
        "moderate":    "عدوى بكتيرية أو استخدام الكورتيزون",
        "significant": "عدوى بكتيرية واضحة أو حالة التهابية",
    },
    "NEUT_LOW": {
        "mild":        "عدوى فيروسية أو تفاوت طبيعي",
        "moderate":    "مرض فيروسي أو بعض الأدوية",
        "significant": "عدوى فيروسية شديدة أو تأثير دواء أو حالة مناعية",
    },
    "LYMPH_HIGH": {
        "mild":        "التعافي من عدوى فيروسية حديثة",
        "moderate":    "عدوى فيروسية نشطة مثل الإنفلونزا",
        "significant": "مرض فيروسي واضح أو عدوى مزمنة تحتاج تقييم",
    },
    "LYMPH_LOW": {
        "mild":        "ضغط جسدي أو استخدام الكورتيزون",
        "moderate":    "دواء كورتيزون أو مرض حديث أو تثبيط مناعي",
        "significant": "تثبيط مناعي واضح يحتاج تقييم",
    },
    "GLUC_HIGH": {
        "mild":        "مرحلة ما قبل السكري أو تناول كربوهيدرات كثيرة قبل الفحص أو ضغط نفسي",
        "moderate":    "ما قبل السكري أو بداية السكري خصوصاً إذا لم يكن الصيام مكتملاً",
        "significant": "السكري أو ارتفاع حاد في سكر الدم يحتاج تقييم عاجل",
    },
    "GLUC_LOW": {
        "mild":        "صيام طويل أو تأخر وجبة أو مجهود بدني",
        "moderate":    "صيام زائد أو تأثير دواء",
        "significant": "نقص سكر حاد يحتاج تقييم عاجل",
    },
    "HBA1C_HIGH": {
        "mild":        "مرحلة ما قبل السكري (5.7 إلى 6.4%)، وغالباً يكفي تعديل النظام الغذائي والنشاط البدني",
        "moderate":    "ما قبل السكري أو بداية السكري يحتاج متابعة ونمط حياة صحي",
        "significant": "نطاق السكري (6.5% فأكثر) يحتاج متابعة طبية",
    },
    "HBA1C_LOW": {
        "mild":        "تحكم ممتاز في سكر الدم",
        "moderate":    "تحكم جيد جداً في سكر الدم أو نوع من أنواع أنيميا تكسر الدم",
        "significant": "تحكم مكثف جداً في السكر، يفضل مناقشته مع الطبيب",
    },
    "BUN_HIGH": {
        "mild":        "جفاف أو تناول بروتين كثير أو تفاوت طبيعي",
        "moderate":    "جفاف أو إجهاد الكلى أو نظام غذائي غني بالبروتين",
        "significant": "انخفاض في وظائف الكلى يحتاج تقييم",
    },
    "BUN_LOW": {
        "mild":        "قلة البروتين في النظام الغذائي أو الإفراط في شرب الماء",
        "moderate":    "سوء التغذية أو حالة في الكبد",
        "significant": "مرض كبدي واضح أو سوء تغذية شديد",
    },
    "CREAT_HIGH": {
        "mild":        "كتلة عضلية كبيرة أو نظام غذائي غني بالبروتين أو مجهود بدني شديد",
        "moderate":    "انخفاض في ترشيح الكلى أو جفاف",
        "significant": "انخفاض واضح في وظائف الكلى يحتاج تقييم",
    },
    "CREAT_LOW": {
        "mild":        "كتلة عضلية منخفضة أو قلة البروتين في الغذاء",
        "moderate":    "ضعف العضلات أو سوء التغذية",
        "significant": "ضعف عضلي شديد أو سوء تغذية حاد",
    },
    "ALT_HIGH": {
        "mild":        "الكبد الدهني أو مجهود بدني شديد أو بعض الأدوية والمكملات الغذائية",
        "moderate":    "الكبد الدهني أو تأثير دواء على الكبد",
        "significant": "التهاب كبدي واضح يحتاج تقييم",
    },
    "AST_HIGH": {
        "mild":        "مجهود بدني شديد أو إجهاد عضلي أو الكبد الدهني",
        "moderate":    "حالة في الكبد أو العضلات أو تأثير دواء",
        "significant": "تلف واضح في الكبد أو العضلات يحتاج تقييم",
    },
    "CHOL_HIGH": {
        "mild":        "نظام غذائي غني بالدهون المشبعة أو قلة النشاط البدني أو عوامل وراثية",
        "moderate":    "عوامل غذائية أو قلة النشاط أو استعداد وراثي",
        "significant": "عامل خطر قلبي واضح يحتاج رعاية طبية",
    },
    "CHOL_LOW": {
        "mild":        "نظام غذائي منخفض الدهون أو تفاوت طبيعي",
        "moderate":    "سوء التغذية أو فرط نشاط الغدة الدرقية",
        "significant": "سوء تغذية أو حالة واضحة في الغدة الدرقية",
    },
    "LDL_HIGH": {
        "mild":        "نظام غذائي غني بالدهون المشبعة أو عوامل وراثية",
        "moderate":    "عوامل غذائية أو قلة النشاط أو ارتفاع كوليسترول وراثي",
        "significant": "عامل خطر قلبي واضح يحتاج تعديل الغذاء ومراجعة طبية",
    },
    "HDL_LOW": {
        "mild":        "قلة النشاط البدني أو التدخين أو النظام الغذائي",
        "moderate":    "قلة التمرين أو التدخين أو نظام غذائي غني بالسكريات",
        "significant": "عامل خطر قلبي واضح خصوصاً مع ارتفاع الكوليسترول الضار",
    },
    "HDL_HIGH": {
        "mild":        "النشاط البدني المنتظم أو النظام الغذائي الصحي أو عوامل وراثية إيجابية. ارتفاع HDL بشكل عام علامة جيدة.",
        "moderate":    "ممارسة الرياضة والنمط الصحي. ارتفاع HDL يعتبر حماية للقلب.",
        "significant": "نشاط بدني مرتفع أو عوامل وراثية. هذا بشكل عام مؤشر إيجابي.",
    },
    "TRIG_HIGH": {
        "mild":        "تناول كربوهيدرات أو سكريات كثيرة أو عدم الصيام قبل الفحص",
        "moderate":    "كثرة الكربوهيدرات أو مقاومة الأنسولين",
        "significant": "متلازمة استقلابية أو مقاومة أنسولين واضحة تحتاج رعاية طبية",
    },
    "IRON_HIGH": {
        "mild":        "تناول مكملات الحديد مؤخراً أو تفاوت طبيعي",
        "moderate":    "إفراط في مكملات الحديد أو نقل دم متكرر",
        "significant": "حالة وراثية تسبب تراكم الحديد تحتاج تقييم",
    },
    "IRON_LOW": {
        "mild":        "نقص بسيط في الحديد أو قلة الحديد في الغذاء",
        "moderate":    "أنيميا نقص الحديد أو ضعف امتصاصه",
        "significant": "نقص حديد واضح يحتاج مكملات وتحديد السبب",
    },
    "FERR_HIGH": {
        "mild":        "عدوى حديثة أو التهاب أو إفراط في مكملات الحديد",
        "moderate":    "التهاب نشط أو حالة في الكبد",
        "significant": "حالة التهابية واضحة أو مرض كبدي أو تراكم الحديد",
    },
    "FERR_LOW": {
        "mild":        "مخازن حديد منخفضة، وهي مرحلة مبكرة قبل أن تتطور الأنيميا",
        "moderate":    "نقص حديد مع استنزاف المخازن، ويحتمل الحاجة لمكملات",
        "significant": "مخازن حديد شبه فارغة تحتاج مكملات وتحديد السبب",
    },
    "TIBC_HIGH": {
        "mild":        "نقص بسيط في الحديد، الجسم يرفع طاقته لامتصاص المزيد",
        "moderate":    "نقص الحديد يجعل الجسم يزيد قدرته على ربط الحديد",
        "significant": "نقص حديد واضح",
    },
    "TIBC_LOW": {
        "mild":        "تفاوت طبيعي أو مرض مزمن",
        "moderate":    "ارتفاع الحديد أو مرض مزمن أو سوء تغذية",
        "significant": "ارتفاع واضح في الحديد أو مرض مزمن شديد",
    },
    "B12_HIGH": {
        "mild":        "تناول مكملات ب12 مؤخراً",
        "moderate":    "جرعات مكملات عالية أو حالة في الكبد",
        "significant": "إفراط في المكملات أو مرض كبدي يحتاج تقييم",
    },
    "B12_LOW": {
        "mild":        "قلة تناول اللحوم أو منتجات الألبان في الغذاء",
        "moderate":    "نقص ب12 بسبب ضعف الامتصاص أو قلة الغذاء",
        "significant": "نقص واضح في ب12 قد يؤثر على الأعصاب وإنتاج كريات الدم",
    },
    "FOL_LOW": {
        "mild":        "قلة تناول الخضروات الورقية والبقوليات",
        "moderate":    "نقص الفوليك بسبب النظام الغذائي أو ضعف الامتصاص",
        "significant": "نقص واضح في الفوليك يؤثر على إنتاج كريات الدم الحمراء",
    },
    "TSH_HIGH": {"mild": "خمول بسيط في الغدة الدرقية أو تفاوت طبيعي","moderate": "خمول الغدة الدرقية يحتاج تقييم طبي","significant": "خمول واضح في الغدة الدرقية يحتاج علاجاً"},
    "TSH_LOW":  {"mild": "نشاط بسيط زائد في الغدة الدرقية أو ضغط نفسي","moderate": "فرط نشاط الغدة الدرقية يحتاج تقييم طبي","significant": "فرط نشاط واضح في الغدة الدرقية يحتاج اهتماماً عاجلاً"},
    "FT4_HIGH": {"mild": "نشاط بسيط زائد في الغدة أو تأثير دواء","moderate": "فرط نشاط الغدة الدرقية","significant": "فرط نشاط واضح يحتاج تقييماً"},
    "FT4_LOW":  {"mild": "خمول بسيط في الغدة الدرقية","moderate": "خمول الغدة الدرقية","significant": "خمول واضح يحتاج علاجاً"},
    "FT3_HIGH": {"mild": "ارتفاع طفيف في هرمون الغدة أو ضغط نفسي","moderate": "فرط نشاط الغدة الدرقية","significant": "فرط نشاط واضح في الغدة"},
    "FT3_LOW":  {"mild": "نقص بسيط في هرمون الغدة","moderate": "خمول الغدة أو مرض حاد","significant": "نقص واضح في هرمون الغدة الدرقية"},
    "TEST_HIGH": {"mild": "تفاوت طبيعي أو نشاط بدني عالٍ أو مكملات","moderate": "استخدام مكملات هرمونية أو خلل هرموني","significant": "استخدام الستيرويدات البنائية أو اضطراب هرموني يحتاج تقييماً"},
    "TEST_LOW":  {"mild": "ضغط نفسي أو قلة نوم أو قلة نشاط بدني","moderate": "نقص هرموني أو ضغط مزمن أو تراجع مرتبط بالعمر","significant": "نقص هرموني واضح أو اضطراب في الغدة النخامية يحتاج تقييماً"},
    "PROL_HIGH": {"mild": "ضغط نفسي أو رياضة أو بعض الأدوية","moderate": "بعض الأدوية أو مشكلة بسيطة في الغدة النخامية","significant": "ورم حميد في الغدة النخامية أو تأثير دواء يحتاج تقييماً"},
    "PROL_LOW":  {"mild": "تفاوت طبيعي","moderate": "قصور في الغدة النخامية","significant": "اضطراب واضح في الغدة النخامية"},
    "CORT_HIGH": {"mild": "ضغط نفسي أو قلة نوم أو قياس صباحي","moderate": "ضغط مزمن أو نشاط زائد في الغدة الكظرية","significant": "اضطراب في الغدة الكظرية يحتاج تقييماً"},
    "CORT_LOW":  {"mild": "تفاوت طبيعي أو قياس مسائي","moderate": "قصور في الغدة الكظرية","significant": "قصور واضح في الغدة الكظرية يحتاج تقييماً عاجلاً"},
    "FSH_HIGH":  {"mild": "تفاوت طبيعي أو بداية انقطاع الطمث","moderate": "انخفاض الاحتياطي المبيضي أو انقطاع الطمث","significant": "فشل مبيضي أو نقص هرموني أولي"},
    "FSH_LOW":   {"mild": "تفاوت طبيعي","moderate": "مشكلة في الغدة النخامية أو تحت المهاد","significant": "اضطراب في الغدة النخامية يؤثر على الهرمونات التناسلية"},
    "LH_HIGH":   {"mild": "تفاوت طبيعي أو وقت الإباضة","moderate": "بداية انقطاع الطمث أو مشكلة في المبايض","significant": "فشل مبيضي أو اضطراب في الغدة النخامية"},
    "LH_LOW":    {"mild": "تفاوت طبيعي","moderate": "خلل في الغدة النخامية أو تحت المهاد","significant": "اضطراب واضح في الغدة النخامية"},
    "VITD_HIGH": {"mild": "جرعات مكملات فيتامين د عالية","moderate": "إفراط في مكملات فيتامين د","significant": "تسمم بفيتامين د يحتاج تقليل الجرعة"},
    "VITD_LOW":  {"mild": "قلة التعرض للشمس أو قلة الغذاء الغني بالفيتامين","moderate": "نقص فيتامين د، شائع لدى من يقضون وقتاً في الداخل","significant": "نقص حاد يؤثر على العظام والمناعة"},
    "MAG_HIGH":  {"mild": "مكملات المغنيسيوم أو مشكلة بسيطة في الكلى","moderate": "خلل في وظائف الكلى أو إفراط في المكملات","significant": "خلل واضح في الكلى يحتاج تقييماً"},
    "MAG_LOW":   {"mild": "قلة الغذاء الغني بالمغنيسيوم أو ضغط نفسي","moderate": "قلة الغذاء أو الإسهال أو تأثير دواء","significant": "نقص واضح يؤثر على العضلات والقلب"},
    "ZINC_HIGH": {"mild": "مكملات الزنك","moderate": "إفراط في مكملات الزنك","significant": "تسمم بالزنك من جرعات عالية مستمرة"},
    "ZINC_LOW":  {"mild": "قلة تناول اللحوم أو المأكولات البحرية","moderate": "ضعف الامتصاص أو قلة الزنك في الغذاء","significant": "نقص واضح يؤثر على المناعة والتئام الجروح"},
    "PHOS_HIGH": {"mild": "كثرة الغذاء الغني بالفوسفور أو مشكلة بسيطة في الكلى","moderate": "خلل في الكلى أو خمول الغدة الجار درقية","significant": "مرض كلوي واضح أو اضطراب في الغدة الجار درقية"},
    "PHOS_LOW":  {"mild": "قلة الغذاء أو استخدام مضادات الحموضة","moderate": "سوء التغذية أو ضعف الامتصاص أو فرط نشاط الجار درقية","significant": "نقص حاد يؤثر على الطاقة وصحة العظام"},
    # Cardiac
    "TROP_HIGH": {"mild": "إجهاد خفيف لعضلة القلب أو مجهود بدني شديد","moderate": "ضغط على القلب أو إصابة بسيطة في عضلة القلب","significant": "تلف واضح في عضلة القلب يحتاج تقييماً عاجلاً"},
    "BNP_HIGH":  {"mild": "ضغط خفيف على القلب أو مشكلة بسيطة في الكلى","moderate": "القلب تحت ضغط متزايد أو بداية قصور القلب","significant": "قصور قلب واضح يحتاج تقييماً عاجلاً"},
    "DDIM_HIGH": {"mild": "عدوى حديثة أو عملية جراحية أو التهاب","moderate": "احتمال خلل في التجلط أو تدخل طبي حديث","significant": "خطر جلطة واضح يحتاج تقييماً عاجلاً"},
    "URICA_HIGH": {"mild": "كثرة اللحوم الحمراء أو المأكولات البحرية في الغذاء","moderate": "خطر النقرس أو انخفاض إفراز الكلى للحمض","significant": "خطر نقرس واضح أو مشكلة في الكلى"},
    "URICA_LOW":  {"mild": "قلة البروتين في الغذاء أو تفاوت طبيعي","moderate": "قلة البروتين الشديدة أو مشكلة في الكبد","significant": "مرض كبدي أو حالة استقلابية نادرة"},
    "GGT_HIGH":   {"mild": "الكبد الدهني أو بعض الأدوية أو كثرة الدهون","moderate": "مشكلة في الكبد أو القنوات الصفراوية أو تأثير دواء","significant": "مرض واضح في الكبد أو القنوات الصفراوية يحتاج تقييماً"},
    "ALP_HIGH":   {"mild": "نمو العظام أو شفاء كسر أو مشكلة بسيطة في الكبد","moderate": "مرض في الكبد أو القنوات الصفراوية أو العظام","significant": "مرض واضح في الكبد أو اضطراب في العظام"},
    "LDH_HIGH":   {"mild": "مجهود بدني شديد أو تلف بسيط في الأنسجة","moderate": "تلف في الكبد أو القلب أو العضلات","significant": "تلف واضح في أحد الأعضاء يحتاج تحقيقاً"},
    # Inflammation
    "CRP_HIGH":   {"mild": "عدوى بسيطة أو ضغط جسدي أو عوامل نمط حياة","moderate": "عدوى نشطة أو حالة التهابية","significant": "عدوى أو مرض التهابي واضح يحتاج تقييماً"},
    "ESR_HIGH":   {"mild": "عدوى بسيطة أو أنيميا أو تفاوت طبيعي عند كبار السن","moderate": "التهاب نشط أو عدوى أو نشاط مناعي ذاتي","significant": "مرض التهابي أو مناعي واضح يحتاج تقييماً"},
    "INR_HIGH":   {"mild": "تخثر حدودي أو مشكلة بسيطة في الكبد","moderate": "إفراط في مضادات التخثر أو خلل في وظائف الكبد","significant": "خطر نزيف واضح يحتاج تقييماً عاجلاً"},
    "INR_LOW":    {"mild": "تفاوت طبيعي","moderate": "نقص في مضادات التخثر عند من يتناولونها","significant": "خطر تجلط عند المرضى على مضادات التخثر"},
    "PT_HIGH":    {"mild": "مشكلة بسيطة في الكبد أو نقص فيتامين ك","moderate": "خلل في وظائف الكبد أو نقص واضح في فيتامين ك","significant": "مرض كبدي واضح أو اضطراب في التجلط"},
}

# Maps test names to their cause keys
CAUSE_KEY_MAP = [
    ("WBC",           "WBC"),
    ("WHITE BLOOD",   "WBC"),
    ("RBC",           "RBC"),
    ("RED BLOOD",     "RBC"),
    ("HEMOGLOBIN",    "HGB"),
    ("HEMATOCRIT",    "HCT"),
    ("MCV",           "MCV"),
    ("MCH",           "MCH"),
    ("MCHC",          None),      # skip, MCHC rarely needs causes
    ("PLATELET",      "PLT"),
    ("NEUTROPHIL",    "NEUT"),
    ("LYMPHOCYTE",    "LYMPH"),
    ("MONOCYTE",      None),
    ("EOSINOPHIL",    None),
    ("BASOPHIL",      None),
    ("GLUCOSE",       "GLUC"),
    ("HBA1C",         "HBA1C"),
    ("GLYCATED",      "HBA1C"),
    ("BUN",           "BUN"),
    ("UREA",          "BUN"),
    ("CREATININE",    "CREAT"),
    ("EGFR",          None),
    ("SODIUM",        None),
    ("POTASSIUM",     None),
    ("CHLORIDE",      None),
    ("ALT",           "ALT"),
    ("SGPT",          "ALT"),
    ("AST",           "AST"),
    ("SGOT",          "AST"),
    ("BILIRUBIN",     None),
    ("PROTEIN",       None),
    ("ALBUMIN",       None),
    ("CALCIUM",       None),
    ("CHOLESTEROL",   "CHOL"),
    ("LDL",           "LDL"),
    ("HDL",           "HDL"),
    ("TRIGLYCERIDE",  "TRIG"),
    ("NON-HDL",       "LDL"),
    ("SERUM IRON",    "IRON"),
    ("FERRITIN",      "FERR"),
    ("TIBC",          "TIBC"),
    ("TRANSFERRIN",   "TIBC"),
    ("VITAMIN B12",   "B12"),
    ("B12",           "B12"),
    ("FOLATE",        "FOL"),
    ("TSH",           "TSH"),
    ("FREE T3",       "FT3"),
    ("FREE T4",       "FT4"),
    ("T3",            "FT3"),
    ("T4",            "FT4"),
    ("TESTOSTERONE",  "TEST"),
    ("PROLACTIN",     "PROL"),
    ("CORTISOL",      "CORT"),
    ("FSH",           "FSH"),
    ("LH",            "LH"),
    ("VITAMIN D",     "VITD"),
    ("25-OH",         "VITD"),
    ("MAGNESIUM",     "MAG"),
    ("ZINC",          "ZINC"),
    ("PHOSPHORUS",    "PHOS"),
    # Cardiac
    ("TROPONIN",      "TROP"),
    ("BNP",           "BNP"),
    ("NT-PROBNP",     "BNP"),
    ("D-DIMER",       "DDIM"),
    ("D-DAI",         "DDIM"),
    ("URIC ACID",     "URICA"),
    ("GGT",           "GGT"),
    ("ALP",           "ALP"),
    ("LDH",           "LDH"),
    # Inflammation
    ("CRP",           "CRP"),
    ("HS-CRP",        "CRP"),
    ("ESR",           "ESR"),
    ("INR",           "INR"),
    ("PT",            "PT"),
]

def _lookup_key(test_name: str, flag: str):
    up = test_name.upper()
    for keyword, base in CAUSE_KEY_MAP:
        if keyword in up:
            if base is None:
                return None
            return f"{base}_HIGH" if flag == "HIGH" else f"{base}_LOW"
    return None

def _get_cause(test_name, flag, severity, lang="en"):
    key = _lookup_key(test_name, flag)
    if key is None:
        return ("consult your doctor" if lang == "en" else "استشر طبيبك")
    sev = severity if severity in ("mild", "moderate", "significant") else "mild"
    store = EN_CAUSES if lang == "en" else AR_CAUSES
    entry = store.get(key, {})
    return entry.get(sev, entry.get("mild", ("consult your doctor" if lang == "en" else "استشر طبيبك")))

# Builds the overall summary block at the top of the report
def _summary_en(summary, patient_name, critical):
    name = patient_name or "the patient"
    n, h, lo = summary["normal"], summary["high"], summary["low"]
    total = summary["total"]
    lines = [
        f"## Summary for {name}", "",
        f"Out of **{total} tests** in your lab report:",
        f"- **{n} results** are within the normal range",
        f"- **{h + lo} results** are outside the normal range ({h} high, {lo} low)",
    ]
    if critical:
        lines.append(f"\n### Tests Requiring Prompt Attention ({len(critical)}):")
        for t in critical:
            lines.append(f"- **{t['test_name'].split('—')[0].strip()}**: {t['result_raw']} {t['unit']} (range: {t['ref_raw']})")
    return "\n".join(lines)

def _summary_ar(summary, patient_name, critical):
    name = patient_name or "المريض"
    n, h, lo = summary["normal"], summary["high"], summary["low"]
    total = summary["total"]
    total_str  = _ar_results_count(total)
    normal_str = _ar_results_count(n)
    abnorm_str = _ar_results_count(h + lo)
    lines = [
        f"## ملخص النتائج لـ {name}", "",
        f"من أصل {total_str} في تقرير التحليل:",
        f"- {normal_str} ضمن المعدل الطبيعي",
        f"- {abnorm_str} خارج المعدل الطبيعي ({_ar_results_count(h)} مرتفعة، {_ar_results_count(lo)} منخفضة)",
    ]
    if critical:
        lines.append(f"\n### الفحوصات التي تتطلب الرعاية العاجلة ({len(critical)}):")
        for t in critical:
            lines.append(f"- **{t['test_name'].split('—')[0].strip()}**: {t['result_raw']} {t['unit']} (المعدل: {t['ref_raw']})")
    return "\n".join(lines)

# Builds the explanation string for a single test result
def _is_hdl(test_name: str) -> bool:
    """True only for HDL Cholesterol itself, not Non-HDL Cholesterol."""
    up = test_name.upper().strip()
    return up.startswith("HDL") or " HDL " in up

def _explain_en(t):
    name = t.get("full_name") or t["test_name"].split("\u2014")[0].strip()
    sev  = t.get("severity","mild")
    kw   = dict(name=name, result=t["result_raw"], unit=t["unit"], ref=t["ref_raw"],
                concern=_get_cause(t["test_name"], t["flag"], sev, "en"))
    if t["flag"] == "NORMAL": return EN_NORMAL.format(**kw)
    if _is_hdl(t["test_name"]) and t["flag"] == "HIGH":
        return (f"**{name}** -- Your result of **{t['result_raw']} {t['unit']}** is above the reference value ({t['ref_raw']}). "
                f"HDL is the protective cholesterol, so a higher level is generally a positive sign. "
                f"This is often related to: {kw['concern']}")
    s = sev if sev in EN_HIGH else "mild"
    return (EN_HIGH if t["flag"] == "HIGH" else EN_LOW)[s].format(**kw)

def _explain_ar(t):
    en_name = t.get("full_name") or t["test_name"].split("—")[0].strip()
    name = _ar_test_name(en_name)
    sev  = t.get("severity","mild")
    kw   = dict(name=name, result=t["result_raw"], unit=t["unit"], ref=t["ref_raw"],
                concern=_get_cause(t["test_name"], t["flag"], sev, "ar"))
    if t["flag"] == "NORMAL": return AR_NORMAL.format(**kw)
    if _is_hdl(t["test_name"]) and t["flag"] == "HIGH":
        return (f"**{name}**: نتيجتك {t['result_raw']} {t['unit']} أعلى من القيمة المرجعية ({t['ref_raw']}). "
                f"الـ HDL هو الكوليسترول النافع، لذلك ارتفاعه بشكل عام مؤشر إيجابي. "
                f"غالباً يرتبط بـ: {kw['concern']}")
    s = sev if sev in AR_HIGH else "mild"
    return (AR_HIGH if t["flag"] == "HIGH" else AR_LOW)[s].format(**kw)


def generate_explanations(analysis: dict) -> dict:
    patient    = analysis["patient_info"]
    panels_ord = analysis["panels_found"]
    tests      = analysis["tests"]
    summary    = analysis["summary"]
    critical   = analysis["critical"]

    panels = {p: [] for p in panels_ord}
    for t in tests:
        if t["panel"] in panels:
            panels[t["panel"]].append(t)

    panels_en, panels_ar = {}, {}
    for panel, ptests in panels.items():
        blocks_en = [EN_PANEL_INTRO.get(panel, f"**{panel}**"), ""]
        blocks_ar = [AR_PANEL_INTRO.get(panel, f"**{panel}**"), ""]
        for t in ptests:
            blocks_en.append(_explain_en(t))
            blocks_ar.append(_explain_ar(t))
        panels_en[panel] = "\n\n".join(blocks_en)
        panels_ar[panel] = "\n\n".join(blocks_ar)

    return {
        "patient_info": patient,
        "summary": summary,
        "overall_en": _summary_en(summary, patient.get("name"), critical),
        "overall_ar": _summary_ar(summary, patient.get("name"), critical),
        "panels_en": panels_en,
        "panels_ar": panels_ar,
        "panels_order": panels_ord,
        "tests": tests,
        "critical": critical,
        "generated_at": datetime.now().isoformat(),
    }

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")
    from step1_extract import extract_from_pdf
    from step2_compare import analyze_tests
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_data/sample_blood_test.pdf"
    expl = generate_explanations(analyze_tests(extract_from_pdf(path)))
    print(expl["overall_ar"])
    print("\n---\n")
    first = expl["panels_order"][0]
    print(expl["panels_ar"][first][:1200])
