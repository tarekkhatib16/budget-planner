import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  server: {
    // host: true exposes the dev server on the LAN so the app can be opened
    // (and added to the home screen) from an iPhone on the same wifi.
    host: true,
    proxy: {
      '/api': 'http://localhost:8001',
    },
  },
});
