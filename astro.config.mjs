// @ts-check
import { defineConfig } from 'astro/config';
import UnoCSS from '@unocss/astro';

export default defineConfig({
  base: '/pc-builder',
  integrations: [
    UnoCSS({ injectReset: true }),
  ],
  vite: {
    build: {
      rollupOptions: {
        output: {
          // Avoid @ in asset filenames - GitHub Pages doesn't like it
          assetFileNames: 'assets/[name]-[hash][extname]',
          chunkFileNames: 'assets/[name]-[hash].js',
        },
      },
    },
  },
});
