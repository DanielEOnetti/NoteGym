import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  
  base: '/static/',  // ← CAMBIA ESTO
  
  build: {
    outDir: 'static/dist', 
    manifest: true, 
    
    rollupOptions: {
      input: 'frontend/main.jsx' 
    }
  },
  
  server: {
    port: 5173,
    origin: 'http://localhost:5173'
  }
});