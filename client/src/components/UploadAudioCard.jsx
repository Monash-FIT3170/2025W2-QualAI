import React, { useState } from 'react';
import '../assets/styles/UploadAudioCard.css'

const UploadAudioCard = ({ onTranscriptionComplete }) => {
  const [isUploading, setIsUploading] = useState(false);

  /**
   * Handles file selection
   * @param {React.ChangeEvent<HTMLInputElement>} e - File input change event
   */
  const handleFileChange = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const selectedFile = files[0];

      console.log('Selected file:', selectedFile.name);

      setIsUploading(true);
      try {
        // Create FormData object (as the endpoint expects form data)
        const formData = new FormData();
        formData.append('file', selectedFile);

        // POST request to FastAPI endpoint
        const response = await fetch("http://localhost:8000/transcribe/", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || 'Error uploading file');
        }

        // Process the HTML response from FastAPI
        const resultTranscriptionData = await response.text();

        if (onTranscriptionComplete) {
          onTranscriptionComplete(resultTranscriptionData);
        }
      } catch (error) {
        console.error('An unexpected error occurred:', error);
      } finally {
        setIsUploading(false);
      }
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4 mb-4">
      <div className="flex flex-col items-center justify-center py-2 px-4 gap-2">
        {/* File icon */}
        <i className="bi bi-file-text text-6xl text-slate-400" aria-hidden="true" />

        {/* Title and instructions */}
        <h3 className="text-sm font-medium text-slate-200 mb-1">Upload Audio</h3>
        <p className="text-xs text-slate-500 mb-3">Drag and drop or click to select</p>

        {/* Upload button with conditional spinner and text */}
        <label
          className={`bg-indigo-600 text-white text-sm px-4 py-2 rounded-md flex items-center gap-2 cursor-pointer transition-colors ${
            isUploading ? "opacity-50 cursor-not-allowed" : "hover:bg-indigo-700"
          }`}
          aria-label="Upload audio file"
          htmlFor="audio-upload-input"
        >
          {/* Hidden file input */}
          <input
            type="file"
            id="audio-upload-input"
            className="hidden"
            accept="audio/*"
            onChange={handleFileChange}
            disabled={isUploading} // Disables file selection during upload
          />
          {isUploading ? (
            <>
              <i className="bi bi-arrow-clockwise spin" aria-hidden="true" />
              Processing...
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