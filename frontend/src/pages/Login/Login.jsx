import { useState } from 'react';

import api from '../../api';
import { useNavigate, Link } from 'react-router-dom';

import { ACCESS_TOKEN, REFRESH_TOKEN } from '../../constants';

import styles from './Login.module.css';

import TopBar from '../../components/TopBar';
import HomeButton from '../../components/HomeButton';
import Container from '../../components/Container';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    try {
      const response = await api.post('/user/token', { username, password });

      if (response.status === 200) {
        const { access, refresh } = response.data;
        // Save tokens to local storage
        localStorage.setItem(ACCESS_TOKEN, access);
        localStorage.setItem(REFRESH_TOKEN, refresh);

        setUsername('');
        setPassword('');
        navigate('/');
      }
    } catch (error) {
      // Console error for debugging
      console.error('Login failed:', error);

      // Check if the error is a 401 Unauthorized
      if (error.response.status === 401) {
        setErrorMessage('Invalid username or password');
      }
      else {
        setErrorMessage('Unknown Error');
      }

      // Clear any existing tokens on failed login
      localStorage.removeItem(ACCESS_TOKEN);
      localStorage.removeItem(REFRESH_TOKEN);
    }
  };

  return (
    <div>
      <TopBar>
        <HomeButton size="sm" />
      </TopBar>

      <Container>
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
            {errorMessage && <p className="text-red-500 text-sm">{errorMessage}</p>}
            <small className={styles.smallText}>
              Don't have an account?
              <Link to="/register" className={styles.link}>Register here</Link>
            </small>
            <button type="submit" className={styles.submitButton}>
              Login
            </button>
          </form>
        </div>
      </Container>
    </div>
  );
}

export default Login;
