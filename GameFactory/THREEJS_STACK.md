# Three.js-стек GameFactory (по умолчанию для новых Three.js-игр)

Утверждён Alex 2026-11-11. Ставится в каждый проект локально (npm), версии фиксированы.

| Библиотека | Версия | Для чего |
|---|---|---|
| three (+ @types/three) | 0.187.0 | рендер, GLTFLoader из `three/addons` |
| postprocessing | 6.39.6 | EffectComposer, Bloom, ToneMapping, HueSaturation, Vignette, SMAA |
| n8ao | 2.0.1 | SSAO (`N8AOPostPass` в composer postprocessing) |
| three.quarks | 0.17.1 | частицы/VFX |
| gsap | 3.15.1 | твины камеры, UI, катсцен |
| @dimforge/rapier3d-compat | 0.21.0 | физика, character controller |
| vite / typescript / vitest | 8.3.8 / 7.0.2 / 5.1.0 | сборка, типы, тесты |
| Blender | 5.2.3 LTS (`/opt/homebrew/bin/blender`, MCP blender) | модели, конвертация, запекание |

```bash
npm i three@0.187.0 postprocessing@6.39.6 n8ao@2.0.1 three.quarks@0.17.1 gsap@3.15.1 @dimforge/rapier3d-compat@0.21.0
npm i -D --legacy-peer-deps @types/three@0.187.0 vite@8.3.8 typescript@7.0.2 vitest@5.1.0
echo "legacy-peer-deps=true" > .npmrc   # vitest 5.1 ломает arborist npm 11 (edgesOut) без этого
```

## Известные проблемы

- **n8ao 2.0.1 + three 0.187**: класс MRT n8ao переопределяет `texture` → массив; three падает в `setupRenderTarget` (`reading 'length'`). Фикс без правки node_modules — после создания прохода:
  ```ts
  const proto = Object.getPrototypeOf(aoPass.depthDownsampleTarget);
  Object.defineProperty(proto, 'texture', { configurable: true,
    get() { return this.textures[0]; }, set(v) { this.textures[0] = v; } });
  ```
- n8ao без типов: `declare module 'n8ao'` с классом `N8AOPostPass extends Pass`.
- С postprocessing: `renderer.toneMapping = NoToneMapping`, тонмаппинг через `ToneMappingEffect`.
- Шейдерные `#include <...>` в ShaderMaterial — только на отдельной строке.

Пример рабочей связки: `/Users/mac/ThrowForAninals/src/engine/renderer.ts`.
