const TranscriptionSection = () => {
  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4 flex-1 flex flex-col">
      <div className="flex justify-between items-center mb-2 font-sora">
        <h3 className="text-lg text-white font-bold">Transcription</h3>
          <div className='flex gap-3'>
            <button 
              className="bg-indigo-600 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center gap-2" 
              //onClick={editTranscription} // editing/highlighting transcriptions will be implemented later.
            >
              <i className="bi bi-pencil" />
            </button>

            <button 
              className="bg-indigo-600 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center gap-2" 
              //onClick={downloadTranscription} // download transcription placeholder
            >
              <i className="bi bi-download"/>
            </button>
        </div>
      </div>
      <div className="bg-slate-700 rounded-lg p-3 flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto">
          <p className="text-sm text-gray-300 leading-6">
            Transcribed interview text will go here.
          </p>
        </div>
        <div className="flex justify-end mt-2">
          <button className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200">
            <i className="bi bi-code"></i>
          </button>
          <button className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200">
            <i className="bi bi-highlighter"></i>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TranscriptionSection;