import React from 'react';

export const ActionPromptButton = ({
  action,
  index,
  disabled = false,
  onClick,
  className = '',
}) => {
  // Common button styles
  const getButtonClasses = () => {
    const baseClasses = 'text-left px-3 py-1 rounded';
    const stateClasses = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';
    const colorClasses = 'bg-gray-700 hover:bg-gray-600';

    return `${baseClasses} ${stateClasses} ${colorClasses} ${className}`.trim();
  };

  const handleClick = (e) => {
    if (disabled) return;
    e.preventDefault();
    e.stopPropagation();
    onClick?.(e);
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={getButtonClasses()}
    >
      {typeof index === 'number' ? `${index + 1}. ` : ''}{action}
    </button>
  );
};

export default ActionPromptButton;
