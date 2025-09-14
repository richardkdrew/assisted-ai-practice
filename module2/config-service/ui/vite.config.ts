import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
    fs: {
      allow: [
        // Allow serving files from the project root
        resolve(__dirname, '..'),
        // Allow serving files from the svc-client directory
        resolve(__dirname, '../svc-client')
      ]
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
