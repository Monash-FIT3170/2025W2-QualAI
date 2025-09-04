import React, { useState } from 'react';
import '../assets/styles/UploadAudioCard.css'
import { API_ENDPOINTS } from "../config/api";
import { useProject } from "../contexts/ProjectContext";

const UploadAudioCard = ({ onTranscriptionComplete }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const { activeProjectId, activeProject } = useProject();

  const handleFileChange = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const selectedFile = files[0];

      console.log('Selected file:', selectedFile.name);

      // Check if a project is selected
      if (!activeProjectId || !activeProject) {
        console.error('No project selected. Please select a project first.');
        alert('Please select a project before uploading audio.');
        return;
      }

      setIsUploading(true);
      try {
        // Create FormData object (as the endpoint expects form data)
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('project_id', activeProjectId.toString());
        formData.append('project_name', activeProject.name);

      const response = await fetch(API_ENDPOINTS.TRANSCRIBE, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Error uploading file');
      }

        // Process the JSON response from FastAPI
        const resultTranscriptionData = await response.json();

        if (onTranscriptionComplete) {
          onTranscriptionComplete(JSON.stringify(resultTranscriptionData));
        }
      } catch (error) {
        console.error('An unexpected error occurred:', error);
        alert('Upload failed. Please try again.');
      } finally {
        setIsUploading(false);
      }
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4 mb-4">
      <div className="flex flex-col items-center justify-center py-2 px-4 gap-2">
        <i className="bi bi-file-text text-6xl text-slate-400" aria-hidden="true" />
        <h3 className="text-sm font-medium text-slate-2 00 mb-1">Upload Audio</h3>
        <p className="text-xs text-slate-500 mb-3">Drag and drop or click to select</p>
        
        {/* Show current project */}
        {activeProject && (
          <p className="text-xs text-slate-400 mb-2">
            Project: {activeProject.name}
          </p>
        )}

        {/* Upload button with conditional spinner and text */}
        <label
          className={`bg-indigo-600 text-white text-sm px-4 py-2 rounded-md flex items-center gap-2 cursor-pointer transition-colors ${
            isUploading || !activeProjectId ? "opacity-50 cursor-not-allowed" : "hover:bg-indigo-700"
          }`}
          aria-label="Upload audio file"
          htmlFor="audio-upload-input"
        >
          <input
            type="file"
            id="audio-upload-input"
            className="hidden"
            accept=".mp3,.m4a,.wav,.mp4,audio/*,video/*"
            onChange={handleFileChange}
            disabled={isUploading || !activeProjectId} // Disables file selection during upload or when no project selected
          />
          {isUploading ? (
            <>
              <i className="bi bi-arrow-clockwise spin" aria-hidden="true" />
              Processing...
            </>
          ) : !activeProjectId ? (
            <>
              <i className="bi bi-exclamation-triangle" aria-hidden="true" />
              Select Project First
            </>
          ) : (
            <>
              <i className="bi bi-upload" aria-hidden="true" />
              Upload
            </>
          )}
        </label>
      </div>
    </div>
  );
};

export default UploadAudioCard;