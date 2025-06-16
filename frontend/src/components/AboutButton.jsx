import { useNavigate } from 'react-router-dom';
import BaseButton from './ui/BaseButton';

function AboutButton({ size = 'md', className = '' }) {
  const navigate = useNavigate();
  const handleClick = () => navigate('/about');

  return (
    <BaseButton
      onClick={handleClick}
      variant="secondary"
      size={size}
      className={className}
    >
      <span className="hidden sm:inline">What is it?</span>
      <span className="sm:hidden">About</span>
    </BaseButton>
  );
}

export default AboutButton;
