#!/usr/bin/env node

const helpText = `
🚀 QualAI Project - Available Commands
=====================================

📦 Setup & Installation:
  npm run setup          - Complete project setup (install all dependencies)
  npm run install:all    - Install Node.js and Python dependencies
  npm run setup:env      - Setup environment variables

🚀 Development (Choose one):
  npm start              - Start all services in development mode
  npm run dev            - Start all services with hot reload
  npm run dev:backend    - Start only FastAPI backend
  npm run dev:frontend   - Start only React frontend
  npm run dev:landing    - Start only landing page
  npm run dev:docker     - Start all services with Docker

🏗️ Build & Production:
  npm run build          - Build frontend and prepare for production
  npm run build:frontend - Build React frontend only
  npm run start:backend  - Start production backend
  npm run start:frontend - Start production frontend
  npm run start:landing  - Start production landing page

🧪 Testing:
  npm test               - Run Python backend tests
  npm run test:frontend  - Run frontend linting

🔧 Maintenance:
  npm run status         - Check status of all services
  npm run logs           - View Docker container logs
  npm run clean          - Clean all dependencies and containers
  npm run reset          - Complete reset and reinstall
  npm run help           - Show this help message

🌐 Access Points:
  Landing Page:          http://localhost:3000
  Frontend (React):      http://localhost:5173
  Backend (FastAPI):     http://localhost:8000
  Qdrant Dashboard:      http://localhost:6333 (Docker only)

💡 Quick Start:
  1. npm run setup      (first time only)
  2. npm start          (starts everything)
  3. Open http://localhost:3000 in your browser

📚 For more information, check the README.md file.
`;

console.log(helpText);
