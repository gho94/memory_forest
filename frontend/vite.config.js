import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['@ffmpeg/ffmpeg', '@ffmpeg/util'],
  },
  server: {
    host: '0.0.0.0',  // leb.Delete when deploying
    port: 3000,       // leb.Delete when deploying
    watch: {
      usePolling: true  // leb.Delete when deploying
    },
    headers: {
      "Cross-Origin-Opener-Policy" : "same-origin",
      "Cross-Origin-Embedder-Policy" : "unsafe-none",
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
});