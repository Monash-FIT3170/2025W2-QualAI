import React, { useState } from 'react';
import UploadAudioCard from '../components/UploadAudioCard';
import AnalysisSteps from '../components/AnalysisSteps';
import TranscriptionSection from '../components/TranscriptionSection';
import AIAssistant from '../components/AIAssistant';


const Dashboard = () => {
  const [transcriptionData, setTranscriptionData] = useState(null);

  const handleTranscriptionComplete = (dataObj) => {
    // We expect a plain JS object: { filename, transcription }
    if (!dataObj || typeof dataObj !== 'object' || !dataObj.transcription) {
      console.error('Invalid transcription data received');
      return;
    }
    setTranscriptionData(dataObj);
  };

  return (
    /* Main container with full height */
    <div className="flex h-full">
      {/* Grid container for three-column layout */}
      <div className="flex-1 min-h-0 grid h-full gap-4 grid-cols-[1fr_2fr_1fr]">
        {/* Left Sidebar */}
        <div className="flex flex-col gap-4 h-full min-h-0">
          <UploadAudioCard onTranscriptionComplete={handleTranscriptionComplete} />
          <AnalysisSteps />
        </div>

        {/* Main Content Area */}
        <div className="flex flex-col h-full min-h-0">
          <TranscriptionSection transcriptionData={transcriptionData} />
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