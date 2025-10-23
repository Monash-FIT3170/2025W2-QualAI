import React, { useState } from 'react';
import Logo from '../assets/images/logo.png';
import NewProjectModal from './modals/NewProjectModal';
import { useEffect } from 'react';
import { useRef } from 'react';
import { useProject } from '../contexts/ProjectContext';
import DeleteProjectModal from './modals/DeleteProjectModal';


/**
 * Main navigation bar component
 * Handles project navigation and creation
 */
const NavBar = () => {
  // State for controlling modal visibility
  const [showModal, setShowModal] = useState(false);
  const [status, setStatus] = useState("booting");

useEffect(() => {
  let intervalId;

  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:8000/status");
      const data = await res.json();
      setStatus(data.status);
    } catch {
      setStatus("booting"); // fallback if server unreachable
    }
  };

  if (status === "online") {
    intervalId = setInterval(fetchStatus, 60000); // 1 min after the boot
  } else {
    intervalId = setInterval(fetchStatus, 2000); // 2 sec on system startup
  }

  fetchStatus();

  return () => clearInterval(intervalId);
}, [status]);

  const statusConfig = {
    online: {
      text: "System Online",
      classes: "bg-green-50 text-green-800",
      dot: "bg-green-500"
    },
    booting: {
      text: "System Booting",
      classes: "bg-yellow-50 text-yellow-800",
      dot: "bg-yellow-500 animate-pulse"
    }
  };

  const { text: statusText, classes: statusClasses, dot: dotColor } =
    statusConfig[status] || statusConfig.booting;
  
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const { projects, activeProjectId, setActiveProjectId, loadProjects } = useProject();

  const activeProject = projects.find(p => p.project_id === activeProjectId);



  /**
   * Handles opening project files
   * Creates a hidden file input element programmatically
   */
  const openProjectFile = () => { 
    // Create a hidden file input element
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json,.xml,.txt,.csv'; 
    fileInput.style.display = 'none';
    
    // Handle file selection
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        console.log('Selected file:', file.name);
        // TODO: Add actual file handling logic here
      }
    });
    
    // Trigger file dialog
    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);  // Clean up
  };

  return (
    <nav className="bg-slate-800 border-b border-slate-700 py-2">
      {/* Inner container with max-width and centering */}
      <div className="flex justify-between items-center max-w-[1600px] mx-auto px-4 h-16">
        {/* Logo/branding section */}
        <div className="flex items-center">
          <img 
            src={Logo} 
            alt="QualAI" 
            className="h-8 w-auto" 
            aria-hidden="true"
          />
          <span className="ml-2 text-xl font-bold text-white">QualAI</span>

          {/* Current Project Badge */}
          <div
            className="ml-4 hidden sm:flex items-center gap-2 px-3 py-1 rounded-md border border-slate-700 bg-slate-700/40"
            title={
              activeProject
                ? (activeProject.description || activeProject.name)
                : "No project selected"
            }
            aria-label="Current project"
          >
            <i className="bi bi-folder2" aria-hidden="true" />
            {activeProject ? (
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-semibold text-white leading-tight truncate max-w-[240px]">
                  Currently working on: {activeProject.name}
                </span>
                <span className="text-xs text-slate-300 leading-tight truncate max-w-[320px] md:block">
                  {activeProject.description || "No description"}
                </span>
              </div>
            ) : (
              <span className="text-sm text-slate-300">No project selected</span>
            )}
          </div>


        </div>
        
        {/* Project navigation section */}
        <div className="flex items-center">
          {/* Project selector pill */}
          <div className="flex bg-slate-700 rounded-md mr-2 p-1 ml-[5px] gap-2">
            {projects.length === 0 && (
              <span className="px-3 py-2 text-sm text-slate-300">No projects yet</span>
            )}
            {projects.map((p) => (
              <button
                key={p.project_id}
                onClick={() => setActiveProjectId(p.project_id)}
                className={
                  "px-4 py-2 rounded-md text-sm font-medium transition-colors " +
                  (activeProjectId === p.project_id
                    ? "bg-indigo-600 text-white hover:bg-indigo-700"
                    : "bg-slate-600 text-white/80 hover:bg-slate-500")
                }
                title={p.description || ""}
              >
                {p.name}
              </button>
            ))}
          </div>

          
          {/* Open project button */}
          <button 
            className="flex items-center px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
            onClick={openProjectFile}
            aria-label="Open project file"
          >
            <i className="bi bi-folder2-open mr-2" aria-hidden="true"/>
            Open Project
          </button>
        </div>
        
        {/* Action buttons section */}
        <div className="flex items-center gap-4">
           {/* Delete project button */}
          <button
            className="flex items-center p-2 text-white text-sm font-medium rounded-md transition-colors hover:text-red-600"
            onClick={() => setShowDeleteModal(true)}
            aria-label="Delete project"
          >
            <i className="bi bi-trash text-xl" aria-hidden="true" />
          </button>
          {/* New project button */}
          <button 
            className="flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors"
            onClick={() => setShowModal(true)}
            aria-label="Create new project"
          >
            <i className="bi bi-plus mr-2" aria-hidden="true"/>
            New Project
          </button>
          
          {/* System status indicator */}
          <div
            className={`flex items-center px-3 py-1 rounded-full text-xs font-medium ${statusClasses}`}
            role="status"
            aria-live="polite"
          >
            <span className={`h-2 w-2 rounded-full mr-2 ${dotColor}`}></span>
            {statusText}
          </div>

        </div>
      </div>
      
      {/* Conditionally render New Project modal
      {showModal && (
        <NewProjectModal onClose={() => setShowModal(false)} />
      )} */}

      {/*this reloads list of projects when a project is created*/}
      {showModal && (
        <NewProjectModal
        onClose={() => setShowModal(false)}
        onCreated={() => loadProjects()}  // refresh after create
        />
      )}

      {showDeleteModal && (
        <DeleteProjectModal
          projectId={activeProjectId} 
          onClose={() => setShowDeleteModal(false)}
          onDelete={() => {
            loadProjects(); // refresh project list after deletion
            setActiveProjectId(null); 
          }}
        />
      )}

    </nav>
  );
};

export default NavBar;