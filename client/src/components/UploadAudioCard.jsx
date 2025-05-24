/**
 * UploadAudioCard Component
 * 
 * Provides a drag-and-drop interface for uploading audio files for transcription.
 * Handles file selection and initiates the upload process.
 */
const UploadAudioCard = () => {
  // const [selectedFile, setSelectedFile] = useState(null);
  // const [isUploading, setIsUploading] = useState(false);

  /**
   * Handles file selection
   * @param {React.ChangeEvent<HTMLInputElement>} e - File input change event
   */
  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const selectedFile = files[0];
      console.log('Selected file:', selectedFile.name);
      // TODO: Implement file validation and upload logic
    }
  };

  return (
    /* Main card container */
    <div className="bg-slate-800 rounded-xl shadow-md p-4 mb-4">
      {/* Content container with centered items */}
      <div className="flex flex-col items-center justify-center py-2 px-4 gap-2">
        {/* Upload icon (commented out as it's not working - using bi icon instead) */}
        {/* <div className="text-2xl text-slate-400 mb-2">
          <i className="icon-cloud-upload"></i>
        </div> */}
        
        {/* File icon */}
        <i className="bi bi-file-text text-6xl text-slate-400" aria-hidden="true" />
        
        {/* Title and instructions */}
        <h3 className="text-sm font-medium text-slate-200 mb-1">Upload Audio</h3>
        <p className="text-xs text-slate-500 mb-3">Drag and drop or click to select</p>
        
        {/* File upload input (hidden) with styled label as button */}
        <label 
          className="bg-indigo-600 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center gap-2 cursor-pointer transition-colors"
          aria-label="Upload audio file"
          htmlFor="audio-upload-input"
        >
          {/* Hidden file input */}
          <input 
            type="file"
            id="audio-upload-input"
            className="hidden"
            accept="audio/*"  // Accept all audio formats
            onChange={handleFileChange}
          />
          <i className="bi bi-upload" aria-hidden="true"/>
          Upload
        </label>
      </div>
    </div>
  );
};

export default UploadAudioCard;