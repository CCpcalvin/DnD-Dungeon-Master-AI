import { jwtDecode } from "jwt-decode";

import api from "./api";
import { handleApiError } from "./apiErrorHandler";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";

const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN);
  if (!refreshToken) return false;

  try {
    const response = await api.post("/user/token/refresh", {
      refresh: refreshToken,
    });
    if (response.status === 200) {
      const { access } = response.data;
      localStorage.setItem(ACCESS_TOKEN, access);
      return true;
    }
  } catch (error) {
    handleApiError(error, {
      onError: (response) => {
        logout();
        alert("An authentication error occurred. Please try again.");
      },
    });
  }
  return false;
};

export const isAuthenticated = async () => {
  const token = localStorage.getItem(ACCESS_TOKEN);
  if (!token) return false;

  try {
    const decoded = jwtDecode(token);
    const now = Date.now() / 1000;

    // If token is expired, try to refresh it
    if (decoded.exp < now) {
      return await refreshAccessToken();
    }

    return true;
  } catch (error) {
    console.error("Error in authentication:", error);
    return await refreshAccessToken();
  }
};

export const logout = () => {
  localStorage.removeItem(ACCESS_TOKEN);
  localStorage.removeItem(REFRESH_TOKEN);
  delete api.defaults.headers.common["Authorization"];
};
