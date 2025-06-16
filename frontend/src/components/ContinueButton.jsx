import { useNavigate } from 'react-router-dom';
import BaseButton from './ui/BaseButton';

function ContinueButton({ size = 'md', className = '', collapsible = true }) {
  const navigate = useNavigate();
  const handleClick = () => navigate('/my-sessions');

  return (
    <BaseButton
      onClick={handleClick}
      variant="ghost"
      size={size}
      className={`hover:bg-opacity-20 ${className}`}
    >
      {collapsible ? (
        <>
          <span className="hidden sm:inline">Continue Your Journey</span>
          <span className="sm:hidden">Continue</span>
        </>
      ) : (
        <span>Continue Your Journey</span>
      )}
    </BaseButton>
  );
}

export default ContinueButton;
