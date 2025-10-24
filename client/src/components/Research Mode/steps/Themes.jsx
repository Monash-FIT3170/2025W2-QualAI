import React, { useState, useEffect } from 'react';
import { useProject } from '../../../contexts/ProjectContext';
import { API_ENDPOINTS } from '../../../config/api';

function ThemesToolBar({ setPhase, onGenerateThemes, isGenerating }) {
  return (
    <div className="text-white">
      <div className="relative mb-2 flex items-center justify-between">
        <button
          onClick={() => setPhase("Codes")}
          className="text-slate-500 rounded hover:text-white text-xl font-bold"
        >
          {"<"}
        </button>
        <h2 className="text-xl font-semibold mb-1">Themes</h2>
        <button
          onClick={onGenerateThemes}
          disabled={isGenerating}
          className={`px-4 py-2 rounded ${
            isGenerating 
              ? 'bg-slate-600 cursor-not-allowed' 
              : 'bg-indigo-600 hover:bg-indigo-700'
          }`}
        >
          {isGenerating ? 'Generating...' : 'Generate Themes'}
        </button>
      </div>
    </div>
  );
}

function ThemesList({ themes, selectedTheme, onThemeSelect, onThemeDelete }) {
  return (
    <div className="flex flex-col gap-2 mb-4">
      {themes.map((theme) => (
        <div 
          key={theme.id}
          className={`flex justify-between items-center p-3 rounded ${
            selectedTheme?.id === theme.id 
              ? 'bg-indigo-700 text-white' 
              : 'bg-slate-700 hover:bg-slate-600 text-slate-200'
          }`}
        >
          <button
            onClick={() => onThemeSelect(theme)}
            className="flex-1 text-left"
          >
            {theme.name}
            <span className="text-sm text-slate-400 ml-2">
              ({theme.codes.length} codes)
            </span>
          </button>
          <button
            onClick={() => onThemeDelete(theme.id)}
            className="text-slate-400 hover:text-red-400"
            title="Delete theme"
          >
            <i className="bi bi-trash"></i>
          </button>
        </div>
      ))}
    </div>
  );
}

function ThemeDetails({ theme, codes }) {
  return theme && (
    <div className="bg-slate-800 p-4 rounded">
      <h3 className="text-lg font-semibold text-white mb-3">{theme.name}</h3>
      <div className="space-y-4">
        {theme.codes.map(codeName => {
          const code = codes.find(c => c.code === codeName);
          return code && (
            <div key={code.id} className="border-l-2 border-indigo-500 pl-3">
              <h4 className="font-medium text-slate-200 mb-2">{code.code}</h4>
              <ul className="space-y-2">
                {code.quotes.map((quote, i) => (
                  <li key={i} className="text-slate-400 text-sm">
                    "{quote}"
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function Themes({ setPhase, codes }) {
  const { activeProjectId } = useProject();
  const [themes, setThemes] = useState([]);
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Load existing themes on mount
  useEffect(() => {
    const fetchThemes = async () => {
      try {
        console.log('Fetching themes for project:', activeProjectId);
        console.log('Available codes:', codes); // Add this line
        
        const response = await fetch(API_ENDPOINTS.listProjectThemes(activeProjectId));
        const data = await response.json();
        console.log('Fetched themes:', data);
        setThemes(data.themes);
      } catch (error) {
        console.error('Error fetching themes:', error);
        alert('Error fetching themes: ' + error.message);
      }
    };
    fetchThemes();
  }, [activeProjectId, codes]); // Add codes as dependency

  const handleGenerateThemes = async () => {
    setIsGenerating(true);
    try {
      const payload = {
        project_id: activeProjectId,
        mode: 'online'  // Force online mode
      };
      
      console.log('Generating themes with payload:', payload);

      const response = await fetch(API_ENDPOINTS.GENERATE_THEMES, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Generated themes:', data);
      
      if (data.themes) {
        setThemes(data.themes);
        setSelectedTheme(null);
      }
    } catch (error) {
      console.error('Error generating themes:', error);
      alert('Error generating themes: ' + error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleThemeDelete = async (themeId) => {
    try {
      const response = await fetch(API_ENDPOINTS.deleteTheme(themeId), {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error('Failed to delete theme');
      
      setThemes(themes.filter(t => t.id !== themeId));
      if (selectedTheme?.id === themeId) {
        setSelectedTheme(null);
      }
    } catch (error) {
      console.error('Error deleting theme:', error);
    }
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      <ThemesToolBar 
        setPhase={setPhase}
        onGenerateThemes={handleGenerateThemes}
        isGenerating={isGenerating}
      />
      
      {themes.length > 0 && (
        <ThemesList
          themes={themes}
          selectedTheme={selectedTheme}
          onThemeSelect={setSelectedTheme}
          onThemeDelete={handleThemeDelete}
        />
      )}

      <div className="flex-1 overflow-y-auto">
        <ThemeDetails 
          theme={selectedTheme}
          codes={codes}
        />
      </div>
    </div>
  );
}