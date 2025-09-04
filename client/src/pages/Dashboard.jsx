import React, { useState}from 'react';
import UploadAudioCard from '../components/UploadAudioCard';
import AnalysisSteps from '../components/AnalysisSteps';
import TranscriptionSection from '../components/TranscriptionSection';
import AIAssistant from '../components/AIAssistant';

/**
 * Dashboard Component
 * 
 * Main application layout with three-column design:
 * - Left sidebar for file upload and analysis steps
 * - Central area for transcription content
 * - Right sidebar for AI assistant chat
 */
const Dashboard = () => {
  const [transcriptionData, setTranscriptionData] = useState(null);
  
  const handleTranscriptionComplete = (data) => {
    setTranscriptionData(data);
  };

  return (
    /* Main container with full height */
    <div className="flex h-full">
      {/* Grid container for three-column layout */}
      <div className="flex-1 min-h-0 grid h-full gap-4 grid-cols-[1fr_2fr_1fr]">
        {/* 
          Left Sidebar (1fr width)
          Contains upload functionality and analysis steps 
        */}
        <div className="flex flex-col gap-4 h-full min-h-0">
          {/* File upload card */}
          <UploadAudioCard onTranscriptionComplete={handleTranscriptionComplete}/>
          
          {/* Analysis workflow steps */}
          <AnalysisSteps />
        </div>
        
        {/* 
          Main Content Area (2fr width - takes twice the space of sidebars)
          Primary workspace for transcription editing 
        */}
        <div className="flex flex-col h-full min-h-0">
          <TranscriptionSection 
            transcriptionData={transcriptionData}
            onTranscriptionUploaded={handleTranscriptionComplete}
          />
        </div>
        
        {/* 
          Right Sidebar (1fr width)
          AI Assistant chat interface 
        */}
        <div className="flex flex-col h-full min-h-0">
          <AIAssistant />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;