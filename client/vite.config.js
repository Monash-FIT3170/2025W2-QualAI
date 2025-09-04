import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    dedupe: ['@tiptap/react']
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    clientPort: 5173,
}
})
