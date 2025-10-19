import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// URL do backend Django:
// Em Docker: usa o nome do serviço 'backend'
// Em desenvolvimento local: usa localhost
const BACKEND_URL = process.env.VITE_API_URL || 'https://localhost:8000'; // Se fôr necessário modificar algum destes urls, modifique também em src/libraries/api.js para evitar erros

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
  ],
  server: {
    host: '0.0.0.0',  // Permite acesso externo (necessário para Docker)
    port: 5173,
    watch: {
      usePolling: true,  // Necessário para hot reload em containers Docker
    },
    proxy: {
      // Proxy para a API do Django
      '/api': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },
      // Proxy para o Django Admin e seus recursos
      '/admin': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },
    },
  },
})