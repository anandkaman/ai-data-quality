import React, { useState, useRef, useEffect } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = ({ children, onLogout }) => {
  const [activeTab, setActiveTab] = useState('home');
  const mainContentRef = useRef(null);

  // Force scroll to top whenever activeTab changes
  useEffect(() => {
    // Use requestAnimationFrame to ensure DOM is updated
    requestAnimationFrame(() => {
      // Reset scroll position immediately (no smooth scroll)
      if (mainContentRef.current) {
        mainContentRef.current.scrollTo(0, 0);
        mainContentRef.current.scrollTop = 0;
      }
      
      // Also reset window scroll
      window.scrollTo(0, 0);
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    });
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gray-50 overflow-hidden">
      <Header onLogout={onLogout} />
      <div className="flex h-[calc(100vh-4rem)]">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main 
          ref={mainContentRef} 
          className="flex-1 p-8 overflow-y-auto overflow-x-hidden"
          style={{ scrollBehavior: 'auto' }}
        >
          {React.cloneElement(children, { activeTab, setActiveTab, onLogout })}
        </main>
      </div>
    </div>
  );
};

export default Layout;
