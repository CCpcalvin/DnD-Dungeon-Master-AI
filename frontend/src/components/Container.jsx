import React from 'react';

function Container({ children }) {
  return (
    <div className="container mx-auto p-4 max-w-4xl">
      {children}
    </div>
  );
}

export default Container;
