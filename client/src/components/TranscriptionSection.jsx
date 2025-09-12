/**
 * TranscriptionSection Component
 * * Displays interview transcriptions with editing and export functionality.
 * Provides a workspace for viewing and annotating transcribed text.
 */
import React, { useState, useEffect, useRef } from 'react'; // Make sure React is imported
import { API_ENDPOINTS } from "../config/api";
import { useProject } from "../contexts/ProjectContext";
import "../assets/styles/TranscriptionSection.css";


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
    const [deleting, setDeleting] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editedText, setEditedText] = useState("");
    const [saving, setSaving] = useState(false);
    const [highlightColor, setHighlightColor] = useState("yellow");
    const previousProjectId = useRef(activeProjectId);
    const previousTranscriptionData = useRef(transcriptionData);

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

    // Clear uploaded transcription data when project changes
    useEffect(() => {
        if (activeProjectId !== previousProjectId.current) {
            // Project has changed, clear any uploaded transcription data
            if (onTranscriptionUploaded) {
                onTranscriptionUploaded(null);
            }
            previousProjectId.current = activeProjectId;
        }
    }, [activeProjectId, onTranscriptionUploaded]);

    // Handle new transcription uploads - only run when transcriptionData actually changes
    useEffect(() => {
        if (transcriptionData !== previousTranscriptionData.current) {
            previousTranscriptionData.current = transcriptionData;
            
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
        }
    }, [transcriptionData, transcriptionDataObject, activeProjectId]);

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

    // Handle transcription deletion
    const handleDeleteTranscription = async () => {
        if (!selectedTranscriptionId || !activeProjectId) return;
        
        const confirmed = window.confirm(
            `Are you sure you want to delete this transcription? This action cannot be undone.`
        );
        
        if (!confirmed) return;
        
        try {
            setDeleting(true);
            const response = await fetch(
                API_ENDPOINTS.deleteProjectTranscription(activeProjectId, selectedTranscriptionId),
                {
                    method: 'DELETE',
                }
            );
            
            if (response.ok) {
                // Refresh the transcriptions list
                const refreshResponse = await fetch(API_ENDPOINTS.listProjectTranscriptions(activeProjectId));
                if (refreshResponse.ok) {
                    const data = await refreshResponse.json();
                    setTranscriptions(data);
                    // Clear selection
                    setSelectedTranscriptionId(null);
                    setSelectedTranscriptionText("");
                    setEditedText("");
                    setIsEditing(false);
                }
                console.log('Transcription deleted successfully');
            } else {
                const errorData = await response.json();
                console.error('Failed to delete transcription:', errorData);
                alert('Failed to delete transcription. Please try again.');
            }
        } catch (error) {
            console.error('Error deleting transcription:', error);
            alert('An error occurred while deleting the transcription. Please try again.');
        } finally {
            setDeleting(false);
        }
    };

    // Handle edit mode toggle
    const handleEditToggle = () => {
        if (isEditing) {
            // Cancel editing
            setEditedText("");
            setIsEditing(false);
        } else {
            // Start editing
            setEditedText(selectedTranscriptionText);
            setIsEditing(true);
        }
    };

    // Handle save transcription
    const handleSaveTranscription = async () => {
        if (!selectedTranscriptionId || !activeProjectId || !editedText.trim()) return;
        
        try {
            setSaving(true);
            const response = await fetch(
                API_ENDPOINTS.updateProjectTranscription(activeProjectId, selectedTranscriptionId),
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: editedText }),
                }
            );
            
            if (response.ok) {
                setSelectedTranscriptionText(editedText);
                setIsEditing(false);
                setEditedText("");
                console.log('Transcription saved successfully');
            } else {
                const errorData = await response.json();
                console.error('Failed to save transcription:', errorData);
                alert('Failed to save transcription. Please try again.');
            }
        } catch (error) {
            console.error('Error saving transcription:', error);
            alert('An error occurred while saving the transcription. Please try again.');
        } finally {
            setSaving(false);
        }
    };

    // Handle text highlighting
    const handleHighlightText = () => {
        const selection = window.getSelection();
        if (selection.toString().trim()) {
            const range = selection.getRangeAt(0);
            const span = document.createElement('span');
            span.style.backgroundColor = highlightColor;
            span.style.padding = '2px 4px';
            span.style.borderRadius = '3px';
            span.className = 'highlighted-text';
            
            try {
                range.surroundContents(span);
                selection.removeAllRanges();
            } catch (e) {
                // If surroundContents fails, try a different approach
                const contents = range.extractContents();
                span.appendChild(contents);
                range.insertNode(span);
                selection.removeAllRanges();
            }
        }
    };

    // Handle highlight color change
    const handleHighlightColorChange = (color) => {
        setHighlightColor(color);
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

    // Determine which text to display - only show uploaded transcription if it belongs to current project
    const shouldShowUploadedTranscription = transcriptionDataObject && 
        transcriptionDataObject.project_id && 
        transcriptionDataObject.project_id.toString() === activeProjectId?.toString();
    
    const displayText = selectedTranscriptionText || 
        (shouldShowUploadedTranscription ? transcriptionDataObject.transcription : "") || 
        "Transcribed interview text will go here.";

    return (
        /* Main container with card styling and flex layout */
        <div className="bg-slate-800 rounded-xl shadow-md p-4 flex-1 flex flex-col min-h-0 overflow-hidden">

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
                    {/* Edit/Save transcription button */}
                    <button
                        className={`text-white text-sm px-4 py-2 rounded-md flex items-center gap-2 ${
                            isEditing 
                                ? "bg-green-600 hover:bg-green-700" 
                                : "bg-indigo-600 hover:bg-indigo-700"
                        }`}
                        aria-label={isEditing ? "Save transcription" : "Edit transcription"}
                        onClick={isEditing ? handleSaveTranscription : handleEditToggle}
                        disabled={!selectedTranscriptionId || saving}
                    >
                        {saving ? (
                            <>
                                <i className="bi bi-arrow-clockwise spin" aria-hidden="true" />
                                Saving...
                            </>
                        ) : isEditing ? (
                            <>
                                <i className="bi bi-check" aria-hidden="true" />
                                Save
                            </>
                        ) : (
                            <>
                                <i className="bi bi-pencil" aria-hidden="true" />
                                Edit
                            </>
                        )}
                    </button>

                    {/* Cancel edit button - only show when editing */}
                    {isEditing && (
                        <button
                            className="bg-gray-600 text-white text-sm px-4 py-2 rounded-md hover:bg-gray-700 flex items-center gap-2"
                            aria-label="Cancel editing"
                            onClick={handleEditToggle}
                        >
                            <i className="bi bi-x" aria-hidden="true" />
                            Cancel
                        </button>
                    )}

                    {/* Delete transcription button */}
                    <button
                        className="bg-red-600 text-white text-sm px-4 py-2 rounded-md hover:bg-red-700 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label="Delete transcription"
                        onClick={handleDeleteTranscription}
                        disabled={!selectedTranscriptionId || deleting}
                    >
                        {deleting ? (
                            <>
                                <i className="bi bi-arrow-clockwise spin" aria-hidden="true" />
                                Deleting...
                            </>
                        ) : (
                            <>
                                <i className="bi bi-trash" aria-hidden="true" />
                                Delete
                            </>
                        )}
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
            <div className="bg-slate-700 rounded-lg p-3 flex-1 flex flex-col min-h-0">
                {/* Highlighting toolbar - only show when not editing */}
                {!isEditing && selectedTranscriptionId && (
                    <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-600">
                        <span className="text-xs text-slate-400">Highlight:</span>
                        <div className="flex gap-1">
                            {['yellow', 'lightblue', 'lightgreen', 'pink', 'orange'].map((color) => (
                                <button
                                    key={color}
                                    className={`w-4 h-4 rounded border-2 ${
                                        highlightColor === color ? 'border-white' : 'border-slate-500'
                                    }`}
                                    style={{ backgroundColor: color }}
                                    onClick={() => handleHighlightColorChange(color)}
                                    aria-label={`Select ${color} highlight color`}
                                />
                            ))}
                        </div>
                        <button
                            className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200"
                            aria-label="Highlight selected text"
                            onClick={handleHighlightText}
                        >
                            <i className="bi bi-highlighter" aria-hidden="true"></i>
                        </button>
                    </div>
                )}

                {/* Scrollable transcription text container */}
                <div className="flex-1 overflow-y-auto max-h-[200px] transcription-text">
                    {isEditing ? (
                        <textarea
                            className="w-full h-full bg-transparent text-sm text-gray-300 leading-6 resize-none border-none outline-none"
                            value={editedText}
                            onChange={(e) => setEditedText(e.target.value)}
                            placeholder="Edit transcription text here..."
                        />
                    ) : (
                        <div 
                            className="text-sm text-gray-300 leading-6 whitespace-pre-wrap"
                            contentEditable={false}
                            dangerouslySetInnerHTML={{ __html: displayText.replace(/\n/g, '<br>') }}
                        />
                    )}
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
                </div>
            </div>
        </div>
    );
};

export default TranscriptionSection;