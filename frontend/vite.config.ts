import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // Проксируем API на бэкенд — браузер общается только со своим origin.
    proxy: {
      // 127.0.0.1, не localhost: Node резолвит localhost в IPv6 (::1),
      // а Docker слушает IPv4 — иначе 502.
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
