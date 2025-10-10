import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Dashboard from './pages/Dashboard';
import Setting from './pages/Setting';
import { ProjectProvider } from './contexts/ProjectContext';

/**
 * Main Application Component
 */
function App() {
  return (
    <ProjectProvider>
      <Router>
        <div className="flex flex-col h-screen bg-slate-900 text-white">
          <NavBar />
          <main className="flex-1 min-h-0 overflow-hidden max-w-[1600px] w-full mx-auto p-4">
            <Routes>
              <Route 
                path="/" 
                element={
                  <div className="h-full flex flex-col">
                    <Dashboard />
                  </div>
                } 
              />
              <Route 
                path="/settings" 
                element={
                  <div className="h-full flex flex-col">
                    <Setting />
                  </div>
                } 
              />
            </Routes>
          </main>
        </div>
      </Router>
    </ProjectProvider>
  );
}

export default App;