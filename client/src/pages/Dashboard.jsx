import React from 'react';
import UploadAudioCard from '../components/UploadAudioCard';
import AnalysisSteps from '../components/AnalysisSteps';
import TranscriptionSection from '../components/TranscriptionSection';
import AIAssistant from '../components/AIAssistant';
import '../assets/styles/Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        {/* Left Sidebar */}
        <div className="sidebar">
          <UploadAudioCard />
          <AnalysisSteps />
        </div>
        
        {/* Main Content Area */}
        <div className="main-content">
          <TranscriptionSection />
        </div>
        
        {/* Right Sidebar - Chat Interface */}
        <div className="chat-sidebar">
          <AIAssistant />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;