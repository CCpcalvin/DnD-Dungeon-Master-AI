import { useNavigate } from 'react-router-dom';
import BaseButton from './ui/BaseButton';

function LoginRegisterButton({ size = 'md', className = '' }) {
  const navigate = useNavigate();
  const handleClick = () => navigate('/login');

  return (
    <BaseButton
      onClick={handleClick}
      variant="primary"
      size={size}
      className={`whitespace-nowrap ${className}`}
    >
      Login / Register
    </BaseButton>
  );
}

export default LoginRegisterButton;
