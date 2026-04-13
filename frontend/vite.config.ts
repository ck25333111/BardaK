//────────────────────────────────────────
// frontend/vite.config.ts
// Конфиг Vite:
// - plugins: React (jsx/tsx, fast refresh) + Tailwind v4
// - resolve.alias: алиас "@" -> "./src" чтобы не писать ../../../
//────────────────────────────────────────

import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import path from "node:path"

export default defineConfig({
  plugins: [
    // Нужен для React/TSX: корректная обработка JSX/TSX + Fast Refresh
    react(),

    // Tailwind v4 через Vite-плагин
    tailwindcss(),
  ],
  resolve: {
    alias: {
      // Теперь можно: import x from "@/shared/..."
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
