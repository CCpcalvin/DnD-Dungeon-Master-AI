import { useState, useEffect } from 'react';

import { useNavigate, Link } from 'react-router-dom';
import { isAuthenticated } from '../../utils/auth';

import '../../App.css';
import styles from './Home.module.css';

import TopBar from '../../components/TopBar';
import LogoutButton from '../../components/LogoutButton';
import Container from '../../components/Container';

function Home() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      setIsLoggedIn(await isAuthenticated());
    };
    checkAuth();

    // Set up a storage event listener to detect token changes in other tabs
    const handleStorageChange = checkAuth;
    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  return (
    <div className={`${styles.align_center} min-h-screen bg-gray-900 w-full mx-auto`}>
      {isLoggedIn && (
        <TopBar>
          <Link
            to="/my-sessions"
            className="text-white hover:text-gray-300 font-bold"
          >
            Continue Your Journey
          </Link>
          <LogoutButton />
        </TopBar>
      )}

      <Container>
        <div className="w-full flex items-center justify-center flex-col"
          style={{
            minHeight: isLoggedIn ? 'calc(100vh - 4rem)' : '100vh',
          }}
        >
          <h1 className={`text-2xl text-red-400 mb-4 text-center tracking-widest drop-shadow-lg font-UnifrakturCook ${styles.h1}`}>
            How high can you climb?
          </h1>
          <div className="flex w-full justify-center max-w-md mt-4 gap-20">
            <button
              className="bg-green-800 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
              onClick={() => navigate('/player-creation')}
            >
              Start Your Adventure
            </button>
            {!isLoggedIn && (
              <button
                className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded"
                onClick={() => navigate('/login')}
              >
                Login / Register
              </button>
            )}
          </div>
        </div>
      </Container>
    </div>
  );
}

export default Home;
