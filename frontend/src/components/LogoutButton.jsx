import { useNavigate } from 'react-router-dom';
import BaseButton from './ui/BaseButton';

function LogoutButton({ size = 'md', className = '' }) {
  const navigate = useNavigate();
  const handleClick = () => navigate('/logout');

  return (
    <BaseButton
      onClick={handleClick}
      variant="danger"
      size={size}
      className={className}
    >
      Logout
    </BaseButton>
  );
}

export default LogoutButton;

