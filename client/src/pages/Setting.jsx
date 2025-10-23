import { useState, useCallback, useRef } from "react";
import ProjectDetail from "../components/ProjectDetail";
import AIPromptDetail from "../components/AIPromptDetail";
import HighlightDetail from "../components/HighlightDetail";
import { useProject } from "../contexts/ProjectContext";

const Setting = () => {
  const { activeProject, loading } = useProject();
  const projectDetailRef = useRef(null);
  const highlightDetailRef = useRef(null); 

  const [additionalInstructions, setAdditionalInstructions] = useState("");

  const handleInstructionsChange = useCallback((field, value) => {
    setAdditionalInstructions(value);
  }, []);


  const handleSaveAll = async () => {
    if (projectDetailRef.current) {
      await projectDetailRef.current.saveProject();
    }
    if (highlightDetailRef.current) {
      await highlightDetailRef.current.saveHighlights();
    }

  };

  if (loading) {
    return <div className="p-6">Loading project...</div>;
  }

  if (!activeProject) {
    return <div className="p-6">No project selected</div>;
  }

  return (
    <div className="max-w-7xl mx-auto p-6 bg-slate-800 rounded-lg">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-200 mb-2">Settings</h1>
          <p className="text-slate-500">Configure your project settings</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-7 gap-8">
        <div className="md:col-span-2">
          <ProjectDetail ref={projectDetailRef} project={activeProject} />
        </div>

        <div className="md:col-span-3">
          <HighlightDetail
            ref={highlightDetailRef}
            projectId={activeProject?.project_id}
          />
        </div>

        <div className="md:col-span-2">
          <AIPromptDetail
            additionalInstructions={additionalInstructions}
            onInputChange={handleInstructionsChange}
          />
        </div>
      </div>

      <div className="flex justify-center mt-10">
        <button
          onClick={handleSaveAll}
          className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
};

export default Setting;
