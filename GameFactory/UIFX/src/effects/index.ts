import { jellyPress, squashStretch, pressDepth, ripple, hoverTilt, hoverLift, magnetic } from './interactive';
import {
  popIn, popOut, slideIn, slideOut, dropIn, flipIn, backdrop, cameraZoom, stagger,
  glossyShine, glow, heartbeat, wiggle, breathe, shake, punch, textWave, typewriter,
} from './motion';
import { countUpFx, floatingTextFx, coinFlyFx, confettiFx, starBurst, progressFx, rewardPop } from './reward';
import type { EffectDef } from './types';

export * from './types';
export * from './interactive';
export * from './motion';
export * from './reward';

/** All effects by id (the demo page and style presets resolve effects through this). */
export const EFFECTS = Object.fromEntries(
  [
    jellyPress, squashStretch, pressDepth, ripple,
    hoverTilt, hoverLift, magnetic,
    popIn, popOut, slideIn, slideOut, dropIn, flipIn, backdrop, cameraZoom, stagger,
    glossyShine, glow, heartbeat, wiggle, breathe,
    shake, punch,
    countUpFx, floatingTextFx, coinFlyFx, confettiFx, starBurst, progressFx, rewardPop,
    textWave, typewriter,
  ].map((e) => [e.id, e as unknown as EffectDef]),
) as Record<string, EffectDef>;
