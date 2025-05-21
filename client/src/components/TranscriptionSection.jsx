const TranscriptionSection = () => {
  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4 flex-1 flex flex-col">
      <div className="flex justify-between items-center mb-2 font-sora">
        <h3 className="text-lg text-white font-bold">Transcription</h3>
          <div className='flex gap-3'>
            <button 
              className="bg-indigo-700 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-600 flex items-center gap-2" 
              //onClick={editTranscription} // editing/highlighting transcriptions will be implemented later.
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16">
              <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325"/>
              </svg>
            </button>

            <button 
              className="bg-indigo-700 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-600 flex items-center gap-2" 
              //onClick={downloadTranscription} // download transcription placeholder
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16">
              <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5"/>
              <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708z"/>
              </svg>
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
            <i className="icon-code"></i>
          </button>
          <button className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200">
            <i className="icon-highlighter"></i>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TranscriptionSection;