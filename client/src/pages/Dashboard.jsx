import React, { useState, useEffect } from 'react';
import UploadAudioCard from '../components/UploadAudioCard';
import AnalysisSteps from '../components/AnalysisSteps';
import TranscriptionSection from '../components/TranscriptionSection';
import AIAssistant from '../components/AIAssistant';
import { API_ENDPOINTS } from '../config/api';


const Dashboard = () => {
  const [transcriptionData, setTranscriptionData] = useState(null);
  const [collections, setCollections] = useState([]);
  const [activeCollection, setActiveCollection] = useState('');

  useEffect(() => {
    const fetchCollections = async () => {
      try {
        const resp = await fetch(API_ENDPOINTS.COLLECTIONS);
        const data = await resp.json();
        const names = (data.collections || []).filter((n) => n && !n.startsWith('.internal'));
        setCollections(names);
        if (names.length && !activeCollection) setActiveCollection(names[0]);
      } catch (e) {
        console.error('Failed to load collections', e);
      }
    };
    fetchCollections();
  }, []);

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

        {/* Main Content Area with tabs */}
        <div className="flex flex-col h-full min-h-0">
          {/* Tabs */}
          <div className="flex gap-2 mb-2 overflow-x-auto">
            {collections.map((name) => (
              <button
                key={name}
                className={`px-3 py-1 rounded-md border ${activeCollection === name ? 'bg-indigo-600 text-white border-indigo-500' : 'bg-slate-700 text-slate-200 border-slate-600 hover:bg-slate-600'}`}
                onClick={() => setActiveCollection(name)}
              >
                {name}
              </button>
            ))}
            {!collections.length && (
              <div className="text-slate-400">No collections found. Add PDFs to papers/ and re-ingest.</div>
            )}
          </div>

          {/* Active transcript */}
          {activeCollection && (
            <TranscriptionSection transcriptionData={transcriptionData} collectionName={activeCollection} />
          )}
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