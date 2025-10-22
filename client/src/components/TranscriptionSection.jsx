/**
 * TranscriptionSection Component
 * Displays interview transcriptions with editing, download,
 * and ChatPDF-style highlights (offset-based & persisted).
 */
import React, { useState, useEffect, useRef, useCallback } from "react";
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

/* ---------- Highlight helpers (offset-based, robust) ---------- */
const toPlainText = (htmlOrText) => {
  const temp = document.createElement("div");
  temp.innerHTML = htmlOrText || "";
  return temp.textContent || temp.innerText || "";
};

const getSelectionOffsets = (containerEl, fullPlainText) => {
  const sel = window.getSelection?.();
  if (!sel || sel.rangeCount === 0) return null;

  const range = sel.getRangeAt(0);
  const selectedText = sel.toString();
  if (!selectedText.trim()) return null;

  const pre = document.createRange();
  pre.selectNodeContents(containerEl);
  pre.setEnd(range.startContainer, range.startOffset);
  const start = pre.toString().length;
  const end = start + selectedText.length;

  const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
  return {
    start: clamp(start, 0, fullPlainText.length),
    end: clamp(end, 0, fullPlainText.length),
    selectedText,
  };
};

const normalizeHighlights = (rows) =>
  (rows || []).map((r) => ({
    id: r.id ?? r.highlight_id ?? r.ID ?? undefined,
    start_idx: r.start_idx ?? r.start ?? 0,
    end_idx: r.end_idx ?? r.end ?? 0,
    color: r.color ?? r.colour ?? "yellow",
    comment: r.comment ?? r.note ?? "",
  }));

const renderWithHighlights = (text, highlights) => {
  const hs = normalizeHighlights(highlights).filter(
    (h) =>
      Number.isFinite(h.start_idx) &&
      Number.isFinite(h.end_idx) &&
      h.start_idx < h.end_idx
  );
  if (!hs.length) return text;

  const sorted = [...hs].sort((a, b) => a.start_idx - b.start_idx);
  const out = [];
  let i = 0;
  for (const h of sorted) {
    const s = Math.max(0, h.start_idx);
    const e = Math.min(text.length, h.end_idx);
    if (s > i) out.push({ t: "txt", v: text.slice(i, s) });
    out.push({ t: "hl", v: text.slice(s, e), color: h.color || "yellow" });
    i = e;
  }
  if (i < text.length) out.push({ t: "txt", v: text.slice(i) });

  return out.map((chunk, idx) =>
    chunk.t === "hl" ? (
      <span
        key={idx}
        style={{ background: chunk.color, padding: "2px 4px", borderRadius: 3 }}
      >
        {chunk.v}
      </span>
    ) : (
      <span key={idx}>{chunk.v}</span>
    )
  );
};

const TranscriptionSection = ({ transcriptionData, onTranscriptionUploaded }) => {
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
  const [savedHighlights, setSavedHighlights] = useState([]);

  const previousProjectId = useRef(activeProjectId);
  const previousTranscriptionData = useRef(transcriptionData);
  const transcriptionDataObject = safeParseJSON(transcriptionData);

  /* ---------------------- Load transcriptions when project changes ---------------------- */
  useEffect(() => {
    const loadTranscriptions = async () => {
      if (!activeProjectId) return;
      try {
        setLoading(true);
        const response = await fetch(
          API_ENDPOINTS.listProjectTranscriptions(activeProjectId)
        );
        if (response.ok) {
          const data = await response.json();
          setTranscriptions(data);
          setSelectedTranscriptionId(null);
          setSelectedTranscriptionText("");
        } else {
          console.error("Failed to load transcriptions");
        }
      } catch (error) {
        console.error("Error loading transcriptions:", error);
      } finally {
        setLoading(false);
      }
    };
    loadTranscriptions();
  }, [activeProjectId]);

  /* ---------------------- Clear uploaded transcription when project changes ---------------------- */
  useEffect(() => {
    if (activeProjectId !== previousProjectId.current) {
      if (onTranscriptionUploaded) onTranscriptionUploaded(null);
      previousProjectId.current = activeProjectId;
    }
  }, [activeProjectId, onTranscriptionUploaded]);

  /* ---------------------- Handle new transcription uploads (prop) ---------------------- */
  useEffect(() => {
    if (transcriptionData !== previousTranscriptionData.current) {
      previousTranscriptionData.current = transcriptionData;

      if (transcriptionDataObject && transcriptionDataObject.transcription_id) {
        const refreshTranscriptions = async () => {
          if (!activeProjectId) return;
          try {
            const response = await fetch(
              API_ENDPOINTS.listProjectTranscriptions(activeProjectId)
            );
            if (response.ok) {
              const data = await response.json();
              setTranscriptions(data);
              setSelectedTranscriptionId(transcriptionDataObject.transcription_id);
              setSelectedTranscriptionText(transcriptionDataObject.transcription);
            }
          } catch (error) {
            console.error("Error refreshing transcriptions:", error);
          }
        };
        refreshTranscriptions();
      }
    }
  }, [transcriptionData, transcriptionDataObject, activeProjectId]);

  /* ---------------------- Load selected transcription text ---------------------- */
  const loadTranscriptionText = async (transcriptionId) => {
    if (!activeProjectId || !transcriptionId) return;
    try {
      setLoading(true);
      const response = await fetch(
        API_ENDPOINTS.getProjectTranscription(activeProjectId, transcriptionId)
      );
      if (response.ok) {
        const data = await response.json();
        setSelectedTranscriptionText(data.text);
      } else {
        console.error("Failed to load transcription text");
        setSelectedTranscriptionText("");
      }
    } catch (error) {
      console.error("Error loading transcription text:", error);
      setSelectedTranscriptionText("");
    } finally {
      setLoading(false);
    }
  };

  /* ---------------------- Highlights (per transcription) ---------------------- */
  const loadHighlights = useCallback(async () => {
    if (!selectedTranscriptionId) {
      setSavedHighlights([]);
      return;
    }
    try {
      const url =
        (API_ENDPOINTS.HIGHLIGHTS_LIST &&
          API_ENDPOINTS.HIGHLIGHTS_LIST(selectedTranscriptionId)) ||
        `/highlights/${selectedTranscriptionId}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setSavedHighlights(Array.isArray(data) ? data : []);
      } else {
        setSavedHighlights([]);
      }
    } catch (e) {
      console.error("Failed to load highlights", e);
      setSavedHighlights([]);
    }
  }, [selectedTranscriptionId]);

  useEffect(() => {
    loadHighlights();
  }, [loadHighlights, selectedTranscriptionId]);

  /* ---------------------- Handlers ---------------------- */
  const handleTranscriptionChange = (event) => {
    const transcriptionId = event.target.value;
    setSelectedTranscriptionId(transcriptionId);
    if (transcriptionId) {
      loadTranscriptionText(parseInt(transcriptionId, 10));
    } else {
      setSelectedTranscriptionText("");
    }
  };

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
        { method: "DELETE" }
      );
      if (response.ok) {
        const refreshResponse = await fetch(
          API_ENDPOINTS.listProjectTranscriptions(activeProjectId)
        );
        if (refreshResponse.ok) {
          const data = await refreshResponse.json();
          setTranscriptions(data);
          setSelectedTranscriptionId(null);
          setSelectedTranscriptionText("");
          setEditedText("");
          setIsEditing(false);
        }
        console.log("Transcription deleted successfully");
      } else {
        const errorData = await response.json();
        console.error("Failed to delete transcription:", errorData);
        alert("Failed to delete transcription. Please try again.");
      }
    } catch (error) {
      console.error("Error deleting transcription:", error);
      alert("An error occurred while deleting the transcription. Please try again.");
    } finally {
      setDeleting(false);
    }
  };

  const handleEditToggle = () => {
    if (isEditing) {
      setEditedText("");
      setIsEditing(false);
    } else {
      setEditedText(selectedTranscriptionText);
      setIsEditing(true);
    }
  };

  const handleSaveTranscription = async () => {
    if (!selectedTranscriptionId || !activeProjectId || !editedText.trim()) return;
    try {
      setSaving(true);
      const response = await fetch(
        API_ENDPOINTS.updateProjectTranscription(activeProjectId, selectedTranscriptionId),
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: editedText }), // API expects TranscriptionRequest
        }
      );
      if (response.ok) {
        setSelectedTranscriptionText(editedText);
        setIsEditing(false);
        setEditedText("");
        console.log("Transcription saved successfully");
      } else {
        const errorData = await response.json();
        console.error("Failed to save transcription:", errorData);
        alert("Failed to save transcription. Please try again.");
      }
    } catch (error) {
      console.error("Error saving transcription:", error);
      alert("An error occurred while saving the transcription. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleHighlightText = async () => {
    if (!selectedTranscriptionId) return;
    const container = document.getElementById("transcription-display");
    if (!container) return;

    const plain = toPlainText(displayText);
    const selInfo = getSelectionOffsets(container, plain);
    if (!selInfo) return;

    try {
      // Your /highlights endpoint takes primitive params (no Pydantic model),
      // so send as form or query-params. We'll use form-encoded here.
      const body = new URLSearchParams({
        transcription_id: String(selectedTranscriptionId),
        start: String(selInfo.start),
        end: String(selInfo.end),
        color: highlightColor,
        comment: "",
      });

      const url = API_ENDPOINTS.HIGHLIGHTS_ADD || "/highlights/";
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      if (!res.ok) throw new Error(await res.text());
      // Optimistic: append the new highlight
      setSavedHighlights((prev) => [
        {
          id: crypto.randomUUID?.() ?? String(Date.now()),
          start: selInfo.start,
          end: selInfo.end,
          color: highlightColor,
          comment: "",
        },
        ...prev,
      ]);

      // Clear selection
      const sel = window.getSelection?.();
      sel?.removeAllRanges?.();
    } catch (e) {
      console.error("Failed to save highlight", e);
      alert("Failed to save highlight.");
    }
  };

  const handleHighlightColorChange = (color) => setHighlightColor(color);

  const handleDownloadTranscription = async () => {
    const textToDownload =
      selectedTranscriptionText ||
      (transcriptionDataObject ? transcriptionDataObject.transcription : "");
    if (!textToDownload) {
      console.warn("No transcription to download");
      return;
    }
    try {
      const downloadData = new FormData();
      downloadData.append("final_output", textToDownload);
      downloadData.append(
        "filename",
        `transcription_${selectedTranscriptionId || "default"}.txt`
      );
      const response = await fetch(API_ENDPOINTS.DOWNLOAD, {
        method: "POST",
        body: downloadData,
      });
      if (!response.ok) {
        throw new Error(
          `HTTP error! status: ${response.status} - ${response.statusText}`
        );
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.style.display = "none";
      link.href = url;
      link.download = `transcription_${selectedTranscriptionId || "default"}.txt`;
      document.body.appendChild(link);
      link.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (error) {
      console.error("An unexpected error occurred during download: ", error);
    }
  };

  /* ---------------------- Display text logic ---------------------- */
  const shouldShowUploadedTranscription =
    transcriptionDataObject &&
    transcriptionDataObject.project_id &&
    transcriptionDataObject.project_id.toString() === activeProjectId?.toString();

  const displayText =
    selectedTranscriptionText ||
    (shouldShowUploadedTranscription ? transcriptionDataObject.transcription : "") ||
    "Transcribed interview text will go here.";

  /* -------------------------------- Render -------------------------------- */
  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4 flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-center mb-2 font-sora">
        <div className="flex items-center gap-3">
          <h3 className="text-lg text-white font-bold">Transcription</h3>
          <select
            value={selectedTranscriptionId || ""}
            onChange={handleTranscriptionChange}
            disabled={loading || transcriptions.length === 0}
            className="bg-slate-700 text-white text-sm px-3 py-1 rounded-md border border-slate-600 focus:border-indigo-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="" disabled>
              {loading
                ? "Loading..."
                : transcriptions.length === 0
                ? "No transcriptions"
                : "Select transcription"}
            </option>
            {transcriptions.map((t) => (
              <option key={t.transcription_id} value={t.transcription_id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex gap-3">
          <button
            className={`text-white text-sm px-4 py-2 rounded-md flex items-center gap-2 ${
              isEditing ? "bg-green-600 hover:bg-green-700" : "bg-indigo-600 hover:bg-indigo-700"
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

      {/* Content */}
      <div className="bg-slate-700 rounded-lg p-3 flex-1 flex flex-col min-h-0">
        {!isEditing && selectedTranscriptionId && (
          <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-600">
            <span className="text-xs text-slate-400">Highlight:</span>
            <div className="flex gap-1">
              {["yellow", "lightblue", "lightgreen", "pink", "orange"].map((color) => (
                <button
                  key={color}
                  className={`w-4 h-4 rounded border-2 ${
                    highlightColor === color ? "border-white" : "border-slate-500"
                  }`}
                  style={{ backgroundColor: color }}
                  onClick={() => setHighlightColor(color)}
                  aria-label={`Select ${color} highlight color`}
                />
              ))}
            </div>
            <button
              className="bg-transparent border-0 text-slate-400 cursor-pointer p-1 ml-2 transition-colors hover:text-slate-200"
              aria-label="Save highlight for selected text"
              onClick={handleHighlightText}
              title="Highlight selection"
            >
              <i className="bi bi-highlighter" aria-hidden="true"></i>
            </button>
          </div>
        )}

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
              id="transcription-display"
              className="text-sm text-gray-300 leading-6 whitespace-pre-wrap"
            >
              {renderWithHighlights(toPlainText(displayText), savedHighlights)}
            </div>
          )}
        </div>

        <div className="flex justify-end mt-2">
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
