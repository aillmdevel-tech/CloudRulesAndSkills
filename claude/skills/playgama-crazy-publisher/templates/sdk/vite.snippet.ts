// pub sdk-install: merge into vite.config.ts (keep the game's own plugins and options)
import { defineConfig } from 'vite';
import playgamaBridge from '@playgama/bridge/vite';
import { rmSync } from 'node:fs';
import { resolve } from 'node:path';

/** non-Playgama builds must not carry Bridge files */
const dropBridgeConfig = { name: 'drop-bridge-config', apply: 'build' as const,
  closeBundle() { rmSync(resolve(__dirname, 'dist', 'playgama-bridge-config.json'), { force: true }); } };

/** build target = Vite mode: web (dev, localStorage) | playgama (Bridge local, first <script>) | crazygames (SDK v3 from JS) */
export default defineConfig(({ mode }) => {
  const platform = mode === 'playgama' || mode === 'crazygames' ? mode : 'web';
  return {
    base: './',
    define: { 'import.meta.env.VITE_PLATFORM': JSON.stringify(platform) },
    plugins: [...(platform === 'playgama' ? [playgamaBridge({ mode: 'local' })] : []), ...(platform === 'crazygames' ? [dropBridgeConfig] : [])],
    build: { target: 'es2022' },
  };
});
