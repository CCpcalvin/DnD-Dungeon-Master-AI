import { useState } from 'react';
import '../../App.css';
import styles from './Register.module.css';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/user/register', { username, password });
      if (response.status === 201) {
        setUsername('');
        setPassword('');
        navigate('/login');
      }
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  return (
    <div className={styles.container}>
      <h2>Create Account</h2>
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
          Already have an account? 
          <Link to="/login" className={styles.smallTestLink}>Login here</Link>
        </small>
        <button type="submit" className={styles.submitButton}>
          Register
        </button>
      </form>
    </div>
  );
}

export default Register;
