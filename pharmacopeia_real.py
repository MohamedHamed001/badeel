"""Badeel REAL-drug pharmacopeia (demo dataset).

Real active ingredients with real, standard-reference clinical facts
(contraindications, interactions, ATC codes, narrow-therapeutic-index status),
dressed in real Egyptian-market brand names. Ingredient-level pharmacology is
universal and textbook; brand names are real Egyptian products; EGP prices are
ILLUSTRATIVE and not authoritative.

NOT FOR CLINICAL USE. Educational decision-support demo for a licensed
pharmacist. Clinical facts are simplified reference knowledge, not a validated
drug database.

Schema mirrors pharmacopeia.py exactly so the same build/pipeline code applies.
Classes mirror the synthetic set 1:1 so the same scenarios work with real drugs.
"""

INGREDIENTS = [
    # --- C07 beta blockers -------------------------------------------------
    dict(
        id="ING001", name="Bisoprolol", atc="C07AB07", nti=False,
        drug_class="Selective beta-1 adrenergic blocker",
        equiv_group="beta_blocker_selective",
        indications=["Hypertension", "Chronic stable angina", "Chronic heart failure"],
        forms=[("tablet", ["2.5 mg", "5 mg", "10 mg"])],
        contraindications=["Severe bronchial asthma", "Second or third degree AV block",
                           "Cardiogenic shock", "Decompensated heart failure"],
        interactions=[("Verapamil", "major", "Additive AV nodal suppression, risk of bradyarrhythmia"),
                      ("Gliclazide", "moderate", "Masks adrenergic warning signs of hypoglycaemia")],
        pregnancy="Category C. Use only if benefit outweighs foetal risk.",
        renal="No dose adjustment for eGFR above 20 mL/min.",
        hepatic="Reduce dose in severe impairment.",
        adverse=["Bradycardia", "Fatigue", "Cold extremities"],
        notes="Beta-1 selective, but selectivity is relative and it is still "
              "contraindicated in severe asthma.",
    ),
    dict(
        id="ING002", name="Metoprolol", atc="C07AB02", nti=False,
        drug_class="Selective beta-1 adrenergic blocker",
        equiv_group="beta_blocker_selective",
        indications=["Hypertension", "Angina", "Migraine prophylaxis"],
        forms=[("tablet", ["50 mg", "100 mg"])],
        contraindications=["Severe bronchial asthma", "Second or third degree AV block",
                           "Decompensated heart failure"],
        interactions=[("Verapamil", "major", "Additive AV nodal suppression"),
                      ("Ibuprofen", "moderate", "NSAIDs may blunt antihypertensive effect")],
        pregnancy="Category C.",
        renal="No adjustment required.",
        hepatic="Extensively metabolised; halve dose in cirrhosis.",
        adverse=["Bradycardia", "Dizziness", "Bronchospasm in susceptible patients"],
        notes="Immediate release tablets differ from extended release; do not "
              "swap milligram for milligram without prescriber review.",
    ),
    dict(
        id="ING003", name="Carvedilol", atc="C07AG02", nti=False,
        drug_class="Non-selective beta blocker with alpha-1 blockade",
        equiv_group="beta_blocker_nonselective",
        indications=["Chronic heart failure", "Hypertension"],
        forms=[("tablet", ["6.25 mg", "12.5 mg", "25 mg"])],
        contraindications=["Bronchial asthma of any severity", "Decompensated heart failure",
                           "Severe hepatic impairment", "Second or third degree AV block"],
        interactions=[("Gliclazide", "moderate", "Enhanced hypoglycaemic effect"),
                      ("Verapamil", "major", "Severe bradycardia and hypotension")],
        pregnancy="Category C.",
        renal="No adjustment required.",
        hepatic="Contraindicated in severe impairment.",
        adverse=["Postural hypotension", "Fatigue"],
        notes="Non-selective; carries a stronger bronchospasm warning than the "
              "beta-1 selective agents and is not appropriate in reactive airway disease.",
    ),

    # --- C09 renin angiotensin --------------------------------------------
    dict(
        id="ING004", name="Lisinopril", atc="C09AA03", nti=False,
        drug_class="Angiotensin converting enzyme inhibitor",
        equiv_group="raas_blocker",
        indications=["Hypertension", "Heart failure", "Diabetic nephropathy"],
        forms=[("tablet", ["5 mg", "10 mg", "20 mg"])],
        contraindications=["Pregnancy", "History of angioedema", "Bilateral renal artery stenosis"],
        interactions=[("Ibuprofen", "major", "Increased risk of acute kidney injury"),
                      ("Valsartan", "major", "Dual RAAS blockade, hyperkalaemia and renal failure")],
        pregnancy="Contraindicated in all trimesters. Discontinue immediately if pregnancy detected.",
        renal="Reduce dose if eGFR below 30 mL/min. Monitor potassium.",
        hepatic="No adjustment required.",
        adverse=["Dry persistent cough", "Hyperkalaemia", "First dose hypotension"],
        notes="Dry cough is the commonest reason for switching within this group.",
    ),
    dict(
        id="ING005", name="Valsartan", atc="C09CA03", nti=False,
        drug_class="Angiotensin II receptor blocker",
        equiv_group="raas_blocker",
        indications=["Hypertension", "Heart failure", "Post myocardial infarction"],
        forms=[("tablet", ["40 mg", "80 mg", "160 mg"])],
        contraindications=["Pregnancy", "Bilateral renal artery stenosis", "Severe hepatic impairment"],
        interactions=[("Lisinopril", "major", "Dual RAAS blockade"),
                      ("Ibuprofen", "major", "Increased risk of acute kidney injury")],
        pregnancy="Contraindicated in all trimesters.",
        renal="Monitor potassium and creatinine.",
        hepatic="Contraindicated in severe impairment.",
        adverse=["Dizziness", "Hyperkalaemia"],
        notes="Does not cause the dry cough associated with ACE inhibitors, the "
              "usual switch target from lisinopril.",
    ),
    dict(
        id="ING006", name="Valsartan + Hydrochlorothiazide", atc="C09DA03", nti=False,
        drug_class="Angiotensin II receptor blocker with thiazide diuretic",
        equiv_group="raas_blocker_combination",
        is_combination=True,
        components=["Valsartan", "Hydrochlorothiazide"],
        indications=["Hypertension not controlled on monotherapy"],
        forms=[("tablet", ["80 mg / 12.5 mg", "160 mg / 12.5 mg", "160 mg / 25 mg"])],
        contraindications=["Pregnancy", "Anuria", "Severe hepatic impairment", "Sulfonamide hypersensitivity"],
        interactions=[("Ibuprofen", "major", "Reduced diuretic efficacy and renal risk")],
        pregnancy="Contraindicated in all trimesters.",
        renal="Avoid if eGFR below 30 mL/min due to the thiazide component.",
        hepatic="Contraindicated in severe impairment.",
        adverse=["Hypokalaemia", "Hyponatraemia", "Dizziness"],
        notes="A fixed dose combination; substituting a single-ingredient product "
              "leaves the second indication untreated.",
    ),

    # --- C08 calcium channel blocker --------------------------------------
    dict(
        id="ING007", name="Verapamil", atc="C08DA01", nti=False,
        drug_class="Non-dihydropyridine calcium channel blocker",
        equiv_group="ccb_nondhp",
        indications=["Hypertension", "Angina", "Supraventricular arrhythmia"],
        forms=[("tablet", ["40 mg", "80 mg"]),
               ("tablet, sustained release", ["240 mg"])],
        contraindications=["Severe left ventricular dysfunction", "Second or third degree AV block",
                           "Concomitant beta blockade"],
        interactions=[("Bisoprolol", "major", "Additive AV nodal suppression"),
                      ("Metoprolol", "major", "Additive AV nodal suppression")],
        pregnancy="Category C.",
        renal="No adjustment required.",
        hepatic="Reduce dose in impairment.",
        adverse=["Constipation", "Bradycardia", "Ankle oedema"],
        notes="Sustained release and immediate release are not interchangeable "
              "milligram for milligram.",
    ),

    # --- C10 statins -------------------------------------------------------
    dict(
        id="ING008", name="Atorvastatin", atc="C10AA05", nti=False,
        drug_class="HMG-CoA reductase inhibitor",
        equiv_group="statin",
        indications=["Hypercholesterolaemia", "Cardiovascular risk reduction"],
        forms=[("tablet", ["10 mg", "20 mg", "40 mg", "80 mg"])],
        contraindications=["Active liver disease", "Pregnancy", "Breastfeeding"],
        interactions=[("Azithromycin", "moderate", "Increased myopathy risk"),
                      ("Verapamil", "moderate", "Raised statin levels, myopathy risk")],
        pregnancy="Contraindicated.",
        renal="No adjustment required.",
        hepatic="Contraindicated in active liver disease.",
        adverse=["Myalgia", "Deranged liver enzymes"],
        notes="Potency differs across statins; a milligram for milligram swap to "
              "another statin is not equivalent.",
    ),
    dict(
        id="ING009", name="Rosuvastatin", atc="C10AA07", nti=False,
        drug_class="HMG-CoA reductase inhibitor",
        equiv_group="statin",
        indications=["Hypercholesterolaemia", "Cardiovascular risk reduction"],
        forms=[("tablet", ["5 mg", "10 mg", "20 mg"])],
        contraindications=["Active liver disease", "Pregnancy", "Severe renal impairment"],
        interactions=[("Warfarin", "moderate", "INR elevation reported")],
        pregnancy="Contraindicated.",
        renal="Avoid 40 mg dose in moderate impairment.",
        hepatic="Contraindicated in active liver disease.",
        adverse=["Myalgia", "Proteinuria at high dose"],
        notes="More potent per milligram than atorvastatin; requires dose "
              "conversion, not a milligram for milligram swap.",
    ),

    # --- B01 antithrombotics ----------------------------------------------
    dict(
        id="ING010", name="Warfarin", atc="B01AA03", nti=True,
        drug_class="Vitamin K antagonist anticoagulant",
        equiv_group="anticoagulant",
        indications=["Atrial fibrillation", "Venous thromboembolism", "Mechanical heart valve"],
        forms=[("tablet", ["1 mg", "3 mg", "5 mg"])],
        contraindications=["Active bleeding", "Pregnancy", "Severe uncontrolled hypertension"],
        interactions=[("Ibuprofen", "major", "Markedly increased bleeding risk"),
                      ("Diclofenac", "major", "Increased bleeding risk"),
                      ("Azithromycin", "major", "Potentiates anticoagulant effect, INR rise"),
                      ("Amoxicillin", "moderate", "Possible INR elevation"),
                      ("Sodium Valproate", "major", "Displacement from protein binding, bleeding risk"),
                      ("Paracetamol", "moderate", "Prolonged regular use may raise INR")],
        pregnancy="Contraindicated; teratogenic.",
        renal="Monitor INR closely.",
        hepatic="Enhanced effect; monitor INR.",
        adverse=["Bleeding", "Bruising"],
        notes="Narrow therapeutic index. Any change, including brand to brand, "
              "requires prescriber authorisation and INR monitoring.",
    ),
    dict(
        id="ING011", name="Rivaroxaban", atc="B01AF01", nti=False,
        drug_class="Direct factor Xa inhibitor",
        equiv_group="doac",
        indications=["Atrial fibrillation", "Venous thromboembolism"],
        forms=[("tablet", ["10 mg", "15 mg", "20 mg"])],
        contraindications=["Active bleeding", "Severe renal impairment", "Pregnancy"],
        interactions=[("Ibuprofen", "major", "Increased bleeding risk"),
                      ("Ciprofloxacin", "moderate", "Raised plasma concentration")],
        pregnancy="Contraindicated.",
        renal="Avoid if creatinine clearance below 15 mL/min.",
        hepatic="Contraindicated in coagulopathy-associated hepatic disease.",
        adverse=["Bleeding"],
        notes="A direct oral anticoagulant is not interchangeable with a vitamin "
              "K antagonist without prescriber review.",
    ),
    dict(
        id="ING012", name="Clopidogrel", atc="B01AC04", nti=False,
        drug_class="P2Y12 antiplatelet",
        equiv_group="antiplatelet",
        indications=["Acute coronary syndrome", "Post stent", "Secondary stroke prevention"],
        forms=[("tablet", ["75 mg"])],
        contraindications=["Active bleeding", "Severe hepatic impairment"],
        interactions=[("Omeprazole", "major", "Reduced antiplatelet activation"),
                      ("Ibuprofen", "major", "Increased bleeding risk")],
        pregnancy="Use only if clearly needed.",
        renal="No adjustment required.",
        hepatic="Caution in impairment.",
        adverse=["Bleeding", "Bruising"],
        notes="An antiplatelet is not interchangeable with an anticoagulant; they "
              "treat different indications.",
    ),

    # --- A10 oral antidiabetics -------------------------------------------
    dict(
        id="ING013", name="Metformin", atc="A10BA02", nti=False,
        drug_class="Biguanide antidiabetic",
        equiv_group="antidiabetic_oral",
        indications=["Type 2 diabetes mellitus"],
        forms=[("tablet", ["500 mg", "850 mg", "1000 mg"]),
               ("tablet, extended release", ["1000 mg"])],
        contraindications=["eGFR below 30 mL/min", "Acute metabolic acidosis",
                           "Acute decompensated heart failure"],
        interactions=[("Ciprofloxacin", "minor", "Possible glycaemic fluctuation")],
        pregnancy="Compatible in pregnancy under supervision.",
        renal="Contraindicated below eGFR 30; review dose below eGFR 45.",
        hepatic="Avoid in significant impairment.",
        adverse=["Gastrointestinal upset", "Lactic acidosis (rare)"],
        notes="Extended release improves gastrointestinal tolerance but changes "
              "dosing frequency; not milligram equivalent in schedule.",
    ),
    dict(
        id="ING014", name="Gliclazide", atc="A10BB09", nti=False,
        drug_class="Sulfonylurea antidiabetic",
        equiv_group="antidiabetic_oral",
        indications=["Type 2 diabetes mellitus"],
        forms=[("tablet", ["80 mg"]),
               ("tablet, modified release", ["30 mg", "60 mg"])],
        contraindications=["Type 1 diabetes", "Severe renal impairment", "Sulfonamide hypersensitivity"],
        interactions=[("Bisoprolol", "moderate", "Beta blockers mask hypoglycaemia warning signs")],
        pregnancy="Switch to insulin in pregnancy.",
        renal="Contraindicated in severe impairment; hypoglycaemia risk.",
        hepatic="Caution; hypoglycaemia risk.",
        adverse=["Hypoglycaemia", "Weight gain"],
        notes="Carries hypoglycaemia risk in renal impairment, unlike metformin.",
    ),

    # --- H03 thyroid -------------------------------------------------------
    dict(
        id="ING015", name="Levothyroxine", atc="H03AA01", nti=True,
        drug_class="Thyroid hormone",
        equiv_group="thyroid_hormone",
        indications=["Hypothyroidism"],
        forms=[("tablet", ["25 mcg", "50 mcg", "100 mcg"])],
        contraindications=["Untreated thyrotoxicosis", "Acute myocardial infarction"],
        interactions=[("Omeprazole", "moderate", "Reduced absorption"),
                      ("Pantoprazole", "moderate", "Reduced absorption"),
                      ("Metformin", "minor", "Altered glycaemic control")],
        pregnancy="Continue and monitor; requirements rise.",
        renal="No adjustment required.",
        hepatic="No adjustment required.",
        adverse=["Palpitations if over-replaced"],
        notes="Narrow therapeutic index. Do not split tablets to reach a dose; "
              "retest thyroid function after any change. Prescriber review required.",
    ),

    # --- N03 antiepileptics -----------------------------------------------
    dict(
        id="ING016", name="Sodium Valproate", atc="N03AG01", nti=True,
        drug_class="Broad spectrum antiepileptic",
        equiv_group="antiepileptic",
        indications=["Generalised and focal epilepsy", "Bipolar disorder"],
        forms=[("tablet", ["200 mg", "500 mg"])],
        contraindications=["Pregnancy", "Hepatic impairment", "Urea cycle disorders"],
        interactions=[("Warfarin", "major", "Displacement from protein binding, bleeding risk")],
        pregnancy="Contraindicated; highly teratogenic.",
        renal="No adjustment required.",
        hepatic="Contraindicated in hepatic impairment.",
        adverse=["Tremor", "Weight gain", "Hepatotoxicity"],
        notes="Narrow therapeutic index antiepileptic. An unmonitored switch "
              "risks breakthrough seizure or toxicity. Prescriber review required.",
    ),
    dict(
        id="ING017", name="Levetiracetam", atc="N03AX14", nti=False,
        drug_class="SV2A antiepileptic",
        equiv_group="antiepileptic",
        indications=["Focal and generalised epilepsy"],
        forms=[("tablet", ["250 mg", "500 mg", "1000 mg"])],
        contraindications=["Hypersensitivity to the drug"],
        interactions=[],
        pregnancy="Preferred antiepileptic in pregnancy where suitable.",
        renal="Reduce dose in renal impairment.",
        hepatic="Caution in severe impairment.",
        adverse=["Somnolence", "Irritability"],
        notes="Different mechanism from valproate; not an automatic substitute "
              "for seizure control without prescriber review.",
    ),

    # --- M01 NSAIDs --------------------------------------------------------
    dict(
        id="ING018", name="Diclofenac", atc="M01AB05", nti=False,
        drug_class="Non-steroidal anti-inflammatory drug",
        equiv_group="nsaid",
        indications=["Pain", "Inflammation", "Musculoskeletal disorders"],
        forms=[("tablet", ["50 mg"]),
               ("gel", ["1%"])],
        contraindications=["Active peptic ulcer", "Established ischaemic heart disease",
                           "Severe renal impairment", "Third trimester pregnancy"],
        interactions=[("Warfarin", "major", "Increased bleeding risk"),
                      ("Lisinopril", "major", "Acute kidney injury risk")],
        pregnancy="Avoid, especially third trimester.",
        renal="Avoid in significant impairment.",
        hepatic="Caution.",
        adverse=["Dyspepsia", "Gastrointestinal bleeding", "Raised blood pressure"],
        notes="Carries a higher cardiovascular risk than some other NSAIDs; avoid "
              "in established ischaemic heart disease.",
    ),
    dict(
        id="ING019", name="Ibuprofen", atc="M01AE01", nti=False,
        drug_class="Non-steroidal anti-inflammatory drug",
        equiv_group="nsaid",
        indications=["Pain", "Fever", "Inflammation"],
        forms=[("tablet", ["400 mg", "600 mg"])],
        contraindications=["Active peptic ulcer", "Severe renal impairment",
                           "Third trimester pregnancy", "History of NSAID induced asthma"],
        interactions=[("Warfarin", "major", "Markedly increased bleeding risk"),
                      ("Lisinopril", "major", "Acute kidney injury risk"),
                      ("Clopidogrel", "major", "Increased bleeding risk")],
        pregnancy="Avoid, especially third trimester.",
        renal="Avoid in significant impairment.",
        hepatic="Caution.",
        adverse=["Dyspepsia", "Gastrointestinal bleeding"],
        notes="Lower cardiovascular risk than diclofenac at usual doses; still an "
              "NSAID with bleeding and renal cautions.",
    ),

    # --- N02 analgesic (non-NSAID) ----------------------------------------
    dict(
        id="ING020", name="Paracetamol", atc="N02BE01", nti=False,
        drug_class="Non-opioid analgesic and antipyretic",
        equiv_group="simple_analgesic",
        indications=["Pain", "Fever"],
        forms=[("tablet", ["500 mg"]),
               ("oral suspension", ["120 mg/5 mL"])],
        contraindications=["Severe hepatic impairment"],
        interactions=[("Warfarin", "moderate", "Prolonged regular use may raise INR")],
        pregnancy="Analgesic of choice in pregnancy.",
        renal="No adjustment at usual doses.",
        hepatic="Reduce dose; avoid in severe impairment.",
        adverse=["Hepatotoxicity in overdose"],
        notes="Not anti-inflammatory; a different pharmacological action from an "
              "NSAID and not an equivalent substitute for inflammatory pain.",
    ),

    # --- A02 proton pump inhibitors ---------------------------------------
    dict(
        id="ING021", name="Omeprazole", atc="A02BC01", nti=False,
        drug_class="Proton pump inhibitor",
        equiv_group="ppi",
        indications=["Gastro-oesophageal reflux", "Peptic ulcer", "NSAID gastroprotection"],
        forms=[("capsule, enteric coated", ["20 mg", "40 mg"])],
        contraindications=["Hypersensitivity to proton pump inhibitors"],
        interactions=[("Clopidogrel", "major", "Reduced antiplatelet activation"),
                      ("Levothyroxine", "moderate", "Reduced thyroid hormone absorption")],
        pregnancy="Considered safe where needed.",
        renal="No adjustment required.",
        hepatic="Reduce dose in severe impairment.",
        adverse=["Headache", "Diarrhoea"],
        notes="Inhibits activation of clopidogrel; pantoprazole is preferred when "
              "a patient is on clopidogrel.",
    ),
    dict(
        id="ING022", name="Pantoprazole", atc="A02BC02", nti=False,
        drug_class="Proton pump inhibitor",
        equiv_group="ppi",
        indications=["Gastro-oesophageal reflux", "Peptic ulcer"],
        forms=[("tablet, enteric coated", ["20 mg", "40 mg"])],
        contraindications=["Hypersensitivity to proton pump inhibitors"],
        interactions=[("Levothyroxine", "moderate", "Reduced thyroid hormone absorption")],
        pregnancy="Considered safe where needed.",
        renal="No adjustment required.",
        hepatic="Reduce dose in severe impairment.",
        adverse=["Headache", "Diarrhoea"],
        notes="Least likely proton pump inhibitor to affect clopidogrel activation.",
    ),

    # --- J01 antibiotics ---------------------------------------------------
    dict(
        id="ING023", name="Amoxicillin", atc="J01CA04", nti=False,
        drug_class="Aminopenicillin antibiotic",
        equiv_group="penicillin",
        indications=["Respiratory tract infection", "Otitis media", "Urinary tract infection"],
        forms=[("capsule", ["500 mg"]),
               ("oral suspension", ["250 mg/5 mL"])],
        contraindications=["Penicillin hypersensitivity"],
        interactions=[("Warfarin", "moderate", "Possible INR elevation")],
        pregnancy="Considered safe.",
        renal="Reduce dose in severe impairment.",
        hepatic="Caution.",
        adverse=["Rash", "Diarrhoea"],
        notes="Contraindicated in penicillin allergy; a macrolide is the usual "
              "alternative class.",
    ),
    dict(
        id="ING024", name="Azithromycin", atc="J01FA10", nti=False,
        drug_class="Macrolide antibiotic",
        equiv_group="macrolide",
        indications=["Respiratory tract infection", "Atypical infection"],
        forms=[("tablet", ["250 mg", "500 mg"]),
               ("oral suspension", ["200 mg/5 mL"])],
        contraindications=["Cholestatic jaundice with prior macrolide use"],
        interactions=[("Warfarin", "major", "Potentiates anticoagulation"),
                      ("Ciprofloxacin", "major", "Additive QT prolongation")],
        pregnancy="Considered safe where indicated.",
        renal="No adjustment required.",
        hepatic="Caution.",
        adverse=["Diarrhoea", "QT prolongation"],
        notes="Common alternative to a penicillin in allergic patients.",
    ),
    dict(
        id="ING025", name="Ciprofloxacin", atc="J01MA02", nti=False,
        drug_class="Fluoroquinolone antibiotic",
        equiv_group="fluoroquinolone",
        indications=["Urinary tract infection", "Gastrointestinal infection"],
        forms=[("tablet", ["250 mg", "500 mg"])],
        contraindications=["Age under 18 years except specified indications",
                           "History of tendon disorder with quinolones", "Myasthenia gravis"],
        interactions=[("Azithromycin", "major", "Additive QT prolongation"),
                      ("Rivaroxaban", "moderate", "Raised plasma concentration"),
                      ("Metformin", "minor", "Possible glycaemic fluctuation")],
        pregnancy="Avoid.",
        renal="Reduce dose in impairment.",
        hepatic="Caution.",
        adverse=["Tendinopathy", "QT prolongation"],
        notes="Restricted under 18 years; a paediatric prescription needs "
              "prescriber review.",
    ),

    # --- M04 unique drug, no in-set substitute ----------------------------
    dict(
        id="ING026", name="Allopurinol", atc="M04AA01", nti=False,
        drug_class="Xanthine oxidase inhibitor",
        equiv_group="urate_lowering",
        indications=["Chronic gout", "Hyperuricaemia"],
        forms=[("tablet", ["100 mg", "300 mg"])],
        contraindications=["Acute gout attack", "Severe hypersensitivity reaction history"],
        interactions=[("Warfarin", "moderate", "May potentiate anticoagulant effect")],
        pregnancy="Use only if clearly needed.",
        renal="Reduce dose in impairment.",
        hepatic="Caution.",
        adverse=["Rash", "Severe hypersensitivity syndrome (rare)"],
        notes="No equivalent urate-lowering alternative is stocked in this "
              "registry; refer to the prescriber if unavailable.",
    ),
]


# ---------------------------------------------------------------------------
# BRANDS: (brand, brand_ar, ingredient_id, strength, form, manufacturer, price_egp, status)
# Real Egyptian-market brand names. EGP prices are ILLUSTRATIVE.
# ---------------------------------------------------------------------------

BRANDS = [
    # Bisoprolol
    ("Concor", "كونكور", "ING001", "5 mg", "tablet", "Amoun", 78.0, "available"),
    ("Concor", "كونكور", "ING001", "10 mg", "tablet", "Amoun", 112.0, "shortage"),
    ("Concor", "كونكور", "ING001", "2.5 mg", "tablet", "Amoun", 55.0, "available"),
    ("Bisocard", "بيسوكارد", "ING001", "5 mg", "tablet", "Global Napi", 60.0, "available"),
    ("Bisocard", "بيسوكارد", "ING001", "10 mg", "tablet", "Global Napi", 92.0, "available"),
    # Metoprolol
    ("Betaloc", "بيتالوك", "ING002", "50 mg", "tablet", "AstraZeneca", 65.0, "available"),
    ("Betaloc", "بيتالوك", "ING002", "100 mg", "tablet", "AstraZeneca", 98.0, "available"),
    # Carvedilol
    ("Dilatrend", "ديلاتريند", "ING003", "6.25 mg", "tablet", "Roche", 70.0, "available"),
    ("Dilatrend", "ديلاتريند", "ING003", "25 mg", "tablet", "Roche", 120.0, "available"),
    ("Carvid", "كارفيد", "ING003", "12.5 mg", "tablet", "Hikma", 58.0, "available"),
    # Lisinopril
    ("Zestril", "زيستريل", "ING004", "20 mg", "tablet", "AstraZeneca", 85.0, "shortage"),
    ("Sinopril", "سينوبريل", "ING004", "10 mg", "tablet", "EIPICO", 48.0, "available"),
    ("Sinopril", "سينوبريل", "ING004", "20 mg", "tablet", "EIPICO", 66.0, "available"),
    # Valsartan
    ("Tareg", "تاريج", "ING005", "80 mg", "tablet", "Novartis", 96.0, "available"),
    ("Tareg", "تاريج", "ING005", "160 mg", "tablet", "Novartis", 140.0, "available"),
    ("Diovan", "ديوفان", "ING005", "160 mg", "tablet", "Novartis", 155.0, "shortage"),
    # Valsartan + HCTZ (combination)
    ("Co-Diovan", "كو-ديوفان", "ING006", "160 mg / 12.5 mg", "tablet", "Novartis", 168.0, "available"),
    ("Co-Tareg", "كو-تاريج", "ING006", "80 mg / 12.5 mg", "tablet", "Novartis", 130.0, "available"),
    # Verapamil
    ("Isoptin", "إيزوبتين", "ING007", "80 mg", "tablet", "Abbott", 42.0, "available"),
    ("Isoptin SR", "إيزوبتين إس آر", "ING007", "240 mg", "tablet, sustained release", "Abbott", 88.0, "available"),
    # Atorvastatin
    ("Lipitor", "ليبيتور", "ING008", "20 mg", "tablet", "Pfizer", 130.0, "shortage"),
    ("Ator", "أتور", "ING008", "20 mg", "tablet", "EVA Pharma", 72.0, "available"),
    ("Ator", "أتور", "ING008", "40 mg", "tablet", "EVA Pharma", 105.0, "available"),
    # Rosuvastatin
    ("Crestor", "كريستور", "ING009", "10 mg", "tablet", "AstraZeneca", 165.0, "available"),
    ("Rosuvast", "روزوفاست", "ING009", "20 mg", "tablet", "Marcyrl", 98.0, "available"),
    # Warfarin (NTI)
    ("Marevan", "ماريفان", "ING010", "5 mg", "tablet", "Amoun", 45.0, "shortage"),
    ("Marevan", "ماريفان", "ING010", "3 mg", "tablet", "Amoun", 38.0, "available"),
    # Rivaroxaban
    ("Xarelto", "زاريلتو", "ING011", "20 mg", "tablet", "Bayer", 620.0, "available"),
    # Clopidogrel
    ("Plavix", "بلافيكس", "ING012", "75 mg", "tablet", "Sanofi", 190.0, "shortage"),
    ("Clopivas", "كلوبيفاس", "ING012", "75 mg", "tablet", "Marcyrl", 85.0, "available"),
    # Metformin
    ("Glucophage", "جلوكوفاج", "ING013", "1000 mg", "tablet", "Merck", 68.0, "available"),
    ("Glucophage XR", "جلوكوفاج إكس آر", "ING013", "1000 mg", "tablet, extended release", "Merck", 92.0, "shortage"),
    ("Cidophage", "سيدوفاج", "ING013", "500 mg", "tablet", "CID", 30.0, "available"),
    ("Cidophage", "سيدوفاج", "ING013", "850 mg", "tablet", "CID", 42.0, "available"),
    # Gliclazide
    ("Diamicron", "دياميكرون", "ING014", "60 mg", "tablet, modified release", "Servier", 96.0, "available"),
    ("Diamicron", "دياميكرون", "ING014", "80 mg", "tablet", "Servier", 72.0, "available"),
    # Levothyroxine (NTI)
    ("Eltroxin", "إلتروكسين", "ING015", "50 mcg", "tablet", "Aspen", 58.0, "shortage"),
    ("Eltroxin", "إلتروكسين", "ING015", "100 mcg", "tablet", "Aspen", 88.0, "available"),
    # Sodium Valproate (NTI)
    ("Depakine", "ديباكين", "ING016", "500 mg", "tablet", "Sanofi", 76.0, "shortage"),
    ("Depakine", "ديباكين", "ING016", "200 mg", "tablet", "Sanofi", 52.0, "available"),
    # Levetiracetam
    ("Keppra", "كيبرا", "ING017", "500 mg", "tablet", "UCB", 210.0, "available"),
    ("Tiratam", "تيراتام", "ING017", "500 mg", "tablet", "Hikma", 120.0, "available"),
    # Diclofenac
    ("Cataflam", "كاتافلام", "ING018", "50 mg", "tablet", "Novartis", 40.0, "available"),
    ("Voltaren", "فولتارين", "ING018", "50 mg", "tablet", "Novartis", 45.0, "shortage"),
    ("Olfen Gel", "أولفين جيل", "ING018", "1%", "gel", "Mepha", 55.0, "available"),
    # Ibuprofen
    ("Brufen", "بروفين", "ING019", "400 mg", "tablet", "Abbott", 35.0, "available"),
    ("Brufen", "بروفين", "ING019", "600 mg", "tablet", "Abbott", 48.0, "shortage"),
    # Paracetamol
    ("Panadol", "بانادول", "ING020", "500 mg", "tablet", "GSK", 30.0, "available"),
    ("Cetal", "سيتال", "ING020", "500 mg", "tablet", "EPICO", 15.0, "available"),
    ("Cetal", "سيتال", "ING020", "120 mg/5 mL", "oral suspension", "EPICO", 22.0, "available"),
    # Omeprazole
    ("Risek", "ريزك", "ING021", "20 mg", "capsule, enteric coated", "Julphar", 60.0, "shortage"),
    ("Gastrazole", "جاسترازول", "ING021", "20 mg", "capsule, enteric coated", "EIPICO", 34.0, "available"),
    ("Omez", "أوميز", "ING021", "20 mg", "capsule, enteric coated", "Dr Reddy", 40.0, "available"),
    # Pantoprazole
    ("Controloc", "كنترولوك", "ING022", "40 mg", "tablet, enteric coated", "Takeda", 95.0, "available"),
    # Amoxicillin
    ("Amoxil", "أموكسيل", "ING023", "500 mg", "capsule", "GSK", 44.0, "shortage"),
    ("E-Mox", "إي-موكس", "ING023", "500 mg", "capsule", "EIPICO", 26.0, "available"),
    ("E-Mox", "إي-موكس", "ING023", "250 mg/5 mL", "oral suspension", "EIPICO", 20.0, "available"),
    # Azithromycin
    ("Zithromax", "زيثروماكس", "ING024", "500 mg", "tablet", "Pfizer", 130.0, "available"),
    ("Zisrocin", "زيسروسين", "ING024", "500 mg", "tablet", "Amoun", 68.0, "available"),
    # Ciprofloxacin
    ("Ciprocin", "سيبروسين", "ING025", "500 mg", "tablet", "EIPICO", 38.0, "shortage"),
    ("Ciprobay", "سيبروباي", "ING025", "500 mg", "tablet", "Bayer", 95.0, "available"),
    # Allopurinol
    ("Zyloric", "زيلوريك", "ING026", "300 mg", "tablet", "Aspen", 72.0, "shortage"),
    ("Ximara", "زيمارا", "ING026", "100 mg", "tablet", "Hikma", 40.0, "available"),
]


# ---------------------------------------------------------------------------
# ALIASES: misspellings and transliteration variants -> canonical brand
# ---------------------------------------------------------------------------

ALIASES = {
    "concore": "Concor",
    "koncor": "Concor",
    "bisocor": "Concor",
    "conkor": "Concor",
    "betalok": "Betaloc",
    "dilatrind": "Dilatrend",
    "zestrel": "Zestril",
    "sinopryl": "Sinopril",
    "tarej": "Tareg",
    "diovane": "Diovan",
    "isuptin": "Isoptin",
    "lipitour": "Lipitor",
    "atoor": "Ator",
    "crestore": "Crestor",
    "marivan": "Marevan",
    "marevane": "Marevan",
    "xarelt": "Xarelto",
    "plavex": "Plavix",
    "plaviks": "Plavix",
    "glucophag": "Glucophage",
    "glukophage": "Glucophage",
    "cidophag": "Cidophage",
    "diamicrone": "Diamicron",
    "eltroxine": "Eltroxin",
    "eltroksin": "Eltroxin",
    "depakin": "Depakine",
    "kepra": "Keppra",
    "cataflame": "Cataflam",
    "voltarin": "Voltaren",
    "brufin": "Brufen",
    "panadole": "Panadol",
    "cetall": "Cetal",
    "risec": "Risek",
    "controlok": "Controloc",
    "amoxyl": "Amoxil",
    "emox": "E-Mox",
    "zithromaks": "Zithromax",
    "ciprocine": "Ciprocin",
    "zylorик": "Zyloric",
    "ziloric": "Zyloric",
}
