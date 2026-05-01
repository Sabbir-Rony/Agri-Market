import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// VITE_API_TARGET = where the dev proxy forwards /api and /uploads
// Default for local Replit dev: backend runs on port 8000.
const apiTarget = process.env.VITE_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: Number(process.env.PORT) || 5173,
    strictPort: false,
    // Replit preview is proxied through an iframe with a different host.
    // Allow all hosts so Vite doesn't block the preview.
    allowedHosts: true,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
      },
      '/uploads': {
        target: apiTarget,
        changeOrigin: true,
      },
      '/health': {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: Number(process.env.PORT) || 4173,
    allowedHosts: true,
  },
})
