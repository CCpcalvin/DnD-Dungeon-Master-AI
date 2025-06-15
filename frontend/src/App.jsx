import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import api from "./api";

import AuthRoute from "./components/AuthRoute";
import GuestRoute from "./components/GuestRoute";

import Home from "./pages/Home/Home";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import Logout from "./pages/Logout/Logout";
import Session from "./pages/Session/Session";
import MySessions from "./pages/MySessions/MySessions";
import PlayerCreation from "./pages/PlayerCreation/PlayerCreation";

import TestMenu from "./pages/TestPages/TestMenu";
import RedirectTest from "./pages/TestPages/RedirectTest";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          path="/login"
          element={
            <GuestRoute>
              <Login />
            </GuestRoute>
          }
        />
        <Route
          path="/register"
          element={
            <GuestRoute>
              <Register />
            </GuestRoute>
          }
        />
        <Route path="/logout" element={<Logout />} />
        <Route
          path="/my-sessions"
          element={
            <AuthRoute>
              <MySessions />
            </AuthRoute>
          }
        />
        <Route
          path="/player-creation"
          element={
            <AuthRoute>
              <PlayerCreation />
            </AuthRoute>
          }
        />
        <Route
          path="/session/:sessionId"
          element={
            <AuthRoute>
              <Session api={api} />
            </AuthRoute>
          }
        />

        {/* Testing */}
        <Route
          path="/test"
          element={
            <AuthRoute>
              <TestMenu />
            </AuthRoute>
          }
        />

        <Route path="/test/:testCase" element={<RedirectTest />} />

        {/* Invalid URL */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
