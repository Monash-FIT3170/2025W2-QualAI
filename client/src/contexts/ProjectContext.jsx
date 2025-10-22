import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { API_ENDPOINTS } from '../config/api';

const ProjectContext = createContext();

export const useProject = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
};

export const ProjectProvider = ({ children }) => {
  const [projects, setProjects] = useState([]);
  const [activeProjectId, setActiveProjectId] = useState(
    () => Number(localStorage.getItem('activeProjectId')) || null 
  );
  const [loading, setLoading] = useState(true);

  const loadProjects = useCallback(async () => {
    try {
      const res = await fetch(API_ENDPOINTS.PROJECT);
      const data = await res.json();
      setProjects(data);

      if (!activeProjectId && data.length > 0) {
        const savedId = Number(localStorage.getItem('activeProjectId'));
        const savedProject = data.find(p => p.project_id === savedId);
        setActiveProjectId(savedProject ? savedProject.project_id : data[0].project_id);
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  }, [activeProjectId]);

  useEffect(() => {
    if (activeProjectId !== null) {
      localStorage.setItem('activeProjectId', activeProjectId);
    }
  }, [activeProjectId]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const createProject = async (projectData) => {
    try {
      const res = await fetch(API_ENDPOINTS.PROJECT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(projectData),
      });
      const data = await res.json();
      if (res.ok) {
        await loadProjects(); // refresh list
        return data;
      }
      throw new Error(data.error || 'Failed to create project');
    } catch (error) {
      console.error('Failed to create project:', error);
      throw error;
    }
  };

  const value = {
    projects,
    activeProjectId,
    setActiveProjectId,
    loadProjects,
    createProject,
    loading,
    activeProject: projects.find(p => p.project_id === activeProjectId) || null,
  };

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
};

export default ProjectContext;