// pub sdk-install: boot order for src/main.ts (adapt names to the game; keep the order)
import './boot/threeHook';                       // three.js only, must be the first import
import { bootProgress, bootLang, bootDone, assetsIdle, firstFrame } from './boot/progress';
import { createPlatform } from './platform';

const platform = await createPlatform();          // 1. SDK init (never blocks: offline on failure)
platform.loadingStart();
bootProgress(0.08);
bootLang(initI18n(platform.language, LOCALES));   // 2. language from the SDK, before the first UI render
const save = await platform.storage.get(SAVE_KEY); // 3. saves only through the platform
// 4. IAP (only when FEATURES.iap): restore permanent items, grant + consume unprocessed consumables
for (const id of await platform.purchases.owned()) { grant(id); if (isConsumable(id)) await platform.purchases.consume(id); }
// 5. pause and audio from the platform (ads included)
platform.onPause((p) => setPaused('platform', p));
platform.onAudio((on) => setMuted('platform', !on));
if (!platform.audioEnabled) setMuted('platform', true);
// 6. build the world; the bar moves with every load
await buildWorld();
await assetsIdle();
await precompile(renderer, scene, camera);       // threeHook: shaders compile here, not in the first seconds of play
bootProgress(0.97);
renderer.render(scene, camera); await firstFrame();
platform.loadingStop();                           // 7. Playgama game_ready / CrazyGames loadingStop: player can act now
bootDone();                                       // 8. loading screen fades out
// gameplayStart when play really starts (and after every resume); gameplayStop on menu, pause, level end, ad
