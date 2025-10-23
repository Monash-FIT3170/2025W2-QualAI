import { useState } from "react";
import AIAssistant from "./AIAssistant";
import ResearchMode from "./Research Mode/ResearchMode";

export default function AssistantContainer() {
  const [activeMode, setActiveMode] = useState("chat");

  return (
    <div className="h-full bg-slate-900 rounded-xl p-1 flex flex-col w-full">
      {/* Tab Bar */}
      <div className="flex mb-4 border-b border-slate-700">
        <button
          onClick={() => setActiveMode("chat")}
          className={`flex-1 py-2 text-center font-medium ${
            activeMode === "chat" ? "text-indigo-400 border-b-2 border-indigo-400" : "text-slate-400"
          }`}
        >
          Chat Mode
        </button>
        <button
          onClick={() => setActiveMode("research")}
          className={`flex-1 py-2 text-center font-medium ${
            activeMode === "research" ? "text-indigo-400 border-b-2 border-indigo-400" : "text-slate-400"
          }`}
        >
          Research Mode
        </button>
      </div>

      {/* Shared content area */}
      <div className="flex-1">
        {activeMode === "chat" ? <AIAssistant /> : <ResearchMode />}
      </div>
    </div>
  );
}
