import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El proxy evita problemas de CORS en desarrollo: /api y /health se reenvían a FastAPI.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: process.env.VITE_BACKEND_URL || "http://localhost:8000", changeOrigin: true },
      "/health": { target: process.env.VITE_BACKEND_URL || "http://localhost:8000", changeOrigin: true },
    },
  },
});
