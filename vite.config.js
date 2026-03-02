// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  
  // Cambia esto para que coincida con la carpeta de salida relativa a STATIC_URL
  base: '/static/dist/', 
  
  build: {
    
    outDir: 'static/dist', 
    manifest: true, 
    emptyOutDir: true, 
    
    rollupOptions: {
      input: 'frontend/main.jsx' 
    }
  },
  
  server: {
    port: 5173,
    origin: 'http://localhost:5173'
  }
});