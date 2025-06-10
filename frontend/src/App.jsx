import './App.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";

import AuthRoute from './components/AuthRoute'
import GuestRoute from './components/GuestRoute'

import Home from './pages/Home/Home'
import Login from './pages/Login/Login'
import Register from './pages/Register/Register'
import Logout from './pages/Logout/Logout'
import Test from './pages/Test/Test'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/session" element={<div>Session Page</div>} />
        <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
        <Route path="/register" element={<GuestRoute><Register /></GuestRoute>} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/test" element={<AuthRoute><Test /></AuthRoute>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
