/** Minimal i18n: language comes from the platform SDK layer. Copy to src/i18n/index.ts and add locales/<lang>.ts. */
export const LANGS = ['en', 'ru', 'es', 'pt-BR', 'tr'] as const;
export type Lang = (typeof LANGS)[number];
type Dict = Record<string, string>;

export function normalizeLang(raw?: string | null): Lang {
  const code = (raw || '').trim().replace('_', '-').toLowerCase();
  const base = code.split('-')[0];
  if (base === 'pt') return 'pt-BR';
  return (LANGS as readonly string[]).includes(base) ? (base as Lang) : 'en';
}

let lang: Lang = 'en';
let dict: Dict = {};
let fallback: Dict = {};

/** Call once after platform.init(), before the first UI render. `?lang=xx` is the QA override. */
export function initI18n(platformLanguage: string | undefined, locales: Record<Lang, Dict>): Lang {
  const override = new URLSearchParams(location.search).get('lang');
  lang = normalizeLang(override || platformLanguage);
  fallback = locales.en;
  dict = locales[lang] || fallback;
  document.documentElement.lang = lang;
  return lang;
}

export const currentLang = () => lang;

/** t('shop.buy'), t('cash.earned', { n: 5 }). Plural keys: key.one / key.few / key.many / key.other. */
export function t(key: string, params: Record<string, string | number> = {}): string {
  let id = key;
  if (typeof params.n === 'number') {
    const form = new Intl.PluralRules(lang).select(params.n);
    if (dict[`${key}.${form}`] ?? fallback[`${key}.${form}`]) id = `${key}.${form}`;
    else if (dict[`${key}.other`] ?? fallback[`${key}.other`]) id = `${key}.other`;
  }
  const text = dict[id] ?? fallback[id] ?? key;
  return text.replace(/\{(\w+)\}/g, (m, p) => (p in params ? String(params[p]) : m));
}

/** Locale-aware uppercase: Turkish i → İ. */
export const upper = (s: string) => s.toLocaleUpperCase(lang);
