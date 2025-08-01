import React from 'react';

/**
 * Mock data for analysis steps
 * @type {Array<Object>}
 */
const mockSteps = [
  {
    icon: 'bi bi-mic',               
    title: 'Upload Audio',                
    description: 'Upload your interview recordings' 
  },
  {
    icon: 'bi bi-file-earmark-text',
    title: 'Transcribe',
    description: 'Convert speech to text'
  },
  {
    icon: 'bi bi-code',
    title: 'Code',
    description: 'Identify key themes and patterns'
  },
  {
    icon: 'bi bi-diagram-3',
    title: 'Analyse',
    description: 'Ask AI Assistant for feedback'
  }
];

/**
 * Component that displays the research analysis workflow steps
 * @param {Object} props - Component props
 * @param {Array<Object>} [props.steps=mockSteps] - Array of step objects
 */
const AnalysisSteps = ({ steps = mockSteps }) => {
  return (
    /* Main container with card styling */
    <div className="bg-slate-800 rounded-xl shadow-md p-4 flex-1">
      {/* Section header */}
      <h2 className="text-lg font-semibold text-white mb-4">Analysis Steps</h2>
      
      {/* Steps list container */}
      <div className="flex flex-col gap-6">
        {steps.map((step, index) => (
          /* Individual step item */
          <div className="flex items-start" key={index}>
            {/* Step icon in circular container */}
            <div className="flex items-center justify-center w-8 h-8 bg-indigo-600 rounded-full mr-3 flex-shrink-0">
              <i className={step.icon} aria-hidden="true"></i>
            </div>
            
            {/* Step text content */}
            <div className="flex-1">
              {/* Step title */}
              <h3 className="text-sm font-medium text-slate-200 mb-1">
                {step.title}
              </h3>
              {/* Step description */}
              <p className="text-xs text-slate-400">
                {step.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnalysisSteps;