import React from 'react';
import '../assets/styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="status-indicators">
          <span className="status-item">
            <i className="icon-database"></i> Database Connected
          </span>
          <span className="status-item">
            <i className="icon-brain"></i> AI Model Ready
          </span>
        </div>
        
        <div className="storage-indicator">
          <span className="storage-text">Storage: 45% used</span>
          <div className="storage-bar">
            <div className="storage-used" style={{ width: '45%' }}></div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;