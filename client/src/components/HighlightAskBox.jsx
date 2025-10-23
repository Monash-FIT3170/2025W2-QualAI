// src/components/HighlightAskBox.jsx
import React, { useEffect, useMemo, useState } from "react";
import { API_ENDPOINTS } from "../config/api";

const COLOR_ORDER = ["yellow", "lightblue", "lightgreen", "pink", "orange", "purple", "red", "teal"];

function uniqueColorsFromHighlights(highlights) {
  const s = new Set();
  (highlights || []).forEach((h) => h?.color && s.add(h.color));
  return Array.from(s);
}

export default function HighlightAskBox({
  projectId,
  transcriptionId,
  transcriptionText,   // plain string of the current transcription
  highlights,           // raw array returned by GET /highlights/{tid}
}) {
  const [availableColors, setAvailableColors] = useState([]);
  const [selectedColors, setSelectedColors] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [mode, setMode] = useState("offline"); // "offline" (Ollama CPU) or "online" (Gemini)

  // Discover colors from current highlights, keep a stable order
  useEffect(() => {
    const fromHighlights = uniqueColorsFromHighlights(highlights);
    const sorted = [...fromHighlights].sort(
      (a, b) => COLOR_ORDER.indexOf(a) - COLOR_ORDER.indexOf(b)
    );
    setAvailableColors(sorted);
    setSelectedColors(sorted); // default: all selected
  }, [highlights]);

  // Index highlights and build a stitched preview of selected ranges
  const filteredSegments = useMemo(() => {
    if (!Array.isArray(highlights) || !transcriptionText) return [];
    const chosen = new Set(selectedColors);
    return highlights
      .filter((h) => chosen.has(h.color))
      .map((h) => {
        const start = Math.max(0, Math.min((h.startOffset ?? h.start ?? 0), transcriptionText.length));
        const end   = Math.max(0, Math.min((h.endOffset   ?? h.end   ?? 0), transcriptionText.length));
        const text  = start < end ? transcriptionText.slice(start, end) : "";
        return {
          id: h.highlight_id ?? h.id,
          start, end, color: h.color,
          text,
        };
      })
      .filter((s) => s.text.trim().length > 0);
  }, [highlights, transcriptionText, selectedColors]);

  const contextPreview = useMemo(() => {
    if (!filteredSegments.length) return "";
    return filteredSegments
      .map((s) => `• (${s.color}) ${s.text}`)
      .join("\n");
  }, [filteredSegments]);

  const toggleColor = (c) => {
    setSelectedColors((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]
    );
  };

  const askAI = async () => {
    if (!projectId || !question.trim()) {
      alert("Select a project and enter a question.");
      return;
    }

    try {
      setBusy(true);
      setAnswer("");

      const res = await fetch(API_ENDPOINTS.ASK_HIGHLIGHTS, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          transcription_id: transcriptionId,
          colors: selectedColors,      // e.g. ["orange","yellow"]
          question,
          mode,                        // "offline" (CPU) or "online"
        }),
      });

      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(txt || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setAnswer(data.answer || data.output || JSON.stringify(data));
    } catch (e) {
      console.error(e);
      alert("Failed to get answer from AI.");
    } finally {
      setBusy(false);
    }
  };

  // Small helper: count per color
  const countByColor = useMemo(() => {
    const counts = {};
    (highlights || []).forEach((h) => {
      const c = h?.color;
      if (!c) return;
      counts[c] = (counts[c] || 0) + 1;
    });
    return counts;
  }, [highlights]);

  return (
    <div className="bg-slate-800 rounded-lg p-3">
      {/* Controls row */}
      <div className="flex flex-wrap items-center gap-2 mb-2">
        {/* Color chips */}
        <div className="flex flex-wrap gap-2">
          {availableColors.length === 0 ? (
            <span className="text-xs text-slate-400">No highlights yet.</span>
          ) : (
            availableColors.map((c) => (
              <button
                key={c}
                onClick={() => toggleColor(c)}
                className={`px-2 py-1 text-xs rounded border flex items-center gap-1 ${
                  selectedColors.includes(c)
                    ? "border-white text-white"
                    : "border-slate-500 text-slate-300"
                }`}
                style={{ background: selectedColors.includes(c) ? c : "transparent" }}
                title={`Toggle ${c}`}
              >
                <span className="font-medium">{c}</span>
                {countByColor[c] ? (
                  <span className="opacity-80">({countByColor[c]})</span>
                ) : null}
              </button>
            ))
          )}
        </div>

        {/* Mode switch (CPU vs online) */}
        <div className="ml-auto flex items-center gap-2">
          <label className="text-xs text-slate-300">Mode:</label>
          <select
            className="bg-slate-700 text-white text-xs px-2 py-1 rounded-md border border-slate-600"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
          >
            <option value="offline">Offline (CPU)</option>
            <option value="online">Online (Gemini)</option>
          </select>
        </div>
      </div>

      {/* Question input */}
      <textarea
        className="w-full bg-slate-700 text-sm text-gray-200 rounded p-2 outline-none"
        rows={3}
        placeholder="Ask a question about the selected highlight colors…"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      {/* Footer: stats + Ask button */}
      <div className="flex justify-between items-center mt-2">
        <span className="text-xs text-slate-400">
          {filteredSegments.length
            ? `${filteredSegments.length} snippet${filteredSegments.length > 1 ? "s" : ""} selected`
            : "No snippets selected"}
        </span>
        <button
          onClick={askAI}
          className={`px-3 py-2 text-sm rounded-md text-white ${
            busy ? "bg-slate-600 opacity-70" : "bg-indigo-600 hover:bg-indigo-700"
          }`}
          disabled={busy}
        >
          {busy ? "Thinking…" : "Ask AI"}
        </button>
      </div>

      {/* Optional: context preview */}
      {contextPreview && (
        <div className="mt-3 bg-slate-700 rounded p-2">
          <div className="text-xs text-slate-300 whitespace-pre-wrap">{contextPreview}</div>
        </div>
      )}

      {/* Answer */}
      {answer && (
        <div className="mt-3 bg-slate-700 rounded p-3">
          <div className="text-sm text-white whitespace-pre-wrap">{answer}</div>
        </div>
      )}
    </div>
  );
}
