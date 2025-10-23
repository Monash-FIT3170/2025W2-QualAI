import { useState, useEffect, forwardRef, useImperativeHandle } from "react";

const ProjectDetail = forwardRef(({ project }, ref) => {
  const [projectName, setProjectName] = useState(project?.name || "");
  const [projectDescription, setProjectDescription] = useState(project?.description || "");
  const [message, setMessage] = useState("");

  useEffect(() => {
    setProjectName(project?.name || "");
    setProjectDescription(project?.description || "");
  }, [project]);

  // expose save method to parent via ref
  useImperativeHandle(ref, () => ({
    async saveProject() {
      try {
        const response = await fetch(`/projects/${project.project_id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: projectName,
            description: projectDescription,
          }),
        });

        if (!response.ok) {
          setMessage("Failed to update project. 😔");
        } else {
          project.name = projectName; // just to show changes without having to refresh backend
          project.description = projectDescription;
          setMessage("✨ Project updated successfully! ✨");
        }
      } catch (error) {
        console.log(`Error: ${error.message || JSON.stringify(error)}`);
      }
    },
  }));

  useEffect(() => {
    if (message) {
      const timeout = setTimeout(() => setMessage(""), 3000);
      return () => clearTimeout(timeout);
    }
  }, [message]);

  return (
    <div className="bg-slate-700 p-6 rounded-lg">
      <h2 className="text-xl font-semibold text-slate-200 mb-4">
        Basic Information
      </h2>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Project Name
        </label>
        <input
          type="text"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          className="bg-slate-600 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter project name"
        />
      </div>

      <div
        style={{
          maxHeight: '20rem',
          overflowY: 'auto',
          paddingRight: '0.5rem',
          scrollbarWidth: 'thin',
          scrollbarColor: 'rgba(148,163,184,0.6) transparent',
        }}
        className="space-y-3"
      >
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Description
        </label>
        <textarea
          value={projectDescription}
          onChange={(e) => setProjectDescription(e.target.value)}
          rows={4}
          className="bg-slate-600 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical"
          placeholder="Enter project description"
        />
      </div>

      {message && <p className="mt-3 text-sm text-gray-200">{message}</p>}
    </div>
  );
});

export default ProjectDetail;
