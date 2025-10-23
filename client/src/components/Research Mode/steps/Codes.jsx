import React, { useState,useEffect,useRef  } from 'react';


function CodesToolBar({ codes, setCodes, setPhase, researchQuestion }) {
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

      <p className="text-sm mb-2 bg-slate-700 rounded-xl p-1 px-4 py-1 italic">'{researchQuestion}'</p>
      <div className="flex justify-left gap-2">
        <button className="bg-slate-900 px-4 py-1 rounded-xl text-sm">
          Add Code
        </button>
        <button className="bg-slate-900 px-4 py-1 rounded-xl text-sm">
          Refresh
        </button>   
      </div>
    </div>
  );
}

function CodesList({ codes }) {
  return (
    <div className="overflow-y-auto max-h-[70vh] bg-slate-900 rounded-xl mt-2 py-1 px-1">
      {Object.entries(codes).map(([codeName, quotes]) => (
        <CodeCard key={codeName} codeName={codeName} quotes={quotes} />
      ))}
    </div>
  );
}

function CodeCard({ codeName, quotes }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="rounded-xl p-2">
      {/* Header Row */}
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
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

export default function Codes({ codes, setCodes, setPhase, researchQuestion, onNext}) {

  useEffect(() => {
    if (Object.keys(codes).length === 0) {
      const dummyCodes = {
        "Code 1": ["Sample text segment 1", "Sample text segment 2"],
        "Code 2": ["Sample text segment 3"],
        "Code 3": ["Sample text segment 4", "Sample text segment 5", "Sample text segment 6"]
      };
      setCodes(dummyCodes);
    }
  }, [codes, setCodes]);

  return (
    <div>
      <CodesToolBar
        codes={codes}
        setCodes={setCodes}
        setPhase={setPhase}
        researchQuestion={researchQuestion}
      />
      <CodesList codes={codes} />
      <button
        onClick={onNext}
        className={"mt-0 px-4 py-2 rounded text-white w-full bg-indigo-600 hover:bg-indigo-700"}
        >
        Generate Themes
      </button>
    </div>
  )
}
