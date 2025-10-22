import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import NavBar from './components/NavBar';
import SettingsNavbar from './components/SettingsNavbar';
import Dashboard from './pages/Dashboard';
import Setting from './pages/Setting';
import { ProjectProvider } from './contexts/ProjectContext';
import { ChatProvider } from './contexts/ChatContext';

function AppContent() {
  const location = useLocation();
  const isSettingsPage = location.pathname.startsWith('/settings');

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-white">
      {isSettingsPage ? <SettingsNavbar /> : <NavBar />}
      <main className="flex-1 min-h-0 overflow-hidden max-w-[1600px] w-full mx-auto p-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/settings" element={<Setting />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <ProjectProvider>
      <ChatProvider>
        <Router>
          <AppContent />
        </Router>
      </ChatProvider>
    </ProjectProvider>
  );
}
