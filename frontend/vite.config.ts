import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Support deployment to multiple paths: /1-ar/ai-tutor/, /2-ar/ai-tutor/, /3-ar/ai-tutor/
  // Set via environment variable: VITE_BASE_PATH
  base: process.env.VITE_BASE_PATH || '/',
  server: {
    port: 5173,
    host: true
  }
})
