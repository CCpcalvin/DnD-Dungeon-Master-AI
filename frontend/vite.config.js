import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const basename = import.meta.env.VITE_BASE_URL || "/";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    watch: {
      usePolling: true, // Use polling for file changes
    },
  },
  base: basename,
});
