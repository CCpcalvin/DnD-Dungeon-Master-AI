// Environment variables (prefixed with VITE_)
const { VITE_API_URL, VITE_ACCESS_TOKEN_KEY, VITE_REFRESH_TOKEN_KEY } = import.meta.env;

export const ACCESS_TOKEN = VITE_ACCESS_TOKEN_KEY || "access";
export const REFRESH_TOKEN = VITE_REFRESH_TOKEN_KEY || "refresh";

export const BACKEND_URL = VITE_API_URL || "http://localhost:8000/api";

// Message role
export const Roles = {
  PLAYER: "Player",
  NARRATOR: "Narrator",
  SYSTEM: "System",
};
