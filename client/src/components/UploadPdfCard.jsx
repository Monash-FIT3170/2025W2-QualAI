import React, { useRef, useState } from "react";
import { useProject } from "../contexts/ProjectContext";
import { API_ENDPOINTS } from "../config/api";

const UploadPdfCard = () => {
  const { activeProjectId } = useProject();
  const inputRef = useRef(null);
  const [busy, setBusy] = useState(false);

  const pick = () => {
    if (!activeProjectId) {
      alert("Please select a project first.");
      return;
    }
    inputRef.current?.click();
  };

  const onPick = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!/\.pdf$/i.test(file.name)) {
      alert("Please choose a .pdf file.");
      e.target.value = "";
      return;
    }
    try {
      setBusy(true);
      const fd = new FormData();
      fd.append("project_id", String(activeProjectId));
      fd.append("file", file);

      const res = await fetch(API_ENDPOINTS.INGEST_PDF || "/ingest/pdf", {
        method: "POST",
        body: fd,
      });
      if (!res.ok) {
        const msg = await res.text().catch(() => "");
        throw new Error(msg || `Upload failed (HTTP ${res.status})`);
      }
      alert("PDF ingested. You can now query it with the AI Assistant.");
    } catch (err) {
      console.error(err);
      alert(`Upload failed: ${err.message || err}`);
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-white">Upload PDF</h3>
          <p className="text-xs text-slate-400">
            Index PDF pages into vectors for ChatPDF-style retrieval.
          </p>
        </div>
        <button
          className={`px-3 py-2 text-sm rounded-md text-white ${
            busy ? "bg-slate-600 opacity-70" : "bg-indigo-600 hover:bg-indigo-700"
          }`}
          onClick={pick}
          disabled={busy}
        >
          {busy ? "Processing…" : "Choose PDF"}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,application/pdf"
          className="hidden"
          onChange={onPick}
        />
      </div>
    </div>
  );
};

export default UploadPdfCard;
