import React from 'react';
import UploadAudioCard from '../components/UploadAudioCard';
import AnalysisSteps from '../components/AnalysisSteps';
import TranscriptionSection from '../components/TranscriptionSection';
import AIAssistant from '../components/AIAssistant';

const Dashboard = () => {
  return (
    <div className="h-full">
      <div className="h-full gap-4 grid grid-cols-[1fr_2fr_1fr]">
        {/* Left Sidebar */}
        <div className="flex-col gap-4">
          <UploadAudioCard />
          <AnalysisSteps />
        </div>
        
        {/* Main Content Area */}
        <div className="flex flex-col gap-4">
          <TranscriptionSection />
        </div>
        
        {/* Right Sidebar - Chat Interface */}
        <div className="h-full">
          <AIAssistant />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;