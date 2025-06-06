import './App.css'
import { BrowserRouter, Routes, Route } from "react-router";

import Home from './pages/Home/Home'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/session" element={<div>Session Page</div>} />
        <Route path="/login" element={<div>Login Page</div>} />
        <Route path="/register" element={<div>Register Page</div>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
