import React from 'react';
import '../assets/styles/UploadAudioCard.css';

const UploadAudioCard = () => {
  const handleUpload = () => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'audio/*';
    fileInput.style.display = 'none';
    
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        console.log('Selected audio file:', file.name);
        // Handle the selected audio file
      }
    });
    
    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);
  };

  return (
    <div className="upload-audio-card">
      <div className="upload-content">
        <div className="upload-icon">
          <i className="icon-cloud-upload"></i>
        </div>
        <h3 className="upload-title">Upload Audio</h3>
        <p className="upload-description">Drag and drop or click to select</p>
        <button className="btn btn-primary btn-sm" onClick={handleUpload}>
          <i className="icon-upload"></i> Upload
        </button>
      </div>
    </div>
  );
};

export default UploadAudioCard;