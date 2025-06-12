import React from 'react';
import Container from './Container';

function TopBar({ children }) {
  return (
    <Container>
      <div className="w-full bg-gray-800 p-4 flex justify-between items-center rounded-lg mt-4">
        {children}
      </div>
    </Container>
  );
}

export default TopBar;