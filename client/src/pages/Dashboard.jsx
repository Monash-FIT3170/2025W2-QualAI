import React from 'react';
import UploadAudioCard from '../components/UploadAudioCard';
import AnalysisSteps from '../components/AnalysisSteps';
import TranscriptionSection from '../components/TranscriptionSection';
import AIAssistant from '../components/AIAssistant';

const Dashboard = () => {
  return (
    <div className="flex h-full">
      <div className="flex-1 min-h-0 grid h-full gap-4 grid-cols-[1fr_2fr_1fr]">
        {/* Left Sidebar */}
        <div className="flex-1">
          <UploadAudioCard />
          <AnalysisSteps />
        </div>
        
        {/* Main Content Area */}
        <div className="flex flex-col h-full min-h-0">
          <TranscriptionSection />
        </div>
        
        {/* Right Sidebar - Chat Interface */}
        <div className="flex flex-col h-full min-h-0">
          <AIAssistant />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;