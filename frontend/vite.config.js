import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig(({ command, mode }) => {
  // Go up one level from frontend directory to get to the root
  const rootDir = path.resolve(__dirname, '..');

  // Load env file from root directory
  const env = loadEnv(mode, rootDir, '');
  
  // Now you can access the environment variables via env.VARIABLE_NAME
  const basename = env.VITE_BASE_URL || "/";

  return {
    plugins: [react()],
    server: {
      host: "0.0.0.0",
      watch: {
        usePolling: true, // Use polling for file changes
      },
    },
    base: basename,
  };});
