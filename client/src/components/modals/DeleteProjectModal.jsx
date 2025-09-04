import React, { useState } from "react";
import { API_BASE } from '../../config/api.jsx';
import { useProject } from '../../contexts/ProjectContext';

/**
 * Modal component for deleting a project
 * @param {Object} props - Component props
 * @param {Function} props.onClose - Function to close the modal
 * @param {Function} props.onDelete - Optional callback to update parent after deletion
 */
const DeleteProjectModal = ({ onClose, onDelete }) => {
  const [loading, setLoading] = useState(false);
  const { projects, activeProjectId, setActiveProjectId, loadProjects } = useProject();

  const canDelete = projects.length > 1;
  const projectId = activeProjectId;

  const handleDelete = async (e) => {
    e.preventDefault();
    if (!canDelete) {
      alert("You cannot delete the only remaining project.");
      return;
    }
    if (!projectId) {
      alert("No active project selected.");
      return;
    }
    setLoading(true);

    // Pick a next active project deterministically (prefer neighbor, else first available)
    const currentIndex = projects.findIndex(p => p.project_id === projectId);
    const candidates = projects.filter(p => p.project_id !== projectId);
    const preferred = candidates[currentIndex] || candidates[currentIndex - 1] || candidates[0];
    const nextActiveId = preferred?.project_id ?? null;

    try {
      const res = await fetch(`${API_BASE}/projects/${projectId}`, {
        method: "DELETE",
      });
      const data = await res.json();

      if (!res.ok || data.error) {
        throw new Error(data.error || "Failed to delete project");
      }

      // Remove chat thread for the deleted project
      try {
        localStorage.removeItem(`aiMessages_${projectId}`);
      } catch {}

      // Switch active project locally (immediately) then refresh list
      if (nextActiveId) {
        setActiveProjectId(nextActiveId);
      }
      await loadProjects();

      onDelete?.(projectId);
      onClose();
    } catch (err) {
      console.error(err);
      alert(err.message || "An error occurred while deleting the project");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/75 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-xl shadow-xl max-w-md w-full mx-4">
        <div className="flex justify-between items-center p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">
            Delete Current Project
          </h2>
          <button
            className="text-slate-400 hover:text-white transition-colors"
            onClick={onClose}
            aria-label="Close modal"
          >
            <i className="bi bi-times"></i>
          </button>
        </div>

        <form className="p-6" onSubmit={handleDelete}>
          <div className="mb-4">
            <p className="text-sm text-slate-200">
              Are you sure you wish to delete this project forever?
            </p>
            {!canDelete && (
              <p className="text-xs text-red-400 mt-2">
                You must have at least one project. Deletion is disabled when only one project remains.
              </p>
            )}
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
              disabled={loading || !canDelete}
            >
              {loading ? "Deleting..." : "Delete"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DeleteProjectModal;