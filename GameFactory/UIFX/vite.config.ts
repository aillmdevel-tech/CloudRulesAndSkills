import { defineConfig } from 'vite';
import { resolve } from 'node:path';

// Demo: http://localhost:5199 — sounds are served from ../sounds at the site root.
export default defineConfig({
  root: resolve(__dirname, 'demo'),
  publicDir: resolve(__dirname, 'sounds'),
  server: { port: 5199, strictPort: true },
  build: { outDir: resolve(__dirname, 'demo-dist'), emptyOutDir: true },
});
