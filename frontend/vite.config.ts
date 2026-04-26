import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom'],
          query: ['@tanstack/react-query', 'axios'],
          motion: ['framer-motion'],
          charts: ['recharts', 'd3-scale'],
          state: ['zustand'],
        },
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173
  }
})
