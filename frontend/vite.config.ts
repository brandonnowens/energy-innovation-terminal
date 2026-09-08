import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('@maptiler') || id.includes('maplibre-gl')) {
              return 'vendor-maptiler';
            }
            if (id.includes('recharts')) {
              return 'vendor-recharts';
            }
            if (id.includes('d3') || id.includes('d3-sankey')) {
              return 'vendor-d3';
            }
            if (id.includes('graphology') || id.includes('@react-sigma')) {
              return 'vendor-graph';
            }
            if (id.includes('leaflet') || id.includes('react-leaflet')) {
              return 'vendor-leaflet';
            }
            if (id.includes('html2canvas') || id.includes('file-saver')) {
              return 'vendor-export';
            }
            if (id.includes('lucide-react')) {
              return 'vendor-icons';
            }
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router-dom') || id.includes('@tanstack')) {
              return 'vendor-react';
            }
          }
        }
      }
    }
  }
})
