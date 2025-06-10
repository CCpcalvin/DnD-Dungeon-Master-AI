import { useState, useEffect } from 'react';

import { useNavigate } from 'react-router-dom';
import api from '../../api';
import { isAuthenticated } from '../../utils/auth';

import '../../App.css';
import styles from './Home.module.css';

import TopBar from '../../components/TopBar';

async function get_session_id() {
  const res = await api.post('/session/new');
  console.log('Response:', res);
  if (res.status === 200) {
    console.log('Session created successfully');
    return res.data.session_id;
  } else {
    throw new Error('Failed to get session ID');
  }
}

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

  const handleStartJourney = async () => {
    if (!isLoggedIn) {
      navigate('/login');
      return;
    }
    try {
      await get_session_id();
      // Redirect to game page or handle session start
    } catch (error) {
      console.error('Error starting session:', error);
    }
  };

  return (
    <div className={`${styles.align_center} min-h-screen bg-gray-900 w-full max-w-7xl mx-auto`}>
      {isLoggedIn && (
        <TopBar>
          <div className="text-white font-bold">DnD Dungeon Master AI</div>
          <button
            onClick={() => navigate('/logout')}
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm"
          >
            Logout
          </button>
        </TopBar>
      )}

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
            onClick={handleStartJourney}
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
    </div>
  );
}

export default Home;
