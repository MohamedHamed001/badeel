import { useLang } from "../LangContext";

// Fixed, non-dismissible. Present on every view (spec section 10).
export function SyntheticBanner() {
  const { t } = useLang();
  return (
    <div
      className="sticky top-0 z-50 border-b text-center text-[11px] tracking-wide"
      style={{
        background: "#0a0c0e",
        color: "var(--color-ink-muted)",
        borderColor: "var(--color-rule)",
      }}
    >
      <div className="px-4 py-1.5">
        <span className="font-semibold" style={{ color: "var(--color-caution)" }}>
          {t("banner.title")}
        </span>
        <span> {t("banner.sub")}</span>
      </div>
    </div>
  );
}
