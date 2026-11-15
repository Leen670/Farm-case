import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // Large videos stay out of the watcher. Everything else in public, including
    // new artwork, has to be watched or Vite keeps serving the old file list.
    watch: { ignored: ["**/*.mp4"] },
  },
});
