import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import AuthRoute from './components/AuthRoute'
import GuestRoute from './components/GuestRoute'

import Home from './pages/Home/Home'
import Login from './pages/Login/Login'
import Register from './pages/Register/Register'
import Logout from './pages/Logout/Logout'
import Test from './pages/Test/Test'
import Session from './pages/Session/Session'
import MySessions from './pages/MySessions/MySessions'
import PlayerCreation from './pages/PlayerCreation/PlayerCreation'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
        <Route path="/register" element={<GuestRoute><Register /></GuestRoute>} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/test" element={<AuthRoute><Test /></AuthRoute>} />
        <Route path="/my-sessions" element={<AuthRoute><MySessions /></AuthRoute>} />
        <Route path="/player-creation" element={<AuthRoute><PlayerCreation /></AuthRoute>} />
        <Route path="/session/:sessionId" element={<AuthRoute><Session /></AuthRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
