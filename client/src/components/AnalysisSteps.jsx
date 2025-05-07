import React from 'react';
import '../assets/styles/AnalysisSteps.css';

const AnalysisSteps = () => {
  const steps = [
    {
      icon: 'icon-microphone',
      title: 'Upload Audio',
      description: 'Upload your interview recordings'
    },
    {
      icon: 'icon-file-alt',
      title: 'Transcribe',
      description: 'Convert speech to text'
    },
    {
      icon: 'icon-code',
      title: 'Code',
      description: 'Identify key themes and patterns'
    },
    {
      icon: 'icon-project-diagram',
      title: 'Analyse',
      description: 'Ask AI Assistant for feedback'
    }
  ];

  return (
    <div className="analysis-steps-card">
      <h2 className="card-title">Analysis Steps</h2>
      <div className="steps-list">
        {steps.map((step, index) => (
          <div className="analysis-step" key={index}>
            <div className="step-icon">
              <i className={step.icon}></i>
            </div>
            <div className="step-content">
              <h3 className="step-title">{step.title}</h3>
              <p className="step-description">{step.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnalysisSteps;