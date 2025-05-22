import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Logo from '../assets/images/logo.png';
import NewProjectModal from './modals/NewProjectModal';

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
  <nav className="bg-slate-800 border-b border-slate-700 py-2">
    <div className="flex justify-between items-center max-w-[1600px] mx-auto px-4 h-16">
      <div className="flex items-center">
        <img src={Logo} alt="QualAI" className="h-8 w-auto" />
        <span className="ml-2 text-xl font-bold text-white">QualAI</span>
      </div>
      
      <div className="flex items-center">
        <div className="flex bg-slate-700 rounded-md mr-2 p-1 ml-[5px]">
          <Link 
            to="/" 
            className="px-4 py-2 rounded-md no-underline text-sm font-medium bg-indigo-600 text-white"
          >
            Project 1
          </Link>
        </div>
        
        <button 
          className="flex items-center px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
          onClick={openProjectFile}
        >
          <i className="bi bi-folder2-open mr-2"></i> Open Project
        </button>
      </div>
      
      <div className="flex items-center gap-4">
        <button 
          className="flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors"
          onClick={() => setShowModal(true)}
        >
          <i className="bi bi-plus mr-2"></i> New Project
        </button>
        
        <div className="flex items-center px-3 py-1 bg-green-50 text-green-800 rounded-full text-xs font-medium">
          <span className="h-2 w-2 bg-green-500 rounded-full mr-2"></span>
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