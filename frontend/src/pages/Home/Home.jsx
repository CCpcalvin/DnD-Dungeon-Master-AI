import '../../App.css'
import styles from './Home.module.css'
import { useNavigate } from 'react-router-dom'
import api from '../../api'


async function get_session_id() {
  const res = await api.post('/session/new/')
  console.log('Response:', res);
  if (res.status === 200) {
    console.log('Session created successfully');
    // console.log('Session ID:', res.data.session_id);
  } else {
    throw new Error('Failed to get session ID');
  }
}


function Home() {
  const navigate = useNavigate();

  return (
    <div className="w-screen flex items-center justify-center flex-col">
      <h1 className={`text-2xl text-red-400 mb-4 text-center tracking-widest drop-shadow-lg font-UnifrakturCook ${styles.h1}`}>
        How high can you climb?
      </h1>
      <div className="flex w-full justify-between max-w-md mt-4">
        <button
          className="bg-green-800 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
          onClick={() => get_session_id()}
        >
          Start your journey
        </button>
        <button className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded"
          onClick={() => navigate('/login')}>
          Login / Register
        </button>
      </div>
    </div >
  );
}


export default Home;
