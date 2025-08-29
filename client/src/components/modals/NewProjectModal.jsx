import React, { useState } from 'react';
import { API_BASE } from '../../config/api.jsx';


/**
 * Modal component for creating a new project
 * @param {Object} props - Component props
 * @param {Function} props.onClose - Function to close the modal
 */
const NewProjectModal = ({ onClose }) => {
  // State to manage form data
  const [formData, setFormData] = useState({
    projectName: '',          // Stores project name input
    projectDescription: '',   // Stores project description
    researchMethod: 'thematic' // Default research method selection
  });

  /**
   * Handles changes in form inputs
   * @param {Object} e - Event object from input change
   */
  const handleChange = (e) => {
    setFormData({
      ...formData,            
      [e.target.name]: e.target.value 
    });
  };

  /**
   * Handles form submission
   * @param {Object} e - Event object from form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
  
    try {
      const res = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.projectName,
          description: formData.projectDescription,
        }),
      });
  
      const data = await res.json();
  
      if (!res.ok || data.error) {
        throw new Error(data.error || 'Failed to create project');
      }
  
      onClose(); 
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };
  

  return (
    <div className="fixed inset-0 bg-slate-900/75 flex items-center justify-center z-50">
      {/* Modal container */}
      <div className="bg-slate-800 rounded-xl shadow-xl max-w-md w-full mx-4">
        {/* Modal header with title and close button */}
        <div className="flex justify-between items-center p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">Create New Project</h2>
          {/* Close button */}
          <button 
            className="text-slate-400 hover:text-white transition-colors"
            onClick={onClose}
            aria-label="Close modal"
          >
            <i className="bi bi-times"></i>
          </button>
        </div>
        
        {/* Form section */}
        <form className="p-6" onSubmit={handleSubmit}>
          {/* Project Name input field */}
          <div className="mb-4">
            <label 
              htmlFor="projectName" 
              className="block text-sm font-medium text-slate-200 mb-1"
            >
              Project Name
            </label>
            <input
              type="text"
              id="projectName"
              name="projectName"
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-600"
              value={formData.projectName}
              onChange={handleChange}
              required            // Field is required
              placeholder="Enter project name"
            />
          </div>
          
          {/* Project Description textarea */}
          <div className="mb-4">
            <label 
              htmlFor="projectDescription" 
              className="block text-sm font-medium text-slate-200 mb-1"
            >
              Description
            </label>
            <textarea
              id="projectDescription"
              name="projectDescription"
              rows="3"
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-600"
              value={formData.projectDescription}
              onChange={handleChange}
              placeholder="Briefly describe your project"
            ></textarea>
          </div>
          
          {/* Form action buttons */}
          <div className="flex justify-end gap-3 mt-6">
            {/* Cancel button */}
            <button 
              type="button" 
              className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              onClick={onClose}
            >
              Cancel
            </button>
            {/* Submit button */}
            <button 
              type="submit" 
              className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Create Project
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewProjectModal;