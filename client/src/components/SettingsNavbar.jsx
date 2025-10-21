import { useState } from 'react';
import Logo from '../assets/images/logo.png';
import { useEffect } from 'react';
import { useProject } from '../contexts/ProjectContext';
import { useNavigate } from 'react-router-dom';


/**
 * Main navigation bar component
 * Handles project navigation and creation
 */
const SettingsNavbar = () => {
  // State for controlling modal visibility
  const [showModal, setShowModal] = useState(false);
  const [status, setStatus] = useState("booting");
  const navigate = useNavigate();

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
        </div>
        
   

        {/* Action buttons section */}
        <div className="flex items-center gap-4">
            <div>
                <button
                    onClick={() => navigate(-1)}
                    className="flex items-center justify-center p-3 rounded-lg text-white transition hover:bg-indigo-700"
                    >

                    <svg
                        fill="currentColor"
                        xmlns="http://www.w3.org/2000/svg"
                        width="25px"
                        height="25px"
                        viewBox="0 0 52 52"
                    >
                        <path d="M30.3,12.6c10.4,0,18.9,8.4,18.9,18.9s-8.5,18.9-18.9,18.9h-8.2c-0.8,0-1.3-0.6-1.3-1.4v-3.2
                        c0-0.8,0.6-1.5,1.4-1.5h8.1c7.1,0,12.8-5.7,12.8-12.8s-5.7-12.8-12.8-12.8H16.4c0,0-0.8,0-1.1,0.1c-0.8,0.4-0.6,1,0.1,1.7l4.9,4.9
                        c0.6,0.6,0.5,1.5-0.1,2.1L18,29.7c-0.6,0.6-1.3,0.6-1.9,0.1l-13-13c-0.5-0.5-0.5-1.3,0-1.8L16,2.1c0.6-0.6,1.6-0.6,2.1,0l2.1,2.1
                        c0.6,0.6,0.6,1.6,0,2.1l-4.9,4.9c-0.6,0.6-0.6,1.3,0.4,1.3c0.3,0,0.7,0,0.7,0L30.3,12.6z"/>
                    </svg>

                    </button>
            </div>

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
      

    </nav>
  );
};

export default SettingsNavbar;