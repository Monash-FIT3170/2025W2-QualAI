import React, { useState,useEffect,useRef  } from 'react';
import { API_ENDPOINTS } from '../../../config/api';
import { useProject } from '../../../contexts/ProjectContext';


function CodesToolBar({ codes, setCodes, setPhase, researchQuestion, setResearchQuestion, handleRefreshCode}) {
  return (
    <div className="text-white">
      <div className="relative mb-2 flex items-center justify-center">
        <button
          onClick={() => setPhase("Landing")}
          className="absolute left-0 text-slate-500 rounded hover:text-white text-xl font-bold"
        >
          {"<"}
        </button>
        <h2 className="text-xl font-semibold mb-1 text-center">Codes</h2>
      </div>

      <p className="text-sm text-center mb-2 rounded-xl p-1 px-4 py-1 italic">'{researchQuestion}'</p>
      <div className="flex justify-start gap-2">
        <button 
        onClick={handleRefreshCode}
        className="bg-indigo-600 hover:bg-indigo-700 px-4 py-1 rounded-xl text-sm transition-colors"
      >
        Refresh
      </button>  
      </div>
    </div>
  );
}

function CodesList({ codes, handleDeleteCode}) {
  return (
    <div className="overflow-y-auto max-h-[50vh] bg-slate-900 rounded-xl mt-2 py-1 px-1 mb-2">
      {codes.map((codeItem) => (
        <CodeCard
          codeId={codeItem.id}
          codeName={codeItem.code}
          quotes={codeItem.quotes}
          handleDeleteCode={handleDeleteCode}
        />
      ))}
    </div>
  );
}

function CodeCard({codeId, codeName, quotes, handleDeleteCode}) {
  const [isOpen, setIsOpen] = useState(false);

  const confirmDelete = () => {
    if (window.confirm(`Are you sure you want to delete the code "${codeName}"?`)) {
      handleDeleteCode(codeId);
    }
  };

  return (
    <div className="rounded-xl p-2">
      {/* Header Row */}
      <div
        className="flex justify-between gap-2 cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <button
          onClick={confirmDelete}
          className="text-red-500 text-xs mt-1 px-1"
          title="deleteCode"
        >
          <i className="bi bi-trash"></i>
        </button>
        <h3 className="text-sm text-white">{codeName}</h3>
        <span className="text-slate-300 text-sm">
          {isOpen ? "▲" : "▼"}
        </span>

      </div>

      {/* Quotes (Dropdown Section) */}
      {isOpen && (
        <ul className="mt-2 ml-3 list-disc text-slate-200">
          {quotes.map((quote, idx) => (
            <li key={idx} className="text-sm mb-1">
              "{quote}"
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Codes({ codes, setCodes, setPhase, researchQuestion, setResearchQuestion, onNext}) {
  const { activeProjectId } = useProject();

  const handleDeleteCode = async (codeId) => {
    try {
      await fetch(`${API_ENDPOINTS.deleteCode(codeId)}`, { method: "DELETE" }); 
      setCodes((prev) => prev.filter((code) => code.id !== codeId));
    } catch (error) {
      console.error("Error deleting code:", error);
    }
  };

    const handleRefreshCode = async (projectID) => {
      try {
        setResearchQuestion(""); 
        setCodes([])
        setPhase("Landing")

        const response = await fetch(API_ENDPOINTS.refreshProjectCodes(projectID), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
 
        if (!response.ok) throw new Error("Failed to refresh codes");

        const data = await response.json();
        setCodes(data.codes || []);
      } catch (error) {
        console.error(error);
      }
    };

  return (
    <div className='flex flex-col h-full'>
      <CodesToolBar
        codes={codes}
        setCodes={setCodes}
        setPhase={setPhase}
        setResearchQuestion={setResearchQuestion}
        researchQuestion={researchQuestion}
        handleRefreshCode={() => handleRefreshCode(activeProjectId)}          
      />
      <CodesList 
        codes={codes}
        handleDeleteCode={handleDeleteCode} />
      <button
        onClick={onNext}
        className={"px-4 py-2 rounded text-white w-full bg-indigo-600 opacity-50 cursor-not-allowed mt-auto"}
        >
        Generate Themes
      </button>
    </div>
  )
}
