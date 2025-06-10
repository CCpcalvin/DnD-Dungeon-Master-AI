import React from 'react';

function TopBar({ children }) {
  return (
    <div className="w-full bg-gray-800 p-4 flex justify-between items-center">
      {children}
    </div>
  );
}

export default TopBar;