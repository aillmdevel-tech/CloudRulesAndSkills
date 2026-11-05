// UI sound manager on Web Audio: lazy decode, volume buses, mute, pitch variation, anti-spam cooldowns,
// polyphony limit, autoplay unlock on first gesture, ogg/mp3 auto-pick, persisted volume.

export interface SoundEntry {
  category: string;
  volume: number;
  pitchVariation: number; // ± semitones
  duration?: number;
  description?: string;
  license?: string;
  source?: string;
}

export interface SoundManifest {
  sounds: Record<string, SoundEntry>;
}

export interface PlayOpts {
  volume?: number; // 0..1 multiplier on the entry volume
  pitch?: number; // semitones offset
  bus?: string; // default: entry.category
  cooldown?: number; // ms; default per category
  delay?: number; // ms
}

const DEFAULT_COOLDOWN: Record<string, number> = { ui: 40, window: 60, feedback: 80, reward: 30 };
const MAX_VOICES_PER_SOUND = 6;
const STORE_KEY = 'uifx.audio';

export class SoundManager {
  readonly ctx: AudioContext;
  readonly master: GainNode;
  private buses = new Map<string, GainNode>();
  private buffers = new Map<string, Promise<AudioBuffer | null>>();
  private lastPlayed = new Map<string, number>();
  private voices = new Map<string, number>();
  private warned = new Set<string>();
  private ext: 'ogg' | 'mp3';
  private state: { master: number; muted: boolean; buses: Record<string, number> };
  /** Optional remap: semantic event → sound id (style presets set this). */
  aliases: Record<string, string> = {};

  constructor(
    public baseUrl: string,
    public manifest: SoundManifest,
  ) {
    const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    this.ctx = new AC({ latencyHint: 'interactive' });
    this.master = this.ctx.createGain();
    this.master.connect(this.ctx.destination);
    const probe = document.createElement('audio');
    this.ext = probe.canPlayType('audio/ogg; codecs="opus"') ? 'ogg' : 'mp3';
    this.state = { master: 0.8, muted: false, buses: {} };
    try {
      Object.assign(this.state, JSON.parse(localStorage.getItem(STORE_KEY) ?? '{}'));
    } catch {
      /* storage blocked */
    }
    this.applyMaster();
    const unlock = () => {
      if (this.ctx.state !== 'running') void this.ctx.resume();
    };
    for (const ev of ['pointerdown', 'keydown', 'touchstart']) window.addEventListener(ev, unlock, { capture: true, passive: true });
  }

  static async load(baseUrl: string): Promise<SoundManager> {
    const base = baseUrl.endsWith('/') ? baseUrl : baseUrl + '/';
    const manifest = (await (await fetch(base + 'sounds.json')).json()) as SoundManifest;
    return new SoundManager(base, manifest);
  }

  /** Decode the listed sounds ahead of time (call after load, e.g. for the current screen). */
  preload(ids: string[] = Object.keys(this.manifest.sounds)): Promise<unknown> {
    return Promise.all(ids.map((id) => this.buffer(this.aliases[id] ?? id)));
  }

  private buffer(id: string): Promise<AudioBuffer | null> {
    let p = this.buffers.get(id);
    if (!p) {
      p = fetch(`${this.baseUrl}${id}.${this.ext}`)
        .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error(`${r.status} ${id}`))))
        .then((b) => this.ctx.decodeAudioData(b))
        .catch((e) => {
          console.warn('[uifx] sound failed', id, e);
          return null;
        });
      this.buffers.set(id, p);
    }
    return p;
  }

  bus(name: string): GainNode {
    let g = this.buses.get(name);
    if (!g) {
      g = this.ctx.createGain();
      g.gain.value = this.state.buses[name] ?? 1;
      g.connect(this.master);
      this.buses.set(name, g);
    }
    return g;
  }

  /** Play by sound id or by alias (e.g. 'button.press'). Returns false if skipped. */
  async play(idOrAlias: string, o: PlayOpts = {}): Promise<boolean> {
    const id = this.aliases[idOrAlias] ?? idOrAlias;
    if (!id || id === 'none') return false;
    const entry = this.manifest.sounds[id];
    if (!entry) {
      if (!this.warned.has(id)) console.warn('[uifx] sound not installed:', id, '— install it or override the event sound');
      this.warned.add(id);
      return false;
    }
    if (this.state.muted || this.ctx.state === 'closed') return false;
    const now = performance.now();
    const cd = o.cooldown ?? DEFAULT_COOLDOWN[entry.category] ?? 40;
    if (now - (this.lastPlayed.get(id) ?? -1e9) < cd) return false;
    if ((this.voices.get(id) ?? 0) >= MAX_VOICES_PER_SOUND) return false;
    this.lastPlayed.set(id, now);
    const buf = await this.buffer(id);
    if (!buf || this.ctx.state !== 'running') return false;
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    const semis = (o.pitch ?? 0) + (Math.random() * 2 - 1) * entry.pitchVariation;
    src.playbackRate.value = Math.pow(2, semis / 12);
    const g = this.ctx.createGain();
    g.gain.value = entry.volume * (o.volume ?? 1);
    src.connect(g).connect(this.bus(o.bus ?? entry.category));
    this.voices.set(id, (this.voices.get(id) ?? 0) + 1);
    src.onended = () => this.voices.set(id, (this.voices.get(id) ?? 1) - 1);
    src.start(this.ctx.currentTime + (o.delay ?? 0) / 1000);
    return true;
  }

  // ---- volume control (persisted per browser)
  get volume(): number {
    return this.state.master;
  }
  set volume(v: number) {
    this.state.master = Math.max(0, Math.min(1, v));
    this.applyMaster();
    this.save();
  }
  get muted(): boolean {
    return this.state.muted;
  }
  set muted(m: boolean) {
    this.state.muted = m;
    this.applyMaster();
    this.save();
  }
  setBusVolume(name: string, v: number): void {
    this.state.buses[name] = v;
    this.bus(name).gain.setTargetAtTime(v, this.ctx.currentTime, 0.02);
    this.save();
  }
  getBusVolume(name: string): number {
    return this.state.buses[name] ?? 1;
  }
  private applyMaster() {
    this.master.gain.setTargetAtTime(this.state.muted ? 0 : this.state.master, this.ctx.currentTime, 0.02);
  }
  private save() {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(this.state));
    } catch {
      /* storage blocked */
    }
  }
}
