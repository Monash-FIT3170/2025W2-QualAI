import React, { useState } from "react";
import { API_BASE } from '../../config/api.jsx';

/**
 * Modal component for deleting a project
 * @param {Object} props - Component props
 * @param {number} props.projectId - ID of the project to delete
 * @param {Function} props.onClose - Function to close the modal
 * @param {Function} props.onDelete - Optional callback to update parent after deletion
 */
const DeleteProjectModal = ({ projectId, onClose, onDelete }) => {
  const [loading, setLoading] = useState(false);

  const handleDelete = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/projects/${projectId}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (data.ok) {
        if (onDelete) onDelete(projectId); // Notify parent
        onClose();
      } else {
        alert(data.error || "Failed to delete project");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred while deleting the project");
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
              disabled={loading}
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
