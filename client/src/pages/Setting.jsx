import React, { useState, useCallback } from "react";
import ProjectDetail from "../components/ProjectDetail";
import AIPromptDetail from "../components/AIPromptDetail";
import HighlightDetail from "../components/HighlightDetail";
import { useProject } from "../contexts/ProjectContext";

const Setting = () => {
  const { activeProject, loading } = useProject();

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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-200 mb-2">Settings</h1>
        <p className="text-slate-500">Configure your project settings</p>
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
          onClick={() => console.log("Saving changes...")} // replace with your actual save logic
          className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
};

export default Setting;
