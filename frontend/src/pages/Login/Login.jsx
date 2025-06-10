import { useState } from 'react';
import '../../App.css';
import styles from './Login.module.css';
import api from '../../api';

import { useNavigate, Link } from 'react-router-dom';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/user/token', { username, password });
      if (response.status === 200) {
        const { access, refresh } = response.data;
        // Save tokens to local storage
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        
        setUsername('');
        setPassword('');
        navigate('/');
      }
    } catch (error) {
      console.error('Login failed:', error);
      // Clear any existing tokens on failed login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  };

  return (
    <div className={styles.container}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          className={styles.inputField}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          className={styles.inputField}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <small className={styles.smallText}>
          Don't have an account?
          <Link to="/register" className={styles.smallTestLink}>Register here</Link>
        </small>
        <button type="submit" className={styles.submitButton}>
          Login
        </button>
      </form>
    </div>
  );
}

export default Login;
