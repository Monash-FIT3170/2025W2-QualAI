import React, { useState, useEffect } from "react";

const ProjectDetail = ({ project }) => {
  const [projectName, setProjectName] = useState(project?.name || "");
  const [projectDescription, setProjectDescription] = useState(project?.description || "");

  useEffect(() => {
    setProjectName(project?.name || "");
    setProjectDescription(project?.description || "");
  }, [project]);

  return (
    <div className="bg-slate-700 p-6 rounded-lg">
      <h2 className="text-xl font-semibold text-slate-200 mb-4">
        Basic Information
      </h2>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Project Name
        </label>
        <input
          type="text"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          className="bg-slate-600 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter project name"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          value={projectDescription}
          onChange={(e) => setProjectDescription(e.target.value)}
          rows={4}
          className="bg-slate-600 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
          placeholder="Enter project description"
        />
      </div>
    </div>
  );
};

export default ProjectDetail;
