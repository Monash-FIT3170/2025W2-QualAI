const UploadAudioCard = () => {

  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4 mb-4">
      <div className="flex flex-col items-center justify-center py-2 px-4 gap-2">
        <div className="text-2xl text-slate-400 mb-2">
          <i className="icon-cloud-upload"></i>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" fill="white" className="text-white mb-2" viewBox="0 0 16 16"> 
          <path d="M5 4a.5.5 0 0 0 0 1h6a.5.5 0 0 0 0-1zm-.5 2.5A.5.5 0 0 1 5 6h6a.5.5 0 0 1 0 1H5a.5.5 0 0 1-.5-.5M5 8a.5.5 0 0 0 0 1h6a.5.5 0 0 0 0-1zm0 2a.5.5 0 0 0 0 1h3a.5.5 0 0 0 0-1z"/>
          <path d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2zm10-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1"/>
        </svg>
        <h3 className="text-sm font-medium text-slate-200 mb-1">Upload Audio</h3>
        <p className="text-xs text-slate-500 mb-3">Drag and drop or click to select</p>
        <label 
          className="bg-indigo-600 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center gap-2" 
        >
          <input type="file" className="hidden"/>
            <i className="bi bi-upload"/>
            Upload
        </label>
      </div>
    </div>
  );
};

export default UploadAudioCard;