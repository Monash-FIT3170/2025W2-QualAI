import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    clientPort: 5173,
    proxy: {
      '/projects': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
});
