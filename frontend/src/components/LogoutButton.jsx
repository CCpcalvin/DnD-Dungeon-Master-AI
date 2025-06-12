import { useNavigate } from 'react-router-dom';

function LogoutButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate('/logout')}
      className="bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm"
    >
      Logout
    </button>
  )
}

export default LogoutButton;

