import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import './assets/styles/App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <NavBar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            {/* Add more routes as needed */}
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;