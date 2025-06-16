import React from 'react';

const sizeClasses = {
  sm: 'py-1 px-3 text-sm',
  md: 'py-2 px-4 text-sm',
  lg: 'py-3 px-6 text-base',
};

const variantClasses = {
  primary: 'bg-green-700 hover:bg-green-600',
  secondary: 'bg-blue-700 hover:bg-blue-600',
  danger: 'bg-red-700 hover:bg-red-600',
  ghost: 'bg-transparent hover:bg-gray-700',
};

const BaseButton = ({
  children,
  onClick,
  size = 'md',
  variant = 'primary',
  className = '',
  type = 'button',
  ...props
}) => {
  const sizeClass = sizeClasses[size] || sizeClasses.md;
  const variantClass = variantClasses[variant] || variantClasses.primary;

  return (
    <button
      type={type}
      onClick={onClick}
      className={`
        ${sizeClass}
        ${variantClass}
        text-white font-medium rounded-md transition-colors
        flex items-center justify-center whitespace-nowrap
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
};

export default BaseButton;
