// Vite com React. O servidor de desenvolvimento roda em http://localhost:5173,
// a origem que o CORS do backend libera.
//
// fs.allow sobe até a raiz do acervo porque main.jsx importa os tokens da marca
// de assets/css/inteli-brand.css, em vez de copiar cores e fontes para cá. No
// repositório do grupo, sem o acervo ao lado, troque esse import pelo CSS do
// próprio grupo e apague o fs.allow.
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, fs: { allow: ['..', '../../..'] } },
});
