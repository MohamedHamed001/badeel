// Fixed, non-dismissible. Present on every view (spec section 10).
export function SyntheticBanner() {
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
        <span className="font-medium">SYNTHETIC DATA · NOT FOR CLINICAL USE</span>
        <span className="opacity-70">
          {"  "}· Decision support for a licensed pharmacist, not a patient-facing
          tool
        </span>
      </div>
    </div>
  );
}
