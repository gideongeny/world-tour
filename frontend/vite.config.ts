import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path"

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      '/auth': 'http://localhost:5000',
      '/booking': 'http://localhost:5000',
      '/ai': 'http://localhost:5000',
      '/finance': 'http://localhost:5000',
      '/admin': 'http://localhost:5000',
      '/api': 'http://localhost:5000',
      '/seed': 'http://localhost:5000',
    }
  }
})
