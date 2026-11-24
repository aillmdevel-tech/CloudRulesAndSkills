import * as THREE from 'three';
import { bootProgress, engineBusy } from './progress';

/** three.js: every GLTFLoader / TextureLoader using DefaultLoadingManager feeds the bar. Import first in main.ts. */
const LM = THREE.DefaultLoadingManager;
LM.onStart = () => engineBusy(true);
LM.onProgress = (_u, loaded, total) => { engineBusy(loaded < total); bootProgress(0.1 + 0.72 * (loaded / Math.max(1, total))); };
LM.onLoad = () => engineBusy(false);
LM.onError = (url) => console.warn('[boot] failed to load', url);

/** compile every material's shader during loading, so the first seconds of play have no hitches */
export async function precompile(renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera) {
  const r = renderer as unknown as { compileAsync?: (s: THREE.Object3D, c: THREE.Camera) => Promise<unknown> };
  if (r.compileAsync) await r.compileAsync(scene, camera); else renderer.compile(scene, camera);
}
