import React, { useState, useCallback } from "react";
import ProjectDetail from "../components/ProjectDetail";
import AIPromptDetail from "../components/AIPromptDetail";
import HighlightDetail from "../components/HighlightDetail";
import { useProject } from "../contexts/ProjectContext";
import { Link, useNavigate } from 'react-router-dom';



const Setting = () => {
  const { activeProject, loading } = useProject();

  const navigate = useNavigate();

  const [additionalInstructions, setAdditionalInstructions] = useState("");

  const [highlightColors, setHighlightColors] = useState([ // default highlight colours
    { id: 1, color: "#E895D6", label: "Important", weight: 3 },
  ]);

  const handleColorChange = (id, field, value) => {
    setHighlightColors((prev) =>
      prev.map((h) =>
        h.id === id ? { ...h, [field]: value } : h
      )
    );
  };

  const handleAddColor = () => {
    setHighlightColors((prev) => [
      ...prev,
      {
        id: Date.now(),
        color: "#000000",
        label: "New highlight",
        weight: 1,
      },
    ]);
  };

  const handleRemoveColor = (id) => {
    setHighlightColors((prev) => prev.filter((h) => h.id !== id));
  };

  if (loading) {
    return <div className="p-6">Loading project...</div>;
  }

  if (!activeProject) {
    return <div className="p-6">No project selected</div>;
  }

  const handleInstructionsChange = useCallback((field, value) => {
    setAdditionalInstructions(value);
  }, []);

  return (
    <div className="max-w-7xl mx-auto p-6 bg-slate-800 rounded-lg">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-200 mb-2">Settings</h1>
          <p className="text-slate-500">Configure your project settings</p>
        </div>
        <button
          onClick={() => navigate(-1)}
          className="flex items-center justify-center p-3 rounded-lg text-white transition hover:bg-indigo-700"
        >

          <svg
            fill="currentColor"
            xmlns="http://www.w3.org/2000/svg"
            width="25px"
            height="25px"
            viewBox="0 0 52 52"
          >
            <path d="M30.3,12.6c10.4,0,18.9,8.4,18.9,18.9s-8.5,18.9-18.9,18.9h-8.2c-0.8,0-1.3-0.6-1.3-1.4v-3.2
              c0-0.8,0.6-1.5,1.4-1.5h8.1c7.1,0,12.8-5.7,12.8-12.8s-5.7-12.8-12.8-12.8H16.4c0,0-0.8,0-1.1,0.1c-0.8,0.4-0.6,1,0.1,1.7l4.9,4.9
              c0.6,0.6,0.5,1.5-0.1,2.1L18,29.7c-0.6,0.6-1.3,0.6-1.9,0.1l-13-13c-0.5-0.5-0.5-1.3,0-1.8L16,2.1c0.6-0.6,1.6-0.6,2.1,0l2.1,2.1
              c0.6,0.6,0.6,1.6,0,2.1l-4.9,4.9c-0.6,0.6-0.6,1.3,0.4,1.3c0.3,0,0.7,0,0.7,0L30.3,12.6z"/>
          </svg>

        </button>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-7 gap-8">
        <div className="md:col-span-2">
          <ProjectDetail project={activeProject} />
        </div>


        <div className="md:col-span-3">
          <HighlightDetail
            highlightColors={highlightColors}
            onColorChange={handleColorChange}
            onAddColor={handleAddColor}
            onRemoveColor={handleRemoveColor}
          />
        </div>

        <div className="md:col-span-2">
          <AIPromptDetail additionalInstructions={additionalInstructions} onInputChange={handleInstructionsChange} />
        </div>
       
      </div>
      <div className="flex justify-center mt-10">
        <button
          onClick={() => console.log("Saving changes...")} 
          className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
};

export default Setting;
