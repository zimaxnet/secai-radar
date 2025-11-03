import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate React and React DOM into their own chunk
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // Separate large UI libraries
          'ui-vendor': ['recharts', '@tanstack/react-table'],
          // Separate form libraries
          'form-vendor': ['react-hook-form', '@hookform/resolvers', 'zod'],
        },
      },
    },
    chunkSizeWarningLimit: 1000, // Increase limit to 1MB for better visibility
  },
})

