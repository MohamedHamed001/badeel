import { useLang } from "../LangContext";

// Fixed, non-dismissible. Present on every view (spec section 10).
export function SyntheticBanner() {
  const { t } = useLang();
  return (
    <div
      className="sticky top-0 z-50 border-b text-center text-[11px] tracking-wide"
      style={{
        background: "var(--color-ink)",
        color: "var(--color-paper)",
        borderColor: "var(--color-ink)",
      }}
    >
      <div className="px-4 py-1.5">
        <span className="font-medium">{t("banner.title")}</span>
        <span className="opacity-70"> {t("banner.sub")}</span>
      </div>
    </div>
  );
}
