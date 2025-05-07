import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Logo from '../assets/images/logo.png';
import NewProjectModal from './modals/NewProjectModal';
import '../assets/styles/NavBar.css';

const NavBar = () => {
  const [showModal, setShowModal] = useState(false);

  const openProjectFile = () => {
    // Create a hidden file input element
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json,.xml,.txt,.csv';
    fileInput.style.display = 'none';
    
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        console.log('Selected file:', file.name);
        // Handle the selected project file
      }
    });
    
    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <img src={Logo} alt="QualAI" className="navbar-logo" />
          <span className="navbar-title">QualAI</span>
        </div>
        
        <div className="navbar-links">
          <div className="project-tabs">
            <Link to="/" className="project-tab active">Project 1</Link>
          </div>
          
          <button className="btn btn-secondary" onClick={openProjectFile}>
            <i className="icon-folder-open"></i> Open Project
          </button>
        </div>
        
        <div className="navbar-actions">
          <button 
            className="btn btn-primary" 
            onClick={() => setShowModal(true)}
          >
            <i className="icon-plus"></i> New Project
          </button>
          
          <div className="system-status">
            <span className="status-indicator"></span>
            System Online
          </div>
        </div>
      </div>
      
      {showModal && (
        <NewProjectModal onClose={() => setShowModal(false)} />
      )}
    </nav>
  );
};

export default NavBar;