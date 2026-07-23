"""Backend message catalogue for English/Arabic clinical text.

Only display strings are localised. The evaluation runs in English (the default),
so translations never affect the graded pipeline. Data-derived fragments
(interaction effect text, leaflet phrases) may remain English within an Arabic
sentence — that is an accepted limitation of the demo.
"""

from __future__ import annotations

Lang = str  # "en" | "ar"

# Patient-flag vocabulary, for embedding inside localised sentences.
FLAG_AR = {
    "bronchial asthma": "الربو الشعبي",
    "penicillin allergy": "حساسية البنسلين",
    "pregnancy": "الحمل",
    "severe renal impairment": "القصور الكلوي الشديد",
    "ischaemic heart disease": "مرض القلب الإقفاري",
    "paediatric": "الأطفال",
    "paediatric, age 10": "طفل عمره 10 سنوات",
}

MESSAGES: dict[str, dict[str, str]] = {
    # --- escalation reasons -------------------------------------------------
    "esc.unresolved": {
        "en": "Product not found in registry. We cannot advise a substitution "
              "for an unrecognised product; confirm the name with the prescriber "
              "before dispensing any alternative.",
        "ar": "المنتج غير موجود في السجل. لا يمكننا اقتراح بديل لمنتج غير معروف؛ "
              "تأكد من الاسم مع الطبيب المعالج قبل صرف أي بديل.",
    },
    "esc.nti": {
        "en": "Narrow therapeutic index drug. Do not substitute without "
              "prescriber authorisation and appropriate monitoring (for example "
              "INR). Refer to prescriber.",
        "ar": "دواء ذو مؤشر علاجي ضيق. لا تصرف بديلاً دون إذن الطبيب المعالج "
              "والمتابعة المناسبة (مثل قياس INR). يُحال إلى الطبيب المعالج.",
    },
    "esc.nti_split": {
        "en": " Do not split or halve tablets to reach the dose.",
        "ar": " لا تقسّم أو تنصّف الأقراص للوصول إلى الجرعة.",
    },
    "esc.upstream": {
        "en": "The prescribed product is itself contraindicated for this patient "
              "and no safe alternative is available. The prescription needs "
              "review — escalate and refer to the prescriber.",
        "ar": "الدواء الموصوف نفسه ممنوع لهذا المريض ولا يتوفر بديل آمن. تحتاج "
              "الوصفة إلى مراجعة — يُحال الأمر إلى الطبيب المعالج.",
    },
    "esc.all_blocked": {
        "en": "Every available alternative was blocked on safety grounds; there "
              "is no therapeutic alternative that is safe here. Do not "
              "substitute — escalate and refer to the prescriber.",
        "ar": "جميع البدائل المتاحة مُنعت لأسباب تتعلق بالسلامة؛ لا يوجد بديل "
              "علاجي آمن هنا. لا تصرف بديلاً — يُحال الأمر إلى الطبيب المعالج.",
    },
    "esc.none": {
        "en": "No substitution is possible: there is no alternative in registry "
              "for this product, and no therapeutic alternative either. Escalate "
              "and refer to the prescriber.",
        "ar": "لا يمكن الاستبدال: لا يوجد بديل في السجل لهذا المنتج، ولا بديل "
              "علاجي. يُحال الأمر إلى الطبيب المعالج.",
    },
    "esc.guard_fail": {
        "en": "model could not produce a grounded suggestion",
        "ar": "تعذّر على النموذج إنتاج اقتراح موثّق",
    },
    # --- safety flags -------------------------------------------------------
    "flag.nti": {
        "en": "Narrow therapeutic index: substitution, including brand-to-brand, "
              "requires prescriber sign-off.",
        "ar": "مؤشر علاجي ضيق: الاستبدال، بما في ذلك بين العلامات التجارية، يتطلب "
              "موافقة الطبيب المعالج.",
    },
    "flag.contra": {
        "en": "Contraindicated in {flag}.",
        "ar": "ممنوع الاستعمال في {flag}.",
    },
    "flag.contra_pregnancy": {
        "en": "Contraindicated in pregnancy; discontinue immediately — this is an "
              "urgent teratogenic risk.",
        "ar": "ممنوع في الحمل؛ أوقف الدواء فوراً — خطر تشوّهات جنينية عاجل.",
    },
    "flag.contra_renal": {
        "en": "Contraindicated in severe renal impairment; contraindicated below "
              "eGFR 30 mL/min.",
        "ar": "ممنوع في القصور الكلوي الشديد؛ ممنوع عند معدل ترشيح كلوي أقل من "
              "30 مل/دقيقة.",
    },
    "flag.interaction": {
        "en": "Interaction with {med}: {effect}.",
        "ar": "تفاعل دوائي مع {med}: {effect}.",
    },
    "flag.combination": {
        "en": "This is a fixed dose combination; a valid substitute must contain "
              "both components. Adding or dropping an active ingredient is not an "
              "equivalent substitution — refer to the prescriber.",
        "ar": "هذا مستحضر مركّب ثابت الجرعة؛ يجب أن يحتوي البديل الصحيح على كلا "
              "المكوّنين. إضافة أو حذف مادة فعّالة ليس استبدالاً مكافئاً — يُحال "
              "إلى الطبيب المعالج.",
    },
    "flag.form": {
        "en": "This is an extended release product; extended release and "
              "immediate release forms are not interchangeable and the dosing "
              "frequency changes.",
        "ar": "هذا مستحضر ممتد المفعول؛ الأشكال ممتدة المفعول وفورية المفعول غير "
              "قابلة للتبديل ويتغيّر عدد مرات الجرعة.",
    },
    "flag.potency": {
        "en": "Within-class substitution: dose conversion required; strengths "
              "are not milligram equivalent between these molecules.",
        "ar": "استبدال داخل نفس الفئة: يلزم تحويل الجرعة؛ التركيزات ليست متكافئة "
              "بالمليجرام بين هذه الجزيئات.",
    },
    # --- counselling additions ---------------------------------------------
    "couns.penicillin": {
        "en": "Avoid beta lactam antibiotics given the penicillin allergy.",
        "ar": "تجنّب مضادات البيتا لاكتام نظراً لحساسية البنسلين.",
    },
    "couns.combo": {
        "en": "This is a fixed dose combination product providing both active "
              "components of the original.",
        "ar": "هذا مستحضر مركّب ثابت الجرعة يوفّر كلا المكوّنين الفعّالين للأصل.",
    },
    "couns.avoided": {
        "en": "A same-class option was avoided: {effect}",
        "ar": "تم تجنّب خيار من نفس الفئة بسبب: {effect}",
    },
    # deterministic fallback rationale (used if the guard drops the LLM prose)
    "rationale.fb.generic": {
        "en": "Same active ingredient and strength as the original — a direct "
              "generic substitution.",
        "ar": "نفس المادة الفعّالة والتركيز مثل الأصل — استبدال جنيس مباشر.",
    },
    "rationale.fb.class": {
        "en": "Same therapeutic class as the original; review the dose-conversion "
              "counselling below.",
        "ar": "نفس الفئة العلاجية للأصل؛ راجع إرشادات تحويل الجرعة أدناه.",
    },
    "rationale.fb.therapeutic": {
        "en": "A therapeutic alternative in the same clinical category; review the "
              "counselling below.",
        "ar": "بديل علاجي ضمن نفس الفئة السريرية؛ راجع الإرشادات أدناه.",
    },
    # --- trace step names ---------------------------------------------------
    "trace.resolve": {"en": "Resolve", "ar": "تحديد الدواء"},
    "trace.nti": {"en": "NTI gate", "ar": "بوابة المؤشر الضيق"},
    "trace.upstream": {"en": "Upstream check", "ar": "فحص الوصفة الأصلية"},
    "trace.candidates": {"en": "Candidates", "ar": "المرشحون"},
    "trace.safety": {"en": "Safety filter", "ar": "مرشّح السلامة"},
    "trace.decide": {"en": "Decide", "ar": "القرار"},
    "trace.rank": {"en": "Rank", "ar": "الترتيب"},
    "trace.narrate": {"en": "Narrate", "ar": "الصياغة"},
    # --- trace details ------------------------------------------------------
    "trace.resolve.ok": {
        "en": '"{text}" → {brand} · {ingredient} · {strength} {form} (match {score}/100).',
        "ar": '"{text}" ← {brand} · {ingredient} · {strength} {form} (تطابق {score}/100).',
    },
    "trace.resolve.fail": {
        "en": '"{text}" did not match any brand, alias or spelling in the '
              "registry above the confidence threshold.",
        "ar": '"{text}" لم يطابق أي علامة تجارية أو اسم بديل أو تهجئة في السجل '
              "فوق حدّ الثقة.",
    },
    "trace.nti.escalate": {
        "en": "{ingredient} is a narrow therapeutic index drug — substitution is "
              "short-circuited before any candidate is generated.",
        "ar": "{ingredient} دواء ذو مؤشر علاجي ضيق — يتوقف الاستبدال قبل توليد أي "
              "مرشّح.",
    },
    "trace.nti.skip": {
        "en": "{ingredient} is not a narrow therapeutic index drug — continue.",
        "ar": "{ingredient} ليس دواءً ذا مؤشر علاجي ضيق — المتابعة.",
    },
    "trace.upstream.block": {
        "en": "The prescribed {ingredient} is itself contraindicated for this "
              "patient — its generics are unsafe too.",
        "ar": "{ingredient} الموصوف نفسه ممنوع لهذا المريض — بدائله الجنيسة غير "
              "آمنة أيضاً.",
    },
    "trace.upstream.ok": {
        "en": "The prescribed {ingredient} is not contraindicated for [{flags}].",
        "ar": "{ingredient} الموصوف غير ممنوع في [{flags}].",
    },
    "trace.candidates.detail": {
        "en": "Generated {n} available candidate(s) by tier.",
        "ar": "تم توليد {n} مرشّح متاح حسب الفئة.",
    },
    "trace.safety.detail": {
        "en": "Ran after generation, before ranking: {surv} survived, {blk} blocked.",
        "ar": "شُغّل بعد التوليد وقبل الترتيب: نجا {surv}، ومُنع {blk}.",
    },
    "trace.decide.escalate": {
        "en": "No candidate survived the safety filter — escalate to the prescriber.",
        "ar": "لم ينجُ أي مرشّح من مرشّح السلامة — يُحال إلى الطبيب المعالج.",
    },
    "trace.decide.ok": {
        "en": "Lowest surviving tier is '{tier}'. Only that tier is offered, so a "
              "closer safe match is never undercut by a further one.",
        "ar": "أدنى فئة ناجية هي '{tier}'. تُعرض هذه الفئة فقط، حتى لا يُزاح بديل "
              "أقرب وأكثر أماناً لصالح بديل أبعد.",
    },
    "trace.rank.detail": {
        "en": "By tier, then stock, then price, then manufacturer continuity.",
        "ar": "حسب الفئة، ثم التوفّر، ثم السعر، ثم استمرارية الشركة المصنّعة.",
    },
    "trace.narrate.model": {
        "en": "Rationale written by {model} through the validator guard ({trips} guard trip(s)).",
        "ar": "المبرّر كُتب بواسطة {model} عبر حارس التحقق ({trips} تعثّر للحارس).",
    },
    "trace.narrate.stub": {
        "en": "Narration stubbed — deterministic run, no model prose.",
        "ar": "الصياغة معطّلة — تشغيل حتمي دون نص من النموذج.",
    },
}

TIER_AR = {"generic": "جنيس", "class": "نفس الفئة", "therapeutic": "علاجي", "none": "تصعيد"}


def t(lang: Lang, key: str, **kw) -> str:
    entry = MESSAGES.get(key)
    if not entry:
        return key
    template = entry.get(lang) or entry["en"]
    # localise embedded patient-flag names for Arabic
    if lang == "ar" and "flag" in kw:
        kw = {**kw, "flag": FLAG_AR.get(str(kw["flag"]).lower(), kw["flag"])}
    if lang == "ar" and "flags" in kw:
        parts = [FLAG_AR.get(f.strip().lower(), f.strip())
                 for f in str(kw["flags"]).split(",")]
        kw = {**kw, "flags": "، ".join(parts)}
    if lang == "ar" and "tier" in kw:
        kw = {**kw, "tier": TIER_AR.get(str(kw["tier"]), kw["tier"])}
    try:
        return template.format(**kw)
    except (KeyError, IndexError):
        return template
