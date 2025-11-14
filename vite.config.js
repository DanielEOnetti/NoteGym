// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // --- Integración con Django ---
  build: {
    // 1. Dónde pondrá Vite los archivos compilados
    // (Debe coincidir con STATICFILES_DIRS en Django)
    outDir: 'static/dist', 
    
    // 2. Este archivo le "dirá" a Django qué archivos se han creado.
    manifest: true, 
    
    rollupOptions: {
      // 3. Este es el "punto de entrada" de nuestra app React.
      // (Crearemos este archivo en el siguiente paso)
      input: 'frontend/main.jsx' 
    }
  },
  
  server: {
    // 4. El puerto que usará el servidor de desarrollo de Vite
    port: 5173 
  }
});