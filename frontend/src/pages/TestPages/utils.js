// Simulate network delay between 300-800ms
export async function NetworkDelay() {
  const delay = 300 + Math.random() * 500;
  return new Promise((resolve) => setTimeout(resolve, delay));
}

// Generate a 404 error response
export function PageNotFoundError(message = "Page not found") {
  return {
    response: {
      status: 404,
      data: {
        status: "error",
        message: message,
        code: 404,
        timestamp: new Date().toISOString(),
      },
    },
    isAxiosError: true,
  };
}
