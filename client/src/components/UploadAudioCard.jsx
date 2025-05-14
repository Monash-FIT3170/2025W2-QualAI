import React from 'react';
// Remove this import: import '../assets/styles/UploadAudioCard.css';

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
    <div className="bg-slate-800 rounded-xl shadow-md p-4 mb-4">
      <div className="flex flex-col items-center justify-center py-8 px-4">
        <div className="text-2xl text-slate-400 mb-2">
          <i className="icon-cloud-upload"></i>
        </div>
        <h3 className="text-sm font-medium text-slate-200 mb-1">Upload Audio</h3>
        <p className="text-xs text-slate-500 mb-3">Drag and drop or click to select</p>
        <button 
          className="bg-blue-500 text-white text-sm px-4 py-2 rounded-md hover:bg-blue-700 flex items-center gap-2" 
          onClick={handleUpload}
        >
          Upload
        </button>
      </div>
    </div>
  );
};

export default UploadAudioCard;