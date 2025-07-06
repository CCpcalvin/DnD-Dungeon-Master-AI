import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ command, mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '');
  
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
  };
});
