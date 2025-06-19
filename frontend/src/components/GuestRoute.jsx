import { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";

import { isAuthenticated } from "../utils/auth";

import Loading from "./Loading";

function GuestRoute({ children }) {
  const [isAuthorized, setIsAuthorized] = useState(null);

  useEffect(() => {
    const checkAuth = async () => {
      const authStatus = await isAuthenticated();
      setIsAuthorized(authStatus);
    };

    checkAuth();
  }, []);

  if (isAuthorized === null) {
    return <Loading />;
  }

  return !isAuthorized ? children : <Navigate to="/" />;
}


export default GuestRoute;
