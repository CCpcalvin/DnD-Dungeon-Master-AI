import { useState } from "react";

import api from "../../utils/api";
import { handleApiError } from "../../utils/apiErrorHandler";

import { useNavigate, Link } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../../constants";
import styles from "./Register.module.css";

import TopBar from "../../components/TopBar";
import HomeButton from "../../components/HomeButton";
import Container from "../../components/Container";

function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // First, register the user
      const registerResponse = await api.post("/user/register", {
        username,
        password,
      });

      if (registerResponse.status === 201) {
        // If registration is successful, log the user in
        const loginResponse = await api.post("/user/token", {
          username,
          password,
        });

        if (loginResponse.status === 200) {
          const { access, refresh } = loginResponse.data;
          // Save tokens to local storage
          localStorage.setItem(ACCESS_TOKEN, access);
          localStorage.setItem(REFRESH_TOKEN, refresh);

          setUsername("");
          setPassword("");
          navigate("/");
        }
      }
    } catch (error) {
      handleApiError(error, {
        onError: (response) => {
          // Handle specific HTTP errors
          if (response.status === 401) {
            setErrorMessage("Invalid username or password");

            // Clear tokens on unauthorized
            localStorage.removeItem(ACCESS_TOKEN);
            localStorage.removeItem(REFRESH_TOKEN);
          } else if (response.status === 400) {
            setErrorMessage("This username is already taken.");
          } else {
            setErrorMessage("An unexpected error occurred");
          }
        },
      });
    }
  };

  return (
    <div>
      <TopBar>
        <HomeButton size="sm" />
      </TopBar>

      <Container>
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
            {errorMessage && (
              <p className="text-red-500 text-sm">{errorMessage}</p>
            )}
            <small className={styles.smallText}>
              Already have an account?
              <Link to="/login" className={styles.link}>
                Login here
              </Link>
            </small>
            <button type="submit" className={styles.submitButton}>
              Register
            </button>
          </form>
        </div>
      </Container>
    </div>
  );
}

export default Register;
