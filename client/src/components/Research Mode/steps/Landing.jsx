import React, { useState,useEffect,useRef  } from 'react';

export default function Landing({ onNext, setResearchQuestion }) {

  const [input, setInput] = useState("");

  const handleChange = (e) => {
    setInput(e.target.value);
  };

  const handleNext = () => {
    setResearchQuestion(input);
    onNext();
  };


  return (
    <div className="flex flex-col h-full justify-center items-center text-white">
      <h2 className="text-xl font-semibold mb-4">Research Mode</h2>
      <p className="text-white text-center text-slate-400 text-center mb-4">
        Description here...
        Enter a research question to get started!
      </p>

      <input
        type="text"
        value={input}
        onChange={handleChange}
        placeholder="Enter your research question"
        className="px-3 py-2 rounded bg-slate-600 text-white w-full max-w-md mb-4 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />

      <button
        disabled={input.trim() === ""}
        onClick={onNext}
        className={`mt-4 px-4 py-2 rounded text-white w-full transition-colors
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