"""
Badeel synthetic pharmacopeia.

FICTIONAL DRUG UNIVERSE. Every ingredient and brand name below is invented.
ATC code structure is real (so class-based substitution logic is realistic) but
no fictional drug corresponds to any real medicine. Not for clinical use.

Design intent: the data is authored so that a naive retrieve-and-answer system
fails in specific, labelled ways. See eval_cases.py for the traps.
"""

# ---------------------------------------------------------------------------
# INGREDIENTS
# ---------------------------------------------------------------------------
# nti          -> narrow therapeutic index, must escalate rather than substitute
# equiv_group  -> ingredients sharing this are direct therapeutic alternatives
# ---------------------------------------------------------------------------

INGREDIENTS = [
    # --- C07 beta blockers -------------------------------------------------
    dict(
        id="ING001", name="Veltolol", atc="C07AB07", nti=False,
        drug_class="Selective beta-1 adrenergic blocker",
        equiv_group="beta_blocker_selective",
        indications=["Hypertension", "Chronic stable angina", "Chronic heart failure (stable)"],
        forms=[("tablet", ["2.5 mg", "5 mg", "10 mg"]),
               ("tablet, extended release", ["5 mg", "10 mg"])],
        contraindications=["Severe bronchial asthma", "Second or third degree AV block",
                           "Cardiogenic shock", "Untreated phaeochromocytoma"],
        interactions=[("Verapaxil", "major", "Additive AV nodal suppression, risk of bradyarrhythmia"),
                      ("Gliclazex", "moderate", "Masks adrenergic warning signs of hypoglycaemia")],
        pregnancy="Category C. Use only if benefit outweighs foetal risk.",
        renal="No dose adjustment for CrCl above 30 mL/min.",
        hepatic="Reduce dose in moderate to severe impairment.",
        adverse=["Bradycardia", "Fatigue", "Cold extremities", "Sleep disturbance"],
        notes="Extended release form is not interchangeable milligram for milligram "
              "with the immediate release tablet. Conversion requires prescriber review.",
    ),
    dict(
        id="ING002", name="Menoprolol", atc="C07AB02", nti=False,
        drug_class="Selective beta-1 adrenergic blocker",
        equiv_group="beta_blocker_selective",
        indications=["Hypertension", "Chronic stable angina", "Migraine prophylaxis"],
        forms=[("tablet", ["25 mg", "50 mg", "100 mg"])],
        contraindications=["Severe bronchial asthma", "Second or third degree AV block",
                           "Decompensated heart failure"],
        interactions=[("Verapaxil", "major", "Additive AV nodal suppression"),
                      ("Veltoprofen", "moderate", "NSAIDs may blunt antihypertensive effect")],
        pregnancy="Category C. Foetal growth restriction reported with prolonged use.",
        renal="No adjustment required.",
        hepatic="Extensively metabolised. Halve dose in cirrhosis.",
        adverse=["Bradycardia", "Dizziness", "Bronchospasm in susceptible patients"],
        notes="Lowest available strength is 25 mg. Cannot match sub-5 mg regimens "
              "used with other agents in this class.",
    ),
    dict(
        id="ING003", name="Carvedanol", atc="C07AG02", nti=False,
        drug_class="Non-selective beta blocker with alpha-1 blockade",
        equiv_group="beta_blocker_nonselective",
        indications=["Chronic heart failure", "Hypertension"],
        forms=[("tablet", ["3.125 mg", "6.25 mg", "12.5 mg", "25 mg"])],
        contraindications=["Bronchial asthma of any severity", "Decompensated heart failure",
                           "Severe hepatic impairment", "Second or third degree AV block"],
        interactions=[("Gliclazex", "moderate", "Enhanced hypoglycaemic effect"),
                      ("Verapaxil", "major", "Severe bradycardia and hypotension")],
        pregnancy="Category C.",
        renal="No adjustment required.",
        hepatic="Contraindicated in severe impairment.",
        adverse=["Postural hypotension", "Fatigue", "Weight gain"],
        notes="Non-selective. Carries a stronger bronchospasm warning than the "
              "beta-1 selective agents and is not an appropriate swap for a patient "
              "with reactive airway disease.",
    ),

    # --- C09 renin angiotensin --------------------------------------------
    dict(
        id="ING004", name="Lisinopran", atc="C09AA03", nti=False,
        drug_class="Angiotensin converting enzyme inhibitor",
        equiv_group="raas_blocker",
        indications=["Hypertension", "Heart failure", "Diabetic nephropathy"],
        forms=[("tablet", ["5 mg", "10 mg", "20 mg"])],
        contraindications=["Pregnancy", "History of angioedema", "Bilateral renal artery stenosis"],
        interactions=[("Veltoprofen", "major", "Increased risk of acute kidney injury"),
                      ("Valsartex", "major", "Dual RAAS blockade, hyperkalaemia and renal failure")],
        pregnancy="Contraindicated in all trimesters. Discontinue immediately if pregnancy detected.",
        renal="Reduce dose if CrCl below 30 mL/min. Monitor potassium.",
        hepatic="No adjustment required.",
        adverse=["Dry persistent cough", "Hyperkalaemia", "First dose hypotension"],
        notes="Dry cough is the commonest reason for switching within this group.",
    ),
    dict(
        id="ING005", name="Valsartex", atc="C09CA03", nti=False,
        drug_class="Angiotensin II receptor blocker",
        equiv_group="raas_blocker",
        indications=["Hypertension", "Heart failure", "Post myocardial infarction"],
        forms=[("tablet", ["40 mg", "80 mg", "160 mg"])],
        contraindications=["Pregnancy", "Bilateral renal artery stenosis", "Severe hepatic impairment"],
        interactions=[("Lisinopran", "major", "Dual RAAS blockade"),
                      ("Veltoprofen", "major", "Increased risk of acute kidney injury")],
        pregnancy="Contraindicated in all trimesters.",
        renal="Monitor potassium and creatinine.",
        hepatic="Contraindicated in severe impairment.",
        adverse=["Dizziness", "Hyperkalaemia"],
        notes="Does not cause the dry cough associated with ACE inhibitors, which "
              "makes it the usual switch target from Lisinopran.",
    ),
    dict(
        id="ING006", name="Valsartex + Hydroclorix", atc="C09DA03", nti=False,
        drug_class="Angiotensin II receptor blocker with thiazide diuretic",
        equiv_group="raas_blocker_combination",
        is_combination=True,
        components=["Valsartex", "Hydroclorix"],
        indications=["Hypertension not adequately controlled on monotherapy"],
        forms=[("tablet", ["80 mg / 12.5 mg", "160 mg / 12.5 mg", "160 mg / 25 mg"])],
        contraindications=["Pregnancy", "Anuria", "Severe hepatic impairment", "Sulfonamide hypersensitivity"],
        interactions=[("Veltoprofen", "major", "Reduced diuretic efficacy and renal risk")],
        pregnancy="Contraindicated in all trimesters.",
        renal="Avoid if CrCl below 30 mL/min due to the thiazide component.",
        hepatic="Contraindicated in severe impairment.",
        adverse=["Hypokalaemia", "Hyponatraemia", "Dizziness"],
        notes="Fixed dose combination. Substituting with a single agent leaves one "
              "component untreated and is not an equivalent swap.",
    ),

    # --- B01 anticoagulants (NTI) -----------------------------------------
    dict(
        id="ING007", name="Warfaridine", atc="B01AA03", nti=True,
        drug_class="Vitamin K antagonist oral anticoagulant",
        equiv_group="anticoagulant_vka",
        indications=["Atrial fibrillation", "Venous thromboembolism", "Mechanical heart valve"],
        forms=[("tablet", ["1 mg", "3 mg", "5 mg"])],
        contraindications=["Active bleeding", "Pregnancy", "Severe uncontrolled hypertension"],
        interactions=[("Veltoprofen", "major", "Markedly increased bleeding risk"),
                      ("Azithromycex", "major", "Potentiates anticoagulant effect, INR rise"),
                      ("Diclofenax", "major", "Increased bleeding risk")],
        pregnancy="Contraindicated. Teratogenic in first trimester.",
        renal="Monitor closely. No fixed adjustment.",
        hepatic="Increased sensitivity. Reduce dose and monitor INR.",
        adverse=["Bleeding", "Bruising", "Rare skin necrosis"],
        notes="NARROW THERAPEUTIC INDEX. Dose is individualised against INR. "
              "Substitution of brand, strength or product must not be made at the "
              "pharmacy counter. Refer to the prescriber.",
    ),
    dict(
        id="ING008", name="Xarelide", atc="B01AF01", nti=False,
        drug_class="Direct factor Xa inhibitor",
        equiv_group="anticoagulant_doac",
        indications=["Atrial fibrillation", "Venous thromboembolism treatment and prophylaxis"],
        forms=[("tablet", ["10 mg", "15 mg", "20 mg"])],
        contraindications=["Active bleeding", "Mechanical heart valve", "Pregnancy",
                           "Severe hepatic impairment with coagulopathy"],
        interactions=[("Veltoprofen", "major", "Increased bleeding risk"),
                      ("Ciproflaxen", "moderate", "Raised plasma concentration")],
        pregnancy="Contraindicated.",
        renal="Avoid if CrCl below 15 mL/min.",
        hepatic="Contraindicated with coagulopathy.",
        adverse=["Bleeding", "Anaemia"],
        notes="Not interchangeable with vitamin K antagonists. Explicitly "
              "contraindicated where a mechanical valve is present.",
    ),

    # --- H03 thyroid (NTI) -------------------------------------------------
    dict(
        id="ING009", name="Levothyral", atc="H03AA01", nti=True,
        drug_class="Synthetic thyroid hormone",
        equiv_group="thyroid_replacement",
        indications=["Primary hypothyroidism", "Post thyroidectomy replacement"],
        forms=[("tablet", ["25 mcg", "50 mcg", "75 mcg", "100 mcg", "125 mcg"])],
        contraindications=["Untreated adrenal insufficiency", "Acute myocardial infarction",
                           "Untreated thyrotoxicosis"],
        interactions=[("Omeprazine", "moderate", "Reduced absorption"),
                      ("Metformax", "minor", "Altered glycaemic control")],
        pregnancy="Category A. Requirements typically increase during pregnancy.",
        renal="No adjustment required.",
        hepatic="No adjustment required.",
        adverse=["Palpitations", "Weight loss", "Insomnia with over-replacement"],
        notes="NARROW THERAPEUTIC INDEX. Brand to brand bioequivalence is not "
              "assumed. Switching product requires thyroid function retesting six "
              "to eight weeks later. Do not substitute at the counter.",
    ),

    # --- N03 antiepileptic (NTI) ------------------------------------------
    dict(
        id="ING010", name="Valproax", atc="N03AG01", nti=True,
        drug_class="Broad spectrum antiepileptic",
        equiv_group="antiepileptic_broad",
        indications=["Generalised epilepsy", "Focal epilepsy", "Bipolar mania prophylaxis"],
        forms=[("tablet, enteric coated", ["200 mg", "500 mg"]),
               ("oral solution", ["200 mg/5 mL"])],
        contraindications=["Pregnancy", "Women of childbearing potential without pregnancy prevention",
                           "Hepatic impairment", "Known urea cycle disorder"],
        interactions=[("Keppratex", "moderate", "Additive sedation"),
                      ("Warfaridine", "major", "Displacement from protein binding, bleeding risk")],
        pregnancy="Contraindicated. Established teratogen with neurodevelopmental risk.",
        renal="Reduce dose in severe impairment.",
        hepatic="Contraindicated.",
        adverse=["Tremor", "Weight gain", "Hair loss", "Hepatotoxicity"],
        notes="NARROW THERAPEUTIC INDEX. Antiepileptic product switching is "
              "associated with breakthrough seizures. Refer to prescriber.",
    ),
    dict(
        id="ING011", name="Keppratex", atc="N03AX14", nti=False,
        drug_class="SV2A ligand antiepileptic",
        equiv_group="antiepileptic_broad",
        indications=["Focal epilepsy", "Generalised tonic clonic seizures"],
        forms=[("tablet", ["250 mg", "500 mg", "1000 mg"]),
               ("oral solution", ["100 mg/mL"])],
        contraindications=["Known hypersensitivity"],
        interactions=[("Valproax", "moderate", "Additive sedation")],
        pregnancy="Category C. Preferred over Valproax where treatment is required.",
        renal="Dose reduction required below CrCl 50 mL/min.",
        hepatic="No adjustment for mild to moderate impairment.",
        adverse=["Somnolence", "Irritability", "Behavioural change"],
        notes="Different mechanism from Valproax. Not a like for like substitution "
              "even though both are broad spectrum.",
    ),

    # --- M01 / N02 analgesics ---------------------------------------------
    dict(
        id="ING012", name="Veltoprofen", atc="M01AE01", nti=False,
        drug_class="Non-steroidal anti-inflammatory drug",
        equiv_group="nsaid",
        indications=["Mild to moderate pain", "Inflammatory arthritis", "Fever"],
        forms=[("tablet", ["200 mg", "400 mg", "600 mg"]),
               ("oral suspension", ["100 mg/5 mL"])],
        contraindications=["Active peptic ulcer", "Severe renal impairment", "Third trimester pregnancy",
                           "History of NSAID induced asthma"],
        interactions=[("Warfaridine", "major", "Markedly increased bleeding risk"),
                      ("Lisinopran", "major", "Acute kidney injury risk"),
                      ("Xarelide", "major", "Increased bleeding risk")],
        pregnancy="Avoid in third trimester. Premature ductus closure.",
        renal="Contraindicated if CrCl below 30 mL/min.",
        hepatic="Use with caution.",
        adverse=["Dyspepsia", "Gastrointestinal bleeding", "Fluid retention"],
        notes="Class effect. Swapping one NSAID for another does not remove the "
              "bleeding or renal interaction.",
    ),
    dict(
        id="ING013", name="Diclofenax", atc="M01AB05", nti=False,
        drug_class="Non-steroidal anti-inflammatory drug",
        equiv_group="nsaid",
        indications=["Musculoskeletal pain", "Osteoarthritis", "Post operative pain"],
        forms=[("tablet, enteric coated", ["25 mg", "50 mg"]),
               ("gel", ["1%"]),
               ("suppository", ["100 mg"])],
        contraindications=["Active peptic ulcer", "Established ischaemic heart disease",
                           "Severe renal impairment", "Third trimester pregnancy"],
        interactions=[("Warfaridine", "major", "Increased bleeding risk"),
                      ("Lisinopran", "major", "Acute kidney injury risk")],
        pregnancy="Avoid in third trimester.",
        renal="Contraindicated in severe impairment.",
        hepatic="Monitor transaminases with prolonged use.",
        adverse=["Dyspepsia", "Raised transaminases", "Cardiovascular events"],
        notes="Carries a cardiovascular warning that Veltoprofen does not, which "
              "makes the two non-equivalent in ischaemic heart disease.",
    ),
    dict(
        id="ING014", name="Paracetamide", atc="N02BE01", nti=False,
        drug_class="Non-opioid analgesic and antipyretic",
        equiv_group="simple_analgesic",
        indications=["Mild pain", "Fever"],
        forms=[("tablet", ["500 mg", "1000 mg"]),
               ("oral suspension", ["120 mg/5 mL", "250 mg/5 mL"]),
               ("suppository", ["125 mg", "250 mg"])],
        contraindications=["Severe hepatic impairment"],
        interactions=[("Warfaridine", "moderate", "Prolonged regular use may raise INR")],
        pregnancy="Category A. Analgesic of choice in pregnancy.",
        renal="Extend dosing interval in severe impairment.",
        hepatic="Reduce total daily dose. Avoid in severe impairment.",
        adverse=["Rare hepatotoxicity in overdose"],
        notes="Not an anti-inflammatory. Substituting an NSAID with Paracetamide "
              "loses the anti-inflammatory action and is a therapeutic downgrade, "
              "not an equivalence.",
    ),

    # --- J01 antibiotics ---------------------------------------------------
    dict(
        id="ING015", name="Amoxicillex", atc="J01CA04", nti=False,
        drug_class="Aminopenicillin antibiotic",
        equiv_group="penicillin",
        indications=["Respiratory tract infection", "Otitis media", "Urinary tract infection"],
        forms=[("capsule", ["250 mg", "500 mg"]),
               ("oral suspension", ["125 mg/5 mL", "250 mg/5 mL"])],
        contraindications=["Penicillin hypersensitivity"],
        interactions=[("Warfaridine", "moderate", "Possible INR elevation")],
        pregnancy="Category B.",
        renal="Extend interval if CrCl below 30 mL/min.",
        hepatic="No adjustment required.",
        adverse=["Diarrhoea", "Rash", "Candidiasis"],
        notes="Absolutely contraindicated in documented penicillin allergy. No "
              "other beta lactam is a safe substitute in confirmed anaphylaxis.",
    ),
    dict(
        id="ING016", name="Azithromycex", atc="J01FA10", nti=False,
        drug_class="Macrolide antibiotic",
        equiv_group="macrolide",
        indications=["Community acquired pneumonia", "Pharyngitis", "Atypical infection"],
        forms=[("tablet", ["250 mg", "500 mg"]),
               ("oral suspension", ["200 mg/5 mL"])],
        contraindications=["Known QT prolongation", "Macrolide hypersensitivity"],
        interactions=[("Warfaridine", "major", "Potentiates anticoagulation"),
                      ("Ciproflaxen", "major", "Additive QT prolongation")],
        pregnancy="Category B.",
        renal="No adjustment for mild to moderate impairment.",
        hepatic="Avoid in severe impairment.",
        adverse=["Nausea", "QT prolongation", "Diarrhoea"],
        notes="Common alternative where penicillin allergy is documented.",
    ),
    dict(
        id="ING017", name="Ciproflaxen", atc="J01MA02", nti=False,
        drug_class="Fluoroquinolone antibiotic",
        equiv_group="fluoroquinolone",
        indications=["Complicated urinary tract infection", "Gastrointestinal infection"],
        forms=[("tablet", ["250 mg", "500 mg", "750 mg"])],
        contraindications=["Age under 18 years except in specified indications",
                           "History of tendon disorder with quinolones", "Myasthenia gravis"],
        interactions=[("Azithromycex", "major", "Additive QT prolongation"),
                      ("Xarelide", "moderate", "Raised plasma concentration")],
        pregnancy="Avoid. Cartilage toxicity in animal studies.",
        renal="Reduce dose if CrCl below 30 mL/min.",
        hepatic="Caution.",
        adverse=["Tendinopathy", "QT prolongation", "Photosensitivity"],
        notes="Carries a tendon rupture and paediatric restriction that the other "
              "oral antibiotics in this dataset do not.",
    ),

    # --- A02 gastro --------------------------------------------------------
    dict(
        id="ING018", name="Omeprazine", atc="A02BC01", nti=False,
        drug_class="Proton pump inhibitor",
        equiv_group="ppi",
        indications=["Gastro-oesophageal reflux", "Peptic ulcer", "NSAID ulcer prophylaxis"],
        forms=[("capsule, enteric coated", ["20 mg", "40 mg"])],
        contraindications=["Known hypersensitivity"],
        interactions=[("Clopidogrex", "major", "Reduced antiplatelet activation"),
                      ("Levothyral", "moderate", "Reduced thyroid hormone absorption")],
        pregnancy="Category C.",
        renal="No adjustment required.",
        hepatic="Reduce dose in severe impairment.",
        adverse=["Headache", "Hypomagnesaemia with long term use"],
        notes="Interacts with Clopidogrex through the same enzyme pathway. "
              "Pantoprazine is the preferred substitute in that scenario.",
    ),
    dict(
        id="ING019", name="Pantoprazine", atc="A02BC02", nti=False,
        drug_class="Proton pump inhibitor",
        equiv_group="ppi",
        indications=["Gastro-oesophageal reflux", "Peptic ulcer"],
        forms=[("tablet, enteric coated", ["20 mg", "40 mg"])],
        contraindications=["Known hypersensitivity"],
        interactions=[("Levothyral", "moderate", "Reduced thyroid hormone absorption")],
        pregnancy="Category B.",
        renal="No adjustment required.",
        hepatic="Reduce dose in severe impairment.",
        adverse=["Headache", "Diarrhoea"],
        notes="Preferred proton pump inhibitor where Clopidogrex is co-prescribed, "
              "as it lacks the clinically significant enzyme interaction.",
    ),
    dict(
        id="ING020", name="Clopidogrex", atc="B01AC04", nti=False,
        drug_class="P2Y12 antiplatelet agent",
        equiv_group="antiplatelet",
        indications=["Secondary prevention after myocardial infarction", "Stent thrombosis prophylaxis"],
        forms=[("tablet", ["75 mg"])],
        contraindications=["Active bleeding", "Severe hepatic impairment"],
        interactions=[("Omeprazine", "major", "Reduced antiplatelet activation"),
                      ("Veltoprofen", "major", "Increased bleeding risk")],
        pregnancy="Category B.",
        renal="No adjustment required.",
        hepatic="Contraindicated in severe impairment.",
        adverse=["Bleeding", "Bruising"],
        notes="Only one strength is manufactured in this registry.",
    ),

    # --- A10 antidiabetic --------------------------------------------------
    dict(
        id="ING021", name="Metformax", atc="A10BA02", nti=False,
        drug_class="Biguanide antidiabetic",
        equiv_group="antidiabetic_oral",
        indications=["Type 2 diabetes mellitus", "Polycystic ovary syndrome"],
        forms=[("tablet", ["500 mg", "850 mg", "1000 mg"]),
               ("tablet, extended release", ["500 mg", "1000 mg"])],
        contraindications=["eGFR below 30 mL/min/1.73m2", "Acute metabolic acidosis",
                           "Acute decompensated heart failure"],
        interactions=[("Ciproflaxen", "minor", "Possible glycaemic fluctuation")],
        pregnancy="Category B.",
        renal="Contraindicated below eGFR 30. Halve dose between 30 and 45.",
        hepatic="Avoid in significant impairment due to lactic acidosis risk.",
        adverse=["Gastrointestinal upset", "B12 deficiency", "Rare lactic acidosis"],
        notes="Extended release form improves gastrointestinal tolerance but is "
              "not milligram equivalent in dosing frequency.",
    ),
    dict(
        id="ING022", name="Gliclazex", atc="A10BB09", nti=False,
        drug_class="Sulfonylurea antidiabetic",
        equiv_group="antidiabetic_oral",
        indications=["Type 2 diabetes mellitus"],
        forms=[("tablet", ["30 mg", "60 mg"]),
               ("tablet, modified release", ["30 mg", "60 mg"])],
        contraindications=["Type 1 diabetes", "Severe renal impairment", "Sulfonamide hypersensitivity"],
        interactions=[("Veltolol", "moderate", "Masked hypoglycaemia warning signs"),
                      ("Carvedanol", "moderate", "Enhanced hypoglycaemic effect")],
        pregnancy="Not recommended. Switch to insulin.",
        renal="Avoid in severe impairment.",
        hepatic="Avoid in severe impairment.",
        adverse=["Hypoglycaemia", "Weight gain"],
        notes="Carries hypoglycaemia risk that Metformax does not. The two are in "
              "the same broad class but are not risk equivalent.",
    ),

    # --- C10 statins -------------------------------------------------------
    dict(
        id="ING023", name="Atorvastin", atc="C10AA05", nti=False,
        drug_class="HMG-CoA reductase inhibitor",
        equiv_group="statin",
        indications=["Hypercholesterolaemia", "Cardiovascular risk reduction"],
        forms=[("tablet", ["10 mg", "20 mg", "40 mg", "80 mg"])],
        contraindications=["Active liver disease", "Pregnancy", "Breastfeeding"],
        interactions=[("Azithromycex", "moderate", "Increased myopathy risk")],
        pregnancy="Contraindicated.",
        renal="No adjustment required.",
        hepatic="Contraindicated in active liver disease.",
        adverse=["Myalgia", "Raised transaminases"],
        notes="Potency differs from Rosuvastin. Milligram for milligram "
              "substitution overdoses or underdoses the patient.",
    ),
    dict(
        id="ING024", name="Rosuvastin", atc="C10AA07", nti=False,
        drug_class="HMG-CoA reductase inhibitor",
        equiv_group="statin",
        indications=["Hypercholesterolaemia", "Cardiovascular risk reduction"],
        forms=[("tablet", ["5 mg", "10 mg", "20 mg", "40 mg"])],
        contraindications=["Active liver disease", "Pregnancy", "Severe renal impairment"],
        interactions=[("Warfaridine", "moderate", "INR elevation reported")],
        pregnancy="Contraindicated.",
        renal="Avoid 40 mg dose if CrCl below 60 mL/min.",
        hepatic="Contraindicated in active liver disease.",
        adverse=["Myalgia", "Proteinuria at high dose"],
        notes="Approximately twice as potent as Atorvastin on a milligram basis. "
              "Dose conversion is required, not direct substitution.",
    ),

    # --- Orphan / no alternative ------------------------------------------
    dict(
        id="ING025", name="Denufolin", atc="V03AB99", nti=False,
        drug_class="Specific chelating antidote",
        equiv_group="orphan_antidote",
        indications=["Acute heavy metal toxicity, specialist use only"],
        forms=[("solution for injection", ["100 mg/mL"])],
        contraindications=["Known hypersensitivity"],
        interactions=[],
        pregnancy="Use only where life threatening toxicity is present.",
        renal="Dose reduction required. Monitor closely.",
        hepatic="No data.",
        adverse=["Infusion site reaction", "Hypotension"],
        notes="No therapeutic alternative exists in this registry. There is no "
              "same-class and no same-group substitute. A shortage of this product "
              "must be escalated, never substituted.",
    ),

    # --- Verapaxil (interaction partner) ----------------------------------
    dict(
        id="ING026", name="Verapaxil", atc="C08DA01", nti=False,
        drug_class="Non-dihydropyridine calcium channel blocker",
        equiv_group="ccb_nondhp",
        indications=["Hypertension", "Supraventricular tachycardia", "Angina"],
        forms=[("tablet", ["40 mg", "80 mg"]),
               ("tablet, sustained release", ["120 mg", "240 mg"])],
        contraindications=["Severe left ventricular dysfunction", "Second or third degree AV block",
                           "Concurrent beta blockade in heart failure"],
        interactions=[("Veltolol", "major", "Additive AV nodal suppression"),
                      ("Carvedanol", "major", "Severe bradycardia")],
        pregnancy="Category C.",
        renal="No adjustment required.",
        hepatic="Reduce dose in cirrhosis.",
        adverse=["Constipation", "Bradycardia", "Ankle oedema"],
        notes="Sustained release and immediate release forms are not "
              "interchangeable on a per-tablet basis.",
    ),
]


# ---------------------------------------------------------------------------
# BRANDS
# (brand, arabic, ingredient_id, strength, form, manufacturer, price_egp, status)
# ---------------------------------------------------------------------------

BRANDS = [
    # Veltolol
    ("Cardex",        "كاردكس",     "ING001", "5 mg",   "tablet", "Nile Pharma",     48.00, "available"),
    ("Cardex",        "كاردكس",     "ING001", "10 mg",  "tablet", "Nile Pharma",     72.00, "shortage"),
    ("Cardex",        "كاردكس",     "ING001", "2.5 mg", "tablet", "Nile Pharma",     35.00, "available"),
    ("Veltocor",      "فيلتوكور",   "ING001", "5 mg",   "tablet", "Delta Labs",      41.50, "available"),
    ("Bislon XR",     "بيسلون",     "ING001", "5 mg",   "tablet, extended release", "Horus Pharm", 88.00, "available"),
    # Trap: same-looking brand, different product entirely
    ("Cardex Plus",   "كاردكس بلس", "ING006", "160 mg / 12.5 mg", "tablet", "Nile Pharma", 130.00, "available"),

    # Menoprolol
    ("Menocard",      "مينوكارد",   "ING002", "50 mg",  "tablet", "Delta Labs",      39.00, "available"),
    ("Prolix",        "برولكس",     "ING002", "25 mg",  "tablet", "Sphinx Pharma",   28.00, "available"),
    ("Prolix",        "برولكس",     "ING002", "100 mg", "tablet", "Sphinx Pharma",   66.00, "available"),

    # Carvedanol
    ("Carvex",        "كارفكس",     "ING003", "6.25 mg","tablet", "Horus Pharm",     52.00, "available"),
    ("Carvex",        "كارفكس",     "ING003", "12.5 mg","tablet", "Horus Pharm",     74.00, "available"),
    ("Dilanor",       "ديلانور",    "ING003", "25 mg",  "tablet", "Nile Pharma",     95.00, "available"),

    # Lisinopran
    ("Lispril",       "ليسبريل",    "ING004", "10 mg",  "tablet", "Delta Labs",      44.00, "available"),
    ("Lispril",       "ليسبريل",    "ING004", "20 mg",  "tablet", "Delta Labs",      61.00, "shortage"),
    ("Tensodel",      "تنسوديل",    "ING004", "10 mg",  "tablet", "Sphinx Pharma",   38.50, "available"),

    # Valsartex
    ("Valtec",        "فالتك",      "ING005", "80 mg",  "tablet", "Horus Pharm",     92.00, "available"),
    ("Valtec",        "فالتك",      "ING005", "160 mg", "tablet", "Horus Pharm",     140.00, "available"),
    ("Sartanex",      "سارتانكس",   "ING005", "80 mg",  "tablet", "Nile Pharma",     85.00, "available"),

    # Valsartex + Hydroclorix
    ("Valtec Plus",   "فالتك بلس",  "ING006", "80 mg / 12.5 mg", "tablet", "Horus Pharm", 118.00, "shortage"),
    ("Valtec Plus",   "فالتك بلس",  "ING006", "160 mg / 12.5 mg","tablet", "Horus Pharm", 145.00, "available"),

    # Warfaridine (NTI)
    ("Coagulex",      "كواجولكس",   "ING007", "5 mg",   "tablet", "Sphinx Pharma",   55.00, "shortage"),
    ("Coagulex",      "كواجولكس",   "ING007", "3 mg",   "tablet", "Sphinx Pharma",   48.00, "available"),
    ("Warfex",        "وارفكس",     "ING007", "5 mg",   "tablet", "Delta Labs",      51.00, "available"),

    # Xarelide
    ("Xarelid",       "زاريليد",    "ING008", "20 mg",  "tablet", "Horus Pharm",     420.00, "available"),
    ("Xarelid",       "زاريليد",    "ING008", "15 mg",  "tablet", "Horus Pharm",     390.00, "available"),

    # Levothyral (NTI)
    ("Thyroxel",      "ثيروكسيل",   "ING009", "50 mcg", "tablet", "Nile Pharma",     32.00, "shortage"),
    ("Thyroxel",      "ثيروكسيل",   "ING009", "100 mcg","tablet", "Nile Pharma",     45.00, "available"),
    ("Euthyral",      "يوثيرال",    "ING009", "50 mcg", "tablet", "Delta Labs",      36.00, "available"),

    # Valproax (NTI)
    ("Depakex",       "ديباكس",     "ING010", "500 mg", "tablet, enteric coated", "Sphinx Pharma", 78.00, "shortage"),
    ("Depakex",       "ديباكس",     "ING010", "200 mg", "tablet, enteric coated", "Sphinx Pharma", 54.00, "available"),

    # Keppratex
    ("Levex",         "ليفكس",      "ING011", "500 mg", "tablet", "Delta Labs",      165.00, "available"),
    ("Levex",         "ليفكس",      "ING011", "1000 mg","tablet", "Delta Labs",      240.00, "available"),

    # Veltoprofen
    ("Veltofen",      "فيلتوفين",   "ING012", "400 mg", "tablet", "Nile Pharma",     22.00, "available"),
    ("Profex",        "بروفكس",     "ING012", "400 mg", "tablet", "Sphinx Pharma",   18.50, "available"),
    ("Profex",        "بروفكس",     "ING012", "600 mg", "tablet", "Sphinx Pharma",   26.00, "shortage"),

    # Diclofenax
    ("Diclorel",      "ديكلوريل",   "ING013", "50 mg",  "tablet, enteric coated", "Delta Labs", 20.00, "available"),
    ("Volterex",      "فولتركس",    "ING013", "50 mg",  "tablet, enteric coated", "Horus Pharm", 24.00, "available"),
    ("Volterex Gel",  "فولتركس جل", "ING013", "1%",     "gel", "Horus Pharm",        58.00, "available"),

    # Paracetamide
    ("Panadex",       "بانادكس",    "ING014", "500 mg", "tablet", "Nile Pharma",     12.00, "available"),
    ("Feverol",       "فيفرول",     "ING014", "500 mg", "tablet", "Delta Labs",      10.50, "available"),
    ("Feverol Kids",  "فيفرول كيدز","ING014", "120 mg/5 mL", "oral suspension", "Delta Labs", 26.00, "available"),

    # Amoxicillex
    ("Amoxil-N",      "أموكسيل",    "ING015", "500 mg", "capsule", "Nile Pharma",    45.00, "shortage"),
    ("Penamox",       "بيناموكس",   "ING015", "500 mg", "capsule", "Sphinx Pharma",  42.00, "available"),
    ("Penamox",       "بيناموكس",   "ING015", "250 mg/5 mL", "oral suspension", "Sphinx Pharma", 38.00, "available"),

    # Azithromycex
    ("Azitrex",       "أزيتركس",    "ING016", "500 mg", "tablet", "Horus Pharm",     95.00, "available"),
    ("Zithrolex",     "زيثرولكس",   "ING016", "250 mg", "tablet", "Delta Labs",      72.00, "available"),

    # Ciproflaxen
    ("Ciprodex-O",    "سيبرودكس",   "ING017", "500 mg", "tablet", "Nile Pharma",     58.00, "available"),
    ("Floxarel",      "فلوكساريل",  "ING017", "500 mg", "tablet", "Sphinx Pharma",   54.00, "available"),

    # Omeprazine
    ("Omezel",        "أوميزيل",    "ING018", "20 mg",  "capsule, enteric coated", "Delta Labs", 33.00, "available"),
    ("Gastrolux",     "جاسترولكس",  "ING018", "20 mg",  "capsule, enteric coated", "Nile Pharma", 29.00, "shortage"),

    # Pantoprazine
    ("Pantorex",      "بانتوركس",   "ING019", "40 mg",  "tablet, enteric coated", "Horus Pharm", 47.00, "available"),

    # Clopidogrex
    ("Clopidex",      "كلوبيدكس",   "ING020", "75 mg",  "tablet", "Sphinx Pharma",   88.00, "available"),

    # Metformax
    ("Glucoformin",   "جلوكوفورمين","ING021", "500 mg", "tablet", "Nile Pharma",     26.00, "available"),
    ("Glucoformin",   "جلوكوفورمين","ING021", "1000 mg","tablet", "Nile Pharma",     40.00, "shortage"),
    ("Metfex XR",     "ميتفكس",     "ING021", "1000 mg","tablet, extended release", "Delta Labs", 68.00, "available"),

    # Gliclazex
    ("Diaclex MR",    "دياكلكس",    "ING022", "60 mg",  "tablet, modified release", "Horus Pharm", 72.00, "available"),

    # Atorvastin
    ("Atorex",        "أتوركس",     "ING023", "20 mg",  "tablet", "Delta Labs",      64.00, "shortage"),
    ("Lipidex",       "ليبيدكس",    "ING023", "20 mg",  "tablet", "Sphinx Pharma",   59.00, "available"),
    ("Lipidex",       "ليبيدكس",    "ING023", "40 mg",  "tablet", "Sphinx Pharma",   86.00, "available"),

    # Rosuvastin
    ("Rosulex",       "روزوليكس",   "ING024", "10 mg",  "tablet", "Horus Pharm",     78.00, "available"),
    ("Rosulex",       "روزوليكس",   "ING024", "20 mg",  "tablet", "Horus Pharm",     104.00, "available"),

    # Denufolin (orphan)
    ("Denufex",       "دينوفكس",    "ING025", "100 mg/mL", "solution for injection", "Nile Pharma", 1250.00, "shortage"),

    # Verapaxil
    ("Verapex",       "فيرابكس",    "ING026", "80 mg",  "tablet", "Sphinx Pharma",   31.00, "available"),
    ("Verapex SR",    "فيرابكس",    "ING026", "240 mg", "tablet, sustained release", "Sphinx Pharma", 69.00, "available"),
]

# Common misspellings and transliteration variants, mapped to canonical brand.
# Trap: "Cardex" vs "Carvex" are one edit apart and are DIFFERENT molecules.
ALIASES = {
    "concor": "Cardex", "kardex": "Cardex", "cardix": "Cardex",
    "carvix": "Carvex", "karvex": "Carvex",
    "valtek": "Valtec", "valtak": "Valtec",
    "lisprel": "Lispril", "lispryl": "Lispril",
    "thyroxil": "Thyroxel", "throxel": "Thyroxel",
    "depakes": "Depakex", "dipakex": "Depakex",
    "profix": "Profex", "brofex": "Profex",
    "panadix": "Panadex", "bandex": "Panadex",
    "glucofformin": "Glucoformin", "glocoformin": "Glucoformin",
    "koagulex": "Coagulex", "coagulix": "Coagulex",
}
