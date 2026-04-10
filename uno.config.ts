import { defineConfig, presetUno, presetWebFonts } from 'unocss';

export default defineConfig({
  presets: [
    presetUno(),
    presetWebFonts({
      fonts: {
        sans: 'Inter:400,500,600,700,800,900',
      },
    }),
  ],
  theme: {
    colors: {
      accent: '#22c55e',
      dark: '#0a0a0b',
      card: '#111',
      border: '#222',
    },
  },
});
