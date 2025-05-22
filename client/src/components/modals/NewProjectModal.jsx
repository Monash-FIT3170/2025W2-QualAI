import React, { useState } from 'react';

const NewProjectModal = ({ onClose }) => {
  const [formData, setFormData] = useState({
    projectName: '',
    projectDescription: '',
    researchMethod: 'thematic'
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    // Handle project creation
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/75 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-xl shadow-xl max-w-md w-full mx-4">
        <div className="flex justify-between items-center p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">Create New Project</h2>
          <button 
            className="text-slate-400 hover:text-white transition-colors"
            onClick={onClose}
          >
            <i className="bi bi-times"></i>
          </button>
        </div>
        
        <form className="p-6" onSubmit={handleSubmit}>
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
              required
            />
          </div>
          
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
            ></textarea>
          </div>
          
          <div className="flex justify-end gap-3 mt-6">
            <button 
              type="button" 
              className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              onClick={onClose}
            >
              Cancel
            </button>
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