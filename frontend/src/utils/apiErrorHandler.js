/**
 * Handles API errors consistently across the application
 * @param {Error} error - The error object from axios
 * @param {Object} options - Additional options
 * @param {Function} options.onError - Callback for handling non-network errors
 */
export const handleApiError = (error, { onError } = {}) => {
  console.error("API Error:", error);

  // Handle network/server errors
  if (!error.response) {
    alert("No response from backend server. Please check your connection.");
    return;
  }

  if (error.code === "ERR_NETWORK") {
    alert("Network error. Please check your internet connection.");
    return;
  }

  // For other errors, delegate to the component's error handler if provided
  if (onError) {
    onError(error.response);
  } else {
    // Default error handling if no handler provided
    console.warn("Unhandled API error:", error.response);
  }
};
