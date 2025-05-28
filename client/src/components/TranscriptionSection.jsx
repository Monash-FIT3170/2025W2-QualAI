import React, { useState, useEffect, useMemo } from 'react';

const TranscriptionSection = ({ transcriptionData }) => {
    // Memoize transcriptionDataObject to only recompute when transcriptionData changes
    const transcriptionDataObject = useMemo(() => {
        return transcriptionData ? JSON.parse(transcriptionData) : null;
    }, [transcriptionData]);

    const [isEditing, setIsEditing] = useState(false);
    const [editedTranscription, setEditedTranscription] = useState(
        transcriptionDataObject?.transcription || ''
    );

    // Update transcription when transcriptionDataObject changes
    useEffect(() => {
        setEditedTranscription(transcriptionDataObject?.transcription || '');
        setIsEditing(false); // Exit edit mode when new data loads
    }, [transcriptionDataObject]);

    // Toggle edit mode
    const toggleEdit = () => {
        setIsEditing(!isEditing);
    };

    // Handle download on the client side
    const handleDownloadTranscription = () => {
        if (!editedTranscription) {
            console.log("No transcription to download");
            return;
        }

        const blob = new Blob([editedTranscription], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = transcriptionDataObject?.filename || 'transcription.txt';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    };

    return (
        <div className="bg-slate-800 rounded-xl shadow-md p-4 flex-1 flex flex-col">
            <div className="flex justify-between items-center mb-2 font-sora">
                <h3 className="text-lg text-white font-bold">Transcription</h3>
                <div className="flex gap-3">
                    <button
                        className="bg-indigo-600 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center gap-2"
                        aria-label={isEditing ? "Exit edit mode" : "Edit transcription"}
                        onClick={toggleEdit}
                        disabled={!transcriptionDataObject}
                    >
                        <i className={isEditing ? "bi bi-check" : "bi bi-pencil"} aria-hidden="true" />
                    </button>
                    <button
                        className="bg-indigo-600 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center gap-2"
                        aria-label="Download transcription"
                        onClick={handleDownloadTranscription}
                        disabled={!transcriptionDataObject}
                    >
                        <i className="bi bi-download" aria-hidden="true" />
                    </button>
                </div>
            </div>
            <div className="bg-slate-700 rounded-lg p-3 flex-1 flex flex-col">
                <div className="flex-1 overflow-y-auto">
                    {isEditing ? (
                        <textarea
                            value={editedTranscription}
                            onChange={(e) => setEditedTranscription(e.target.value)}
                            className="w-full h-full bg-slate-700 text-sm text-gray-300 leading-6 p-2 border-0"
                            style={{ resize: 'none' }}
                        />
                    ) : (
                        <p className="text-sm text-gray-300 leading-6">
                            {editedTranscription || "Transcribed interview text will go here."}
                        </p>
                    )}
                </div>
                <div className="flex justify-end mt-2">
                    <button
                        className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200"
                        aria-label="Toggle code view"
                    >
                        <i className="bi bi-code" aria-hidden="true" />
                    </button>
                    <button
                        className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200"
                        aria-label="Highlight text"
                    >
                        <i className="bi bi-highlighter" aria-hidden="true" />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TranscriptionSection;