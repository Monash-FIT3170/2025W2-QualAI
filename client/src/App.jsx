import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <div className="flex-col h-screen bg-slate-900 text-white">
        <NavBar />
        <main className="h-[90vh] flex-1 overflow-hidden max-w-[1600px] w-full mx-0-auto p-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            {/* Add more routes as needed */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;