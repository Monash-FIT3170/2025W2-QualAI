import { API_ENDPOINTS } from '../../../config/api';
import { useProject } from '../../../contexts/ProjectContext';

import React, { useState, useEffect, useRef  } from 'react';

export default function Landing({ onNext, setResearchQuestion}) {

  const [input, setInput] = useState("");
  const [mode, setMode] = useState('online');
  const [template, setTemplate] = useState('research');
  const { activeProjectId } = useProject();

  const handleChange = (e) => {
    setInput(e.target.value);
  };

  const handleNext = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput) return;

    try {
      const response = await fetch(API_ENDPOINTS.GENERATE_CODE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: trimmedInput,
          mode: mode,
          project: activeProjectId || 'default',
          template: template
      }),
    });

    if (!response.ok) throw new Error(await response.text() || 'Error fetching response from AI');

    const data = await response.json();
    const aiResponse = data.response ?? data.message ?? "AI could not generate a proper response.";

    setResearchQuestion(trimmedInput);
    onNext();

    } catch (error) {
      console.error("Error during AI request:", error);
      alert("There was an error processing your request. Please try again.");
    }
  };


  return (
    <div className="flex flex-col h-full items-center text-white">
      <h2 className="text-xl font-semibold mb-4">Research Mode</h2>
      <p className="text-white text-center text-slate-400 text-center mb-4">
        Perform manual guided analysis on your project with the help of AI.
        
        Enter a research question to get started!
      </p>

      <input
        type="text"
        value={input}
        onChange={handleChange}
        placeholder="Enter your research question!"
        className="px-3 py-2 rounded bg-slate-600 text-white w-full max-w-md mb-4 focus:outline-none focus:ring-1 focus:ring-indigo-500 mt-auto"
      />

      <button
        disabled={input.trim() === ""}
        onClick={handleNext}
        className={`mt-0 px-4 py-2 rounded text-white w-full transition-colors
          ${input.trim() 
            ? "bg-indigo-600 hover:bg-indigo-700"        // enabled
            : "bg-indigo-600 opacity-50 cursor-not-allowed" // disabled
          } max-w-md`}
        >
        Next
      </button>
    </div>
  );
}