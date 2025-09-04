import React, { useState } from 'react';
import '../assets/styles/UploadAudioCard.css'
import { API_ENDPOINTS } from "../config/api";

const UploadAudioCard = ({ onTranscriptionComplete }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const selectedFile = files[0];
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(API_ENDPOINTS.TRANSCRIBE, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Error uploading file');
      }

      // Prefer JSON from API: { filename, transcription }
      let dataObj = null;
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        dataObj = await response.json();
      } else {
        // Fallback: treat response as raw HTML/text and wrap it
        const raw = await response.text();
        dataObj = {
          filename: selectedFile.name.replace(/\.[^/.]+$/, '') + '.html',
          transcription: raw
        };
      }

      onTranscriptionComplete?.(dataObj);
    } catch (error) {
      console.error('An unexpected error occurred:', error);
      alert(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
      // reset input so same file can be chosen again if needed
      e.target.value = '';
    }
  };

  







  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4 mb-4">
      <div className="flex flex-col items-center justify-center py-2 px-4 gap-2">
        <i className="bi bi-file-text text-6xl text-slate-400" aria-hidden="true" />
        <h3 className="text-sm font-medium text-slate-2 00 mb-1">Upload Audio</h3>
        <p className="text-xs text-slate-500 mb-3">Drag and drop or click to select</p>
        <label
          className={`bg-indigo-600 text-white text-sm px-4 py-2 rounded-md flex items-center gap-2 cursor-pointer transition-colors ${
            isUploading ? "opacity-50 cursor-not-allowed" : "hover:bg-indigo-700"
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
            disabled={isUploading}
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