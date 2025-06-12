import { useNavigate } from 'react-router-dom';

function HomeButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate('/')}
      className="text-white hover:text-gray-300 flex items-center font-bold"
    >
      Home
    </button>
  );
}

export default HomeButton;
