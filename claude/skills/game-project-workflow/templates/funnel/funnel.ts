// Player funnel (GameFactory/DESIGN/FUNNEL.md). Copy to src/funnel.ts, import once in main.ts:
//   import { funnel } from './funnel';  funnel.attach(window.__game);
// In game code: funnel.mark('first_action') — each step counts once per session; goal_* / rewarded_* any time.
// Nothing leaves the browser until funnel.onEvent is set (own analytics or a platform's, after Alex's OK).
export type FunnelEvent = { name: string; t: number; data?: Record<string, unknown> };
const KEY = 'gf_funnel_v1';
const ONCE = new Set(['first_frame', 'first_input', 'first_action', 'first_result', 'first_reward', 'next_goal_seen', 'loop_done']);
const t0 = performance.now();

class Funnel {
  events: FunnelEvent[] = [];
  onEvent: ((e: FunnelEvent) => void) | null = null;
  private seen = new Set<string>();

  constructor() {
    const prev = this.diary();
    this.mark('boot', { session: prev.sessions + 1 });
    if (prev.sessions > 0) this.mark('return', { day: Math.floor((Date.now() - prev.first) / 864e5), sessions: prev.sessions });
    this.save({ ...prev, sessions: prev.sessions + 1, first: prev.first || Date.now() });
    const input = () => { this.mark('first_input'); removeEventListener('pointerdown', input); removeEventListener('keydown', input); };
    addEventListener('pointerdown', input); addEventListener('keydown', input);
    addEventListener('pagehide', () => this.mark('session_end', { secs: Math.round(this.now()) }));
  }

  now() { return (performance.now() - t0) / 1000; }
  has(name: string) { return this.seen.has(name); }

  mark(name: string, data?: Record<string, unknown>) {
    if (ONCE.has(name) && this.seen.has(name)) return;
    this.seen.add(name);
    const e: FunnelEvent = { name, t: Math.round(this.now() * 10) / 10, data };
    this.events.push(e);
    const d = this.diary(); d.counts[name] = (d.counts[name] || 0) + 1; this.save(d);
    if (import.meta.env?.DEV) console.debug('[funnel]', name, e.t, data ?? '');
    try { this.onEvent?.(e); } catch { /* analytics must never break the game */ }
  }

  attach(game: Record<string, unknown> | undefined) { if (game) game.funnel = this; }

  private diary(): { sessions: number; first: number; counts: Record<string, number> } {
    try { return JSON.parse(localStorage.getItem(KEY) || '') } catch { return { sessions: 0, first: 0, counts: {} }; }
  }
  private save(d: object) { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch { /* private mode */ } }
}

export const funnel = new Funnel();
