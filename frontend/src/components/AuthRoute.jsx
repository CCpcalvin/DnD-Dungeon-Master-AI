import { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";

import { isAuthenticated } from "../utils/auth";

function AuthRoute({ children }) {
  const [isAuthorized, setIsAuthorized] = useState(null);

  useEffect(() => {
    const checkAuth = async () => {
      const authStatus = await isAuthenticated();
      setIsAuthorized(authStatus);
    };

    checkAuth();
  }, []);

  if (isAuthorized === null) {
    return <div>Loading...</div>;
  }

  return isAuthorized ? children : <Navigate to="/login" />;
}


export default AuthRoute;