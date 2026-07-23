// Frontend string catalogue. Two languages, no i18n library — a flat dictionary
// and a bound t(). Arabic drives RTL layout (see App / LangContext).

export type Lang = "en" | "ar";

type Entry = { en: string; ar: string };

const S = {
  // header / nav
  "nav.console": { en: "Console", ar: "الواجهة" },
  "nav.eval": { en: "Eval browser", ar: "حالات التقييم" },
  "nav.results": { en: "Results", ar: "النتائج" },
  "chip.real": { en: "REAL DRUGS", ar: "أدوية حقيقية" },
  "chip.synthetic": { en: "SYNTHETIC", ar: "بيانات اصطناعية" },
  "health.narration": { en: "narration", ar: "الصياغة" },
  "lang.toggle": { en: "العربية", ar: "EN" },
  // banner
  "banner.title": { en: "SYNTHETIC DATA · NOT FOR CLINICAL USE", ar: "بيانات للعرض · ليست للاستخدام السريري" },
  "banner.sub": {
    en: "· Decision support for a licensed pharmacist, not a patient-facing tool",
    ar: "· دعم قرار لصيدلي مرخّص، وليست أداة موجّهة للمريض",
  },
  // query bar
  "query.placeholder": { en: "e.g. Cardex 10 mg is short · كاردكس ١٠ ناقص", ar: "مثال: كونكور ٥ ناقص والمريض عنده ربو" },
  "query.analyze": { en: "Analyze", ar: "حلّل" },
  "query.flags": { en: "Patient flags", ar: "حالات المريض" },
  "query.meds": { en: "Concurrent meds", ar: "أدوية متزامنة" },
  // empty state
  "empty.hint": { en: "Enter a shortage above, or start from a common case:", ar: "أدخل نقصاً بالأعلى، أو ابدأ من حالة شائعة:" },
  // verdicts
  "verdict.stop": { en: "Do not substitute", ar: "لا تصرف بديلاً" },
  "verdict.caution": { en: "Permitted with counselling", ar: "مسموح مع إرشاد" },
  "verdict.clear": { en: "Substitution permitted", ar: "الاستبدال مسموح" },
  "verdict.unresolved": { en: "Not in registry", ar: "غير موجود في السجل" },
  // tier rail
  "rail.title": { en: "Tier rail", ar: "سلّم الفئات" },
  "tier.generic": { en: "Generic", ar: "جنيس" },
  "tier.class": { en: "Same class", ar: "نفس الفئة" },
  "tier.therapeutic": { en: "Therapeutic", ar: "علاجي" },
  "tier.none": { en: "Escalate", ar: "تصعيد" },
  // substitute / safety / blocked
  "result.nosub": { en: "No substitute offered — see the safety panel and reasoning.", ar: "لا يوجد بديل — راجع لوحة السلامة والتحليل." },
  "safety.title": { en: "Safety", ar: "السلامة" },
  "blocked.title": { en: "Considered and rejected", ar: "تم النظر فيها ورفضها" },
  "audit.toggle": { en: "Show reasoning", ar: "اعرض التحليل" },
  "audit.steps": { en: "deterministic steps", ar: "خطوات حتمية" },
  // footer meta
  "meta.model": { en: "model", ar: "النموذج" },
  "meta.trips": { en: "guard trips", ar: "تعثّرات الحارس" },
  "meta.latency": { en: "latency", ar: "الزمن" },
  "meta.resolution": { en: "resolution", ar: "التطابق" },
  // eval browser
  "eval.title": { en: "Adversarial eval — 30 labelled cases", ar: "تقييم عدائي — ٣٠ حالة موسومة" },
  "eval.id": { en: "ID", ar: "المعرّف" },
  "eval.trap": { en: "Trap", ar: "الفخ" },
  "eval.query": { en: "Query", ar: "الاستعلام" },
  "eval.expected": { en: "Expected", ar: "المتوقّع" },
  "eval.run": { en: "Run →", ar: "شغّل ←" },
  "eval.escalate": { en: "escalate", ar: "تصعيد" },
  // results
  "results.title": { en: "Results — before and after", ar: "النتائج — قبل وبعد" },
  "results.system": { en: "System", ar: "النظام" },
  "results.correct": { en: "Correct", ar: "صحيح" },
  "results.safe": { en: "Safe", ar: "آمن" },
  "results.baseline": { en: "Naive baseline", ar: "الأساس الساذج" },
  "results.current": { en: "Badeel (current)", ar: "بديل (الحالي)" },
  "results.pertrap": { en: "Per-trap breakdown", ar: "التفصيل حسب الفخ" },
  "results.correctW": { en: "correct", ar: "صحيح" },
  "results.safeW": { en: "safe", ar: "آمن" },
  "results.loading": { en: "Loading…", ar: "جارٍ التحميل…" },
  "results.absent": { en: "No eval report yet. Run the scorer to generate one.", ar: "لا يوجد تقرير تقييم بعد. شغّل المصحّح لإنشائه." },
  "m.tier": { en: "tier", ar: "الفئة" },
  "m.escalate": { en: "escalate", ar: "التصعيد" },
  "m.recall": { en: "recall", ar: "الاستدعاء" },
  "m.flags": { en: "flags", ar: "المؤشرات" },
} satisfies Record<string, Entry>;

export type StringKey = keyof typeof S;

// Arabic display names for the fixed patient-flag vocabulary.
export const FLAG_AR: Record<string, string> = {
  "bronchial asthma": "الربو الشعبي",
  "penicillin allergy": "حساسية البنسلين",
  pregnancy: "الحمل",
  "severe renal impairment": "القصور الكلوي الشديد",
  "ischaemic heart disease": "مرض القلب الإقفاري",
  paediatric: "الأطفال",
};

export function makeT(lang: Lang) {
  return (key: StringKey): string => S[key][lang];
}

export function tierLabel(lang: Lang, tier: string): string {
  const map: Record<string, StringKey> = {
    generic: "tier.generic",
    class: "tier.class",
    therapeutic: "tier.therapeutic",
    none: "tier.none",
  };
  const k = map[tier];
  return k ? S[k][lang] : tier;
}
