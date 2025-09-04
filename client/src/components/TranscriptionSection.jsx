/**
 * TranscriptionSection Component
 * * Displays interview transcriptions with editing and export functionality.
 * Provides a workspace for viewing and annotating transcribed text.
 */
import React, { useState, useEffect } from 'react'; // Make sure React is imported
import { API_ENDPOINTS } from "../config/api";
import { useProject } from "../contexts/ProjectContext";


/** Safely parse JSON, returns null on failure */
const safeParseJSON = (json) => {
  try {
    return json ? JSON.parse(json) : null;
  } catch {
    console.error("Invalid transcription data JSON");
    return null;
  }
};

const TranscriptionSection = ({ transcriptionData, onTranscriptionUploaded }) => { // Add callback prop
    const { activeProjectId } = useProject();
    const [transcriptions, setTranscriptions] = useState([]);
    const [selectedTranscriptionId, setSelectedTranscriptionId] = useState(null);
    const [selectedTranscriptionText, setSelectedTranscriptionText] = useState("");
    const [loading, setLoading] = useState(false);

    const transcriptionDataObject = safeParseJSON(transcriptionData);

    // Load transcriptions when project changes
    useEffect(() => {
        const loadTranscriptions = async () => {
            if (!activeProjectId) return;
            
            try {
                setLoading(true);
                const response = await fetch(API_ENDPOINTS.listProjectTranscriptions(activeProjectId));
                if (response.ok) {
                    const data = await response.json();
                    setTranscriptions(data);
                    // Reset selection when project changes
                    setSelectedTranscriptionId(null);
                    setSelectedTranscriptionText("");
                } else {
                    console.error('Failed to load transcriptions');
                }
            } catch (error) {
                console.error('Error loading transcriptions:', error);
            } finally {
                setLoading(false);
            }
        };

        loadTranscriptions();
    }, [activeProjectId]);

    // Refresh transcriptions when a new one is uploaded
    useEffect(() => {
        if (transcriptionDataObject && transcriptionDataObject.transcription_id) {
            // A new transcription was uploaded, refresh the list
            const refreshTranscriptions = async () => {
                if (!activeProjectId) return;
                
                try {
                    const response = await fetch(API_ENDPOINTS.listProjectTranscriptions(activeProjectId));
                    if (response.ok) {
                        const data = await response.json();
                        setTranscriptions(data);
                        // Auto-select the newly uploaded transcription
                        setSelectedTranscriptionId(transcriptionDataObject.transcription_id);
                        setSelectedTranscriptionText(transcriptionDataObject.transcription);
                    }
                } catch (error) {
                    console.error('Error refreshing transcriptions:', error);
                }
            };
            
            refreshTranscriptions();
        }
    }, [transcriptionDataObject, activeProjectId]);

    // Load selected transcription text
    const loadTranscriptionText = async (transcriptionId) => {
        if (!activeProjectId || !transcriptionId) return;
        
        try {
            setLoading(true);
            const response = await fetch(API_ENDPOINTS.getProjectTranscription(activeProjectId, transcriptionId));
            if (response.ok) {
                const data = await response.json();
                setSelectedTranscriptionText(data.text);
            } else {
                console.error('Failed to load transcription text');
                setSelectedTranscriptionText("");
            }
        } catch (error) {
            console.error('Error loading transcription text:', error);
            setSelectedTranscriptionText("");
        } finally {
            setLoading(false);
        }
    };

    // Handle transcription selection
    const handleTranscriptionChange = (event) => {
        const transcriptionId = event.target.value;
        setSelectedTranscriptionId(transcriptionId);
        
        if (transcriptionId) {
            loadTranscriptionText(parseInt(transcriptionId));
        } else {
            setSelectedTranscriptionText("");
        }
    };

    const handleDownloadTranscription = async () => { // Make the function async
        const textToDownload = selectedTranscriptionText || (transcriptionDataObject ? transcriptionDataObject.transcription : "");
        
        if (!textToDownload) {
            console.warn("No transcription to download");
            return; // Exit if no data
        }

        try {
            // Create FormData object
            const downloadData = new FormData();
            downloadData.append('final_output', textToDownload);
            downloadData.append('filename', `transcription_${selectedTranscriptionId || 'default'}.txt`);

            // POST request to FastAPI endpoint and await the response
            const response = await fetch(API_ENDPOINTS.DOWNLOAD, {
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
            link.download = `transcription_${selectedTranscriptionId || 'default'}.txt`;

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

    // Determine which text to display
    const displayText = selectedTranscriptionText || (transcriptionDataObject ? transcriptionDataObject.transcription : "Transcribed interview text will go here.");

    return (
        /* Main container with card styling and flex layout */
        <div className="bg-slate-800 rounded-xl shadow-md p-4 flex-1 flex flex-col">
            {/* Header section with title and action buttons */}
            <div className="flex justify-between items-center mb-2 font-sora">
                {/* Section title with dropdown */}
                <div className="flex items-center gap-3">
                    <h3 className="text-lg text-white font-bold">Transcription</h3>
                    
                    {/* Transcription dropdown */}
                    <select
                        value={selectedTranscriptionId || ""}
                        onChange={handleTranscriptionChange}
                        disabled={loading || transcriptions.length === 0}
                        className="bg-slate-700 text-white text-sm px-3 py-1 rounded-md border border-slate-600 focus:border-indigo-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <option value="" disabled>
                            {loading ? "Loading..." : transcriptions.length === 0 ? "No transcriptions" : "Select transcription"}
                        </option>
                        {transcriptions.map((transcription) => (
                            <option key={transcription.transcription_id} value={transcription.transcription_id}>
                                {transcription.name}
                            </option>
                        ))}
                    </select>
                </div>

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
                        disabled={!displayText || displayText === "Transcribed interview text will go here."}
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
                        {displayText}
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