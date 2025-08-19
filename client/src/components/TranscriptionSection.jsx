/**
 * TranscriptionSection Component
 * * Displays interview transcriptions with editing and export functionality.
 * Provides a workspace for viewing and annotating transcribed text.
 */
import React from 'react'; // Make sure React is imported

/** API endpoint for downloading transcription */
const DOWNLOAD_API_URL = "http://localhost:8000/download/";

/** Safely parse JSON, returns null on failure */
const safeParseJSON = (json) => {
  try {
    return json ? JSON.parse(json) : null;
  } catch {
    console.error("Invalid transcription data JSON");
    return null;
  }
};

const TranscriptionSection = ({ transcriptionData }) => { // Destructure props directly

    const transcriptionDataObject = safeParseJSON(transcriptionData);

    const handleDownloadTranscription = async () => { // Make the function async
        if (!transcriptionDataObject) {
            console.warn("No transcription to download");
            return; // Exit if no data
        }

        try {
            // Create FormData object
            const downloadData = new FormData();
            downloadData.append('final_output', transcriptionDataObject.transcription);
            downloadData.append('filename', transcriptionDataObject.filename);

            // POST request to FastAPI endpoint and await the response
            const response = await fetch(DOWNLOAD_API_URL, {
                method: "POST",
                body: downloadData,
            });

            // Check if the request was successful
            if (!response.ok) {
                // If not successful, throw an error with status text
                throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
            }

            // Get the blob data (the file content)
            const blob = await response.blob();

            // Create a URL for the blob
            const url = window.URL.createObjectURL(blob);

            // Create a temporary link element
            const link = document.createElement('a');
            link.style.display = 'none';
            link.href = url;
            // Set the download attribute to the desired filename
            link.download = transcriptionDataObject.filename;

            // Append the link to the body
            document.body.appendChild(link);
            // Programmatically click the link to trigger the download
            link.click();

            // Clean up by revoking the object URL and removing the link
            window.URL.revokeObjectURL(url);
            document.body.removeChild(link);

        } catch (error) {
            console.error('An unexpected error occurred during download: ', error);
            // You might want to show an error message to the user here
        }
    };

    console.log(transcriptionDataObject);
    if (transcriptionDataObject) { console.log(transcriptionDataObject.transcription); }

    return (
        /* Main container with card styling and flex layout */
        <div className="bg-slate-800 rounded-xl shadow-md p-4 flex-1 flex flex-col">
            {/* Header section with title and action buttons */}
            <div className="flex justify-between items-center mb-2 font-sora">
                {/* Section title */}
                <h3 className="text-lg text-white font-bold">Transcription</h3>

                {/* Action buttons container */}
                <div className='flex gap-3'>
                    {/* Edit transcription button */}
                    <button
                        className="bg-indigo-600 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center gap-2"
                        aria-label="Edit transcription"
                    // onClick={editTranscription} 
                    // TODO: Implement transcription editing functionality
                    >
                        <i className="bi bi-pencil" aria-hidden="true" />
                    </button>

                    {/* Download transcription button */}
                    <button
                        className="bg-indigo-600 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center gap-2"
                        aria-label="Download transcription"
                        onClick={handleDownloadTranscription}
                    >
                        <i className="bi bi-download" aria-hidden="true" />
                    </button>
                </div>
            </div>

            {/* Transcription content area */}
            <div className="bg-slate-700 rounded-lg p-3 flex-1 flex flex-col">
                {/* Scrollable transcription text container */}
                <div className="flex-1 overflow-y-auto">
                    {/* Placeholder transcription text - will be replaced with actual content */}
                    <p className="text-sm text-gray-300 leading-6">
                        {transcriptionDataObject ? transcriptionDataObject.transcription : "Transcribed interview text will go here."}
                    </p>
                </div>

                {/* Transcription toolbar (bottom right) */}
                <div className="flex justify-end mt-2">
                    {/* Code view toggle button */}
                    <button
                        className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200"
                        aria-label="Toggle code view"
                    // TODO: Implement code view toggle functionality
                    >
                        <i className="bi bi-code" aria-hidden="true"></i>
                    </button>

                    {/* Highlighting tool button */}
                    <button
                        className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200"
                        aria-label="Highlight text"
                    // TODO: Implement text highlighting functionality
                    >
                        <i className="bi bi-highlighter" aria-hidden="true"></i>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TranscriptionSection;