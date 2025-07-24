import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(import.meta.dirname, './src'),
      '@/app': resolve(import.meta.dirname, './src/app'),
      '@/shared': resolve(import.meta.dirname, './src/shared'),
      '@/features': resolve(import.meta.dirname, './src/features'),
      '@/assets': resolve(import.meta.dirname, './src/assets'),
    },
  },
  server: {
    port: 3000,
    host: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    target: 'es2022',
  },
})
