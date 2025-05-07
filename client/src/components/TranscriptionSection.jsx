import React from 'react';
import '../assets/styles/TranscriptionSection.css';

const TranscriptionSection = () => {
  return (
    <div className="transcription-card">
      <h3 className="card-title">Transcription</h3>
      <div className="transcription-content">
        <div className="transcription-text">
          <p>
            This is the transcribed text from the audio interview. You can highlight sections
            and add codes to them.
          </p>
        </div>
        <div className="transcription-actions">
          <button className="action-btn">
            <i className="icon-code"></i>
          </button>
          <button className="action-btn">
            <i className="icon-highlighter"></i>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TranscriptionSection;