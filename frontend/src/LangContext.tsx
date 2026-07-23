import { createContext, useContext } from "react";
import type { Lang, StringKey } from "./i18n";
import { makeT } from "./i18n";

interface LangCtx {
  lang: Lang;
  dir: "ltr" | "rtl";
  t: (key: StringKey) => string;
  setLang: (l: Lang) => void;
}

// React Context is built-in — not a state-management library. It only carries
// the current language + a bound translator so components avoid prop-drilling.
const Ctx = createContext<LangCtx>({
  lang: "en",
  dir: "ltr",
  t: makeT("en"),
  setLang: () => {},
});

export const LangProvider = Ctx.Provider;
export const useLang = () => useContext(Ctx);
