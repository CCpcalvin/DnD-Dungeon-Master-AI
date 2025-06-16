import { useNavigate } from 'react-router-dom';
import BaseButton from './ui/BaseButton';

function HomeButton({ size = 'md', className = '' }) {
  const navigate = useNavigate();
  const handleClick = () => navigate('/');

  return (
    <BaseButton
      onClick={handleClick}
      variant="ghost"
      size={size}
      className={`hover:bg-opacity-20 ${className}`}
    >
      Home
    </BaseButton>
  );
}

export default HomeButton;
