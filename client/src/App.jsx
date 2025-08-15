import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Dashboard from './pages/Dashboard';

/**
 * Main Application Component
 */
function App() {
  return (
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
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;