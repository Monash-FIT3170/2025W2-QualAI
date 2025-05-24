const UploadAudioCard = () => {

  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4 mb-4">
      <div className="flex flex-col items-center justify-center py-2 px-4 gap-2">
        <div className="text-2xl text-slate-400 mb-2">
          <i className="icon-cloud-upload"></i>
        </div>
        
        <i className="bi bi-file-text text-6xl" />
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