import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api';
import { isAuthenticated, logout } from '../../utils/auth';
import '../../App.css';
import styles from './Home.module.css';

async function get_session_id() {
  const res = await api.post('/session/new/');
  console.log('Response:', res);
  if (res.status === 200) {
    console.log('Session created successfully');
  } else {
    throw new Error('Failed to get session ID');
  }
}

function TopBar({ onLogout }) {
  return (
    <div className="w-full bg-gray-800 p-4 flex justify-between items-center">
      <div className="text-white font-bold">DnD Dungeon Master AI</div>
      <button
        onClick={onLogout}
        className="bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm"
      >
        Logout
      </button>
    </div>
  );
}

function Home() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      setIsLoggedIn(isAuthenticated());
    };
    checkAuth();
    
    // Set up a storage event listener to detect token changes in other tabs
    const handleStorageChange = () => checkAuth();
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
  };

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
    <div className="min-h-screen bg-gray-900">
      {isLoggedIn && <TopBar onLogout={handleLogout} />}
      
      <div className="w-full flex items-center justify-center flex-col" style={{
        minHeight: isLoggedIn ? 'calc(100vh - 4rem)' : '100vh',
        paddingTop: isLoggedIn ? '0' : '0'
      }}>
        <h1 className={`text-2xl text-red-400 mb-4 text-center tracking-widest drop-shadow-lg font-UnifrakturCook ${styles.h1}`}>
          How high can you climb?
        </h1>
        <div className="flex w-full justify-between max-w-md mt-4">
          <button
            className="bg-green-800 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
            onClick={handleStartJourney}
          >
            {isLoggedIn ? 'Start Your Adventure' : 'Start your journey'}
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
