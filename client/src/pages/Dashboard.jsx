import React, { useState, useCallback } from 'react';
import UploadAudioCard from '../components/UploadAudioCard';
import AnalysisSteps from '../components/AnalysisSteps';
import TranscriptionSection from '../components/TranscriptionSection';
import AIAssistant from '../components/AIAssistant';


const Dashboard = () => {
  const [transcriptionData, setTranscriptionData] = useState(null);
  
  // Use useCallback to prevent function recreation on every render
  const handleTranscriptionComplete = useCallback((data) => {
    setTranscriptionData(data);
  }, []);

  return (
    /* Main container with full height */
    <div className="flex h-full">
      {/* Grid container for three-column layout */}
      <div className="flex-1 min-h-0 grid h-full gap-4 grid-cols-[1fr_2fr_1fr]">
        {/* Left Sidebar */}
        <div className="flex flex-col gap-4 h-full min-h-0">
          {/* File upload card */}
          <UploadAudioCard onTranscriptionComplete={handleTranscriptionComplete}/>
          
          {/* Analysis workflow steps */}
          <AnalysisSteps />
        </div>

        {/* Main Content Area */}
        <div className="flex flex-col h-full min-h-0">
          <TranscriptionSection 
            transcriptionData={transcriptionData}
            onTranscriptionUploaded={handleTranscriptionComplete}
          />
        </div>

        {/* Right Sidebar */}
        <div className="flex flex-col h-full min-h-0">
          <AIAssistant />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;