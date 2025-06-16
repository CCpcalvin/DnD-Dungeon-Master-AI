import React from 'react';

function Footer() {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-900 text-gray-400 py-4 text-center text-sm border-t border-gray-800">
      <div className="container mx-auto px-4">
        <p>© {currentYear} DnD Dungeon Master AI by CCpcalvin. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;
