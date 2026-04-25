import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Navigation = ({ onHomeClick, onViewChange, currentView, isMobileMenuOpen, onMobileClose }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { logout, user } = useAuth();

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleLogout = () => {
    logout();
  };

  const navItems = [
    { name: 'Home', id: 'home', active: currentView === 'home' },
    { name: 'Products', id: 'top-rated', active: currentView === 'top-rated' },
    // { name: 'Trending', id: 'trending', active: currentView === 'trending' },
    // { name: 'My Watchlist', id: 'watchlist', active: currentView === 'watchlist' },
  ];

  const handleNavClick = (item) => {
    if (item.id === 'home') {
      onHomeClick();
    } else {
      onViewChange(item.id);
    }
    // Close mobile menu after selection
    if (onMobileClose) {
      onMobileClose();
    }
  };

  return (
    <>
      {/* Navigation Hover Trigger */}
      <div className="nav-trigger"></div>

      {/* Sidebar */}
      <nav className={`nav-sidebar ${isOpen ? 'active' : ''} ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
        {/* Brand */}
        <div className="nav-brand" onClick={onHomeClick}>
          <img src="/logo.png" alt="Movies Vault" />
        </div>

        {/* Navigation Menu */}
        <ul className="nav-menu">
          {navItems.map((item, index) => (
            <li key={index} className="nav-item">
              <a 
                href="#" 
                className={`nav-link ${item.active ? 'active' : ''}`}
                onClick={(e) => {
                  e.preventDefault();
                  handleNavClick(item);
                }}
              >
                {item.name}
              </a>
            </li>
          ))}
        </ul>

        {/* User Section */}
        <div style={{ marginTop: 'auto', paddingTop: '2rem' }}>
          <div className="nav-item">
            <div className="nav-link user-info">
              <div className="user-avatar">
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span>{user?.username || 'User'}</span>
            </div>
          </div>
          
          {/* Server Wake-up Button */}
          <div className="nav-item">
            <button 
              className="server-wake-btn nav-style"
              onClick={() => window.open('https://movies-vault-backend.onrender.com/', '_blank')}
              style={{ width: '100%', border: 'none', marginBottom: '0.5rem' }}
            >
              Switch On Server
            </button>
          </div>
          
          <div className="nav-item">
            <button 
              className="logout-btn"
              onClick={handleLogout}
              style={{ width: '100%', border: 'none' }}
            >
              Logout
            </button>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navigation;
