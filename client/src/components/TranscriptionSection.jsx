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
    const [projectHighlighters, setProjectHighlighters] = useState([]);

    // highlight state 
    const [highlights, setHighlights] = useState([]);
    const [highlightColor, setHighlightColor] = useState("yellow");

    const previousProjectId = useRef(activeProjectId);
    const previousTranscriptionData = useRef(transcriptionData);

    // ref to the rendered text container for selection offset calc
    const textContainerRef = useRef(null);

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

    // Fetch project highlighters when project changes
    useEffect(() => {
        const fetchHighlighters = async () => {
            if (!activeProjectId) return;
            try {
            const response = await fetch(API_ENDPOINTS.getHighlighters(activeProjectId));
            if (response.ok) {
                const data = await response.json();

                // fallback block if no highlighters exist
                if (data.length === 0) {
                setProjectHighlighters([
                    { highlighter_id: "default-yellow", label: "Highlight", colour: "yellow", weight: 1 },
                    { highlighter_id: "default-blue", label: "Note", colour: "lightblue", weight: 1 },
                    { highlighter_id: "default-green", label: "Context", colour: "lightgreen", weight: 1 },
                    { highlighter_id: "default-pink", label: "Context", colour: "pink", weight: 1 },
                    { highlighter_id: "default-orange", label: "Context", colour: "orange", weight: 1 }
                ]);
                } else {
                setProjectHighlighters(data);
                }

            } else {
                console.error("Failed to fetch project highlighters");
                setProjectHighlighters([]);
            }
            } catch (err) {
            console.error("Error fetching project highlighters:", err);
            setProjectHighlighters([]);
            }
        };

        fetchHighlighters();
    }, [activeProjectId]);


    // Clear uploaded transcription data when project changes
    useEffect(() => {
        if (activeProjectId !== previousProjectId.current) {
            setHighlights([]);

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
                            await fetchHighlights(transcriptionDataObject.transcription_id);

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

    // fetch highlights for a transcription, tolerating 404 where no highlight yet
    const fetchHighlights = async (transcriptionId) => {
        try {
        const res = await fetch(API_ENDPOINTS.getHighlights(transcriptionId));
        if (res.ok) {
            const data = await res.json();
            setHighlights(Array.isArray(data) ? data : []);
        } else if (res.status === 404) {
            setHighlights([]);
        } else {
            console.error('Failed to load highlights');
        }
        } catch (e) {
        console.error('Error loading highlights:', e);
        }
    };

    // Handle transcription selection
    const handleTranscriptionChange = (event) => {
        const transcriptionId = event.target.value;
        setSelectedTranscriptionId(transcriptionId);
        
        if (transcriptionId) {
            const idNum = parseInt(transcriptionId, 10);
            loadTranscriptionText(idNum);
            fetchHighlights(idNum);
        } else {
            setSelectedTranscriptionText("");
            setHighlights([]);
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
                    setHighlights([]);
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

            const currentTranscription = transcriptions.find(
                (t) => t.transcription_id === parseInt(selectedTranscriptionId)
                );

            const response = await fetch(
                API_ENDPOINTS.updateProjectTranscription(activeProjectId, selectedTranscriptionId),
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: currentTranscription?.name || 'Edited transcription',
                        text: editedText,
                    }),
                }
            );
            
            if (response.ok) {
                setSelectedTranscriptionText(editedText);
                setIsEditing(false);
                setEditedText("");
                console.log('Transcription saved successfully');
                
                // Clean up highlights that no longer fit the updated text
                await adjustHighlightsAfterEdit(selectedTranscriptionId, selectedTranscriptionText, editedText);

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

    // compute selection offsets within the text container
    const getSelectionOffsets = (containerEl) => {
        const sel = window.getSelection();
        if (!sel || sel.rangeCount === 0) return null;
        const range = sel.getRangeAt(0);
        if (!containerEl.contains(range.startContainer) || !containerEl.contains(range.endContainer)) {
        return null; // selection is outside
        }

        // Count chars from start of container to range start
        const preRange = range.cloneRange();
        preRange.selectNodeContents(containerEl);
        preRange.setEnd(range.startContainer, range.startOffset);
        const start = preRange.toString().length;

        const selectedText = range.toString();
        const end = start + selectedText.length;

        return { start, end, text: selectedText };
    };
    
    // remove existing highlights overlapping the new one
    const removeOverlappingHighlights = async (transcriptionId, start, end) => {
        const overlaps = highlights.filter(
            (h) => h.startOffset < end && h.endOffset > start
        );
        if (overlaps.length === 0) return;

        const fragmentsToKeep = [];

        for (const h of overlaps) {
            // Full overlap – delete completely
            if (start <= h.startOffset && end >= h.endOffset) {
            await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
            continue;
            }

            // New highlight fully inside old one → split into left + right
            if (start > h.startOffset && end < h.endOffset) {
            fragmentsToKeep.push({
                transcriptionId,
                start: h.startOffset,
                end: start,
                color: h.color,
            });
            fragmentsToKeep.push({
                transcriptionId,
                start: end,
                end: h.endOffset,
                color: h.color,
            });
            await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
            continue;
            }

            // Overlap only on left edge (new starts before, ends inside old)
            if (start < h.startOffset && end > h.startOffset && end < h.endOffset) {
            fragmentsToKeep.push({
                transcriptionId,
                start: end,
                end: h.endOffset,
                color: h.color,
            });
            await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
            continue;
            }

            // Overlap only on right edge (new starts inside old and ends after)
            if (start > h.startOffset && start < h.endOffset && end >= h.endOffset) {
                // keep only the left part before the new selection
                fragmentsToKeep.push({
                    transcriptionId,
                    start: h.startOffset,
                    end: start,
                    color: h.color,
                });
                await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
                continue;
                }

                // 🆕 New highlight ends exactly where the old one ends (like "World" case)
                if (start > h.startOffset && end === h.endOffset) {
                fragmentsToKeep.push({
                    transcriptionId,
                    start: h.startOffset,
                    end: start,
                    color: h.color,
                });
                await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
                continue;
                }
        }

        // Update state + persist new fragments
        setHighlights((prev) =>
            prev.filter((h) => !overlaps.some((o) => o.highlight_id === h.highlight_id))
            .concat(fragmentsToKeep)
        );

        for (const frag of fragmentsToKeep) {
            const url = new URL(`${API_ENDPOINTS.HIGHLIGHTS}/`);
            url.searchParams.set("transcription_id", frag.transcriptionId);
            url.searchParams.set("start", frag.start);
            url.searchParams.set("end", frag.end);
            url.searchParams.set("color", frag.color);
            await fetch(url.toString(), { method: "POST" });
        }
        };

    // Remove highlight(s) from the selected text range
    // Remove only the selected portion of highlight(s)
    const handleClearHighlight = async () => {
        if (!selectedTranscriptionId || !textContainerRef.current) return;

        const offsets = getSelectionOffsets(textContainerRef.current);
        if (!offsets || offsets.text.length === 0) return;

        const transcriptionId = parseInt(selectedTranscriptionId, 10);
        const { start, end } = offsets;

        const overlaps = highlights.filter(
            (h) => h.startOffset < end && h.endOffset > start
        );

        const fragmentsToKeep = [];

        for (const h of overlaps) {
            // Entire overlap – delete completely
            if (start <= h.startOffset && end >= h.endOffset) {
            await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
            continue;
            }

            // Partial overlap on left side
            if (start > h.startOffset && start < h.endOffset && end >= h.endOffset) {
            fragmentsToKeep.push({
                transcriptionId,
                start: h.startOffset,
                end: start,
                color: h.color,
            });
            await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
            continue;
            }

            // Partial overlap on right side
            if (start <= h.startOffset && end > h.startOffset && end < h.endOffset) {
            fragmentsToKeep.push({
                transcriptionId,
                start: end,
                end: h.endOffset,
                color: h.color,
            });
            await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
            continue;
            }

            // Middle portion (split highlight into two)
            if (start > h.startOffset && end < h.endOffset) {
            fragmentsToKeep.push({
                transcriptionId,
                start: h.startOffset,
                end: start,
                color: h.color,
            });
            fragmentsToKeep.push({
                transcriptionId,
                start: end,
                end: h.endOffset,
                color: h.color,
            });
            await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
            }
        }

        // Persist new fragments
        for (const frag of fragmentsToKeep) {
            const url = new URL(`${API_ENDPOINTS.HIGHLIGHTS}/`);
            url.searchParams.set("transcription_id", frag.transcriptionId);
            url.searchParams.set("start", frag.start);
            url.searchParams.set("end", frag.end);
            url.searchParams.set("color", frag.color);
            await fetch(url.toString(), { method: "POST" });
        }

        // Refresh highlights
        setTimeout(() => fetchHighlights(transcriptionId), 100);

        // Clear selection
        const sel = window.getSelection();
        if (sel) sel.removeAllRanges();
    };


    // Remove ALL highlights for the current transcription
    const handleClearAllHighlights = async () => {
        if (!selectedTranscriptionId) return;

        try {
            // Delete every highlight from backend
            for (const h of highlights) {
            await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
            }

            // Clear highlights in state
            setHighlights([]);

            console.log("All highlights cleared successfully");
        } catch (e) {
            console.error("Error clearing all highlights:", e);
            alert("Failed to remove all highlights. Please try again.");
        }
    };


    const addHighlight = async ({ transcriptionId, start, end, color }) => {
        try {
        // Your FastAPI route takes simple params (query/form), not JSON.
        // We'll send as query params to /highlights/
        const url = new URL(`${API_ENDPOINTS.HIGHLIGHTS}/`);
        url.searchParams.set('transcription_id', transcriptionId);
        url.searchParams.set('start', start);
        url.searchParams.set('end', end);
        url.searchParams.set('color', color);

        const res = await fetch(url.toString(), {
            method: 'POST'
        });

        if (!res.ok) {
            const err = await res.text();
            console.error('Failed to add highlight:', err);
            alert('Failed to add highlight');
            return;
        }

        // Re-fetch to keep state in sync with DB
        await fetchHighlights(transcriptionId);
        } catch (e) {
        console.error('Error adding highlight:', e);
        alert('Could not add highlight');
        }
    };

    // Handle text highlighting - persist & re-render instead of DOM wrap
    const handleHighlightText = async () => {
        if (!selectedTranscriptionId || !textContainerRef.current) return;

        const offsets = getSelectionOffsets(textContainerRef.current);
        if (!offsets || offsets.text.length === 0) return;

        const transcriptionId = parseInt(selectedTranscriptionId, 10);

        // remove overlapping highlights (same or overlapping range)
        await removeOverlappingHighlights(transcriptionId, offsets.start, offsets.end);

        // clear visual selection
        const sel = window.getSelection();
        if (sel) sel.removeAllRanges();

        // save new highlight
        await addHighlight({
            transcriptionId,
            start: offsets.start,
            end: offsets.end,
            color: highlightColor,
        });

        // reload highlights after short delay
        setTimeout(() => fetchHighlights(transcriptionId), 100);

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
    
    const displayTextString = selectedTranscriptionText || 
        (shouldShowUploadedTranscription ? transcriptionDataObject.transcription : "") || 
        "Transcribed interview text will go here.";

    const mergeAndDeduplicateHighlights = (ranges) => {
        if (!Array.isArray(ranges)) return [];
        if (ranges.length <= 1) return ranges;

        // Sort by start offset
        const sorted = [...ranges].sort((a, b) => a.startOffset - b.startOffset);

        const merged = [];
        for (const current of sorted) {
            const last = merged[merged.length - 1];

            // if overlapping or identical range, replace with the most recent color (current)
            if (last && current.startOffset < last.endOffset) {
            merged[merged.length - 1] = {
                ...last,
                endOffset: Math.max(last.endOffset, current.endOffset),
                color: current.color, // keep newest color
            };
            } else {
            merged.push(current);
            }
        }

        // Deduplicate exact duplicates (same start, end)
        const unique = [];
        const seen = new Set();
        for (const h of merged) {
            const key = `${h.startOffset}-${h.endOffset}`;
            if (!seen.has(key)) {
            seen.add(key);
            unique.push(h);
            }
        }

        return unique;
    };

    const renderWithHighlights = (text, ranges) => {
        if (!text) return null;
        const mergedRanges = mergeAndDeduplicateHighlights(ranges);
        if (mergedRanges.length === 0) {
            // Render plain text preserving newlines
            return text.split('\n').map((line, i) => (
            <React.Fragment key={`line-${i}`}>
                {line}
                {i < text.split('\n').length - 1 ? <br /> : null}
            </React.Fragment>
            ));
        }

        // Sort highlights by start; do not mutate original
        const sorted = [...mergedRanges].sort((a, b) => a.startOffset - b.startOffset);

        const parts = [];
        let cursor = 0;

        for (let i = 0; i < sorted.length; i++) {
        const h = sorted[i];
        const start = Math.max(0, Math.min(h.startOffset, text.length));
        const end = Math.max(0, Math.min(h.endOffset, text.length));

        if (start > cursor) {
            parts.push({ type: 'text', text: text.slice(cursor, start) });
        }
        if (end > start) {
            parts.push({
            type: 'hl',
            text: text.slice(start, end),
            color: h.color,
            id: h.highlight_id ?? `${start}-${end}-${h.color}-${i}`
            });
        }
        cursor = Math.max(cursor, end);
        }

        if (cursor < text.length) {
        parts.push({ type: 'text', text: text.slice(cursor) });
        }

        // Render, preserving newlines inside each piece
        const renderPiece = (piece, key) => {
        const chunks = piece.text.split('\n');
        const children = [];
        for (let i = 0; i < chunks.length; i++) {
            children.push(chunks[i]);
            if (i < chunks.length - 1) children.push(<br key={`${key}-br-${i}`} />);
        }

        if (piece.type === 'hl') {
            return (
            <span
                key={key}
                className="highlighted-text"
                style={{ backgroundColor: piece.color, padding: '2px 4px', borderRadius: '3px' }}
            >
                {children}
            </span>
            );
        }
        return <React.Fragment key={key}>{children}</React.Fragment>;
        };

        return parts.map((p, idx) => renderPiece(p, `p-${idx}`));
    };

    // Adjust highlights after text edit (no external library)
    // Safely adjust highlights after edit: preserve those whose range text didn't change
    const adjustHighlightsAfterEdit = async (transcriptionId, oldText, newText) => {
        const updated = [];

        for (const h of highlights) {
            const oldSegment = oldText.slice(h.startOffset, h.endOffset);
            const newSegment = newText.slice(h.startOffset, h.endOffset);

            // If the text under highlight is identical, keep it
            if (oldSegment === newSegment && h.endOffset <= newText.length) {
            updated.push(h);
            continue;
            }

            // Otherwise, remove the highlight (text was changed or deleted)
            try {
            await fetch(`${API_ENDPOINTS.HIGHLIGHTS}/${h.highlight_id}`, { method: "DELETE" });
            } catch (e) {
            console.error("Failed to delete outdated highlight:", e);
            }
        }

        setHighlights(updated);
    };




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
                        disabled={!displayTextString || displayTextString === "Transcribed interview text will go here."}
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
                            {projectHighlighters.length > 0 ? (
                                projectHighlighters.map((h) => (
                                    <button
                                    key={h.highlighter_id}
                                    className={`w-4 h-4 rounded border-2 ${
                                        highlightColor === h.colour ? 'border-white' : 'border-slate-500'
                                    }`}
                                    style={{ backgroundColor: h.colour }}
                                    onClick={() => handleHighlightColorChange(h.colour)}
                                    aria-label={`Select ${h.label} highlight`}
                                    title={h.label}
                                    />
                                ))
                            ) : (
                                <span className="text-xs text-slate-400">No highlight colours set</span>
                            )}

                        </div>
                        {/* Clear highlight button */}
                        <button
                            className="w-4 h-4 rounded border-2 border-slate-500 flex items-center justify-center text-slate-400 hover:text-white hover:border-white"
                            onClick={handleClearHighlight}
                            aria-label="Clear selected highlights"
                            title='Clear selected highlight'
                        >
                            <i className="bi bi-eraser-fill text-xs" aria-hidden="true"></i>
                        </button>

                        <button
                            className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200"
                            aria-label="Highlight selected text"
                            onClick={handleHighlightText}
                            title='Select text and click to highlight'
                        >
                            <i className="bi bi-highlighter" aria-hidden="true"></i>
                        </button>

                        {/* Clear all highlights button */}
                        <button
                            className="bg-transparent border border-slate-500 text-slate-400 text-xs px-2 py-1 rounded hover:border-white hover:text-white transition-colors ml-2"
                            onClick={handleClearAllHighlights}
                            aria-label="Remove all highlights"
                        >
                            Clear All
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
                            ref={textContainerRef}
                            className="text-sm text-gray-300 leading-6 whitespace-pre-wrap"
                            contentEditable={false}
                        >
                            {renderWithHighlights(displayTextString, highlights)}
                        </div>
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
