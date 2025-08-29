# 🚀 QualAI - AI-Powered Quality Assurance Platform

A modern, full-stack quality assurance platform built with FastAPI, React, Qdrant vector database, and Docker.

## 🔗 Project Management

This project is managed using a [Notion](https://www.notion.so/Product-Backlog-Qual-AI-1c2a077291a4801ab085ffc3b73abb7e) product backlog which includes:
- **User stories**
- **Tasks**
- **Assigned agile teams**
- **Subtasks with individual assignees**
    
➡️ You can view it here: [QualAI Product Backlog](https://www.notion.so/Product-Backlog-Qual-AI-1c2a077291a4801ab085ffc3b73abb7e)

---

## 🌟 Features

- **AI-Powered Analysis**: Leverage advanced AI models for intelligent quality assessment
- **Modern Tech Stack**: FastAPI backend, React 19 frontend, Qdrant vector database
- **Docker Support**: Complete containerization with docker-compose
- **Real-time Processing**: Live audio transcription and analysis
- **Vector Search**: Semantic similarity search with Qdrant
- **Responsive Design**: Beautiful, mobile-friendly landing page
- **GitHub Pages**: Deployed landing page at `https://[username].github.io/2025W2-QualAI/`

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm 8+
- Python 3.8+ and pip
- Docker and Docker Compose (optional)

### One-Command Setup & Run
```bash
# Complete setup and start
npm run setup && npm start
```

### Manual Setup
```bash
# 1. Install dependencies
npm run install:all

# 2. Start all services
npm start
```

## 📱 Access Points

Once running, access your services at:
- **🌐 Landing Page**: https://[username].github.io/2025W2-QualAI/ (GitHub Pages)
- **⚛️ React Frontend**: http://localhost:5173  
- **🔧 FastAPI Backend**: http://localhost:8000
- **🗄️ Qdrant Dashboard**: http://localhost:6333 (Docker only)

## 🛠️ Available Commands

### Development
```bash
npm start              # Start all services
npm run dev            # Start with hot reload
npm run dev:backend    # Start only backend
npm run dev:frontend   # Start only frontend
npm run dev:landing    # Start only landing page
npm run dev:docker     # Start with Docker
```

### Production
```bash
npm run build          # Build for production
npm run start:backend  # Start production backend
npm run start:frontend # Start production frontend
npm run start:landing  # Start production landing page
```

### Maintenance
```bash
npm run status         # Check service status
npm run logs           # View Docker logs
npm run clean          # Clean dependencies
npm run reset          # Complete reset
npm run help           # Show all commands
```

## 🌐 GitHub Pages Deployment

The landing page is automatically deployed to GitHub Pages when you push to the main branch. The workflow is configured to deploy from `.github/LandingPage/` directory.

**Access your deployed landing page at:**
```
https://[username].github.io/2025W2-QualAI/
```

**To enable GitHub Pages:**
1. Go to your repository Settings
2. Navigate to Pages section
3. Select "GitHub Actions" as the source
4. The landing page will deploy automatically on each push

## 🐳 Docker Setup

### Start with Docker
```bash
npm run dev:docker
```

### Build and Start
```bash
npm run dev:docker:build
```

### View Logs
```bash
npm run logs
```

## 🚀 Running the Project with Docker

To spin up **all services**, run the following command from the root of the project:

```bash
docker compose up
```
(Note: first time running this command it would take a while)

**Note for DeepSeek R1**: To work with Docker, run this command while the ollama container is running:
```bash
docker exec -it ollama ollama pull deepseek-r1:7b
```

### Running Individual Services
To run individual services use the following commands:
```bash
docker compose up -d [qdrant | server | client]
```

**Example** – running only Qdrant:
```bash
docker compose up -d qdrant
```

### Docker Desktop
To visually check if the containers are running:

- Open Docker Desktop
- Navigate to Containers > 2025w2-qualai

You should see the following running services:
- qdrant
- qualai-backend
- qualai-frontend

### Accessing Services
You can access each service in your browser:
- Qdrant Dashboard: http://localhost:6333/dashboard
- Backend (FastAPI): http://localhost:8000
- Frontend (React): http://localhost:5173

## 🏗️ Project Structure

```
2025W2-QualAI/
├── 📁 client/                 # React frontend
│   ├── src/                   # Source code
│   ├── package.json           # Frontend dependencies
│   └── dockerfile            # Frontend container
├── 📁 server/                 # FastAPI backend
│   ├── app/                   # Application code
│   ├── requirements.txt       # Python dependencies
│   └── dockerfile            # Backend container
├── 📁 scripts/                # Utility scripts
│   ├── help.js               # Command help
│   ├── status-check.js       # Service monitoring
│   └── setup-env.js          # Environment setup
├── 📁 .github/                # GitHub configuration
│   ├── 📁 LandingPage/        # Landing page for GitHub Pages
│   │   ├── 📄 index.html      # Main landing page
│   │   └── 📄 .nojekyll       # GitHub Pages configuration
│   └── 📁 workflows/          # GitHub Actions workflows
├── 📄 docker-compose.yml      # Docker orchestration
├── 📄 package.json            # Project scripts
└── 📄 README.md               # This file
```

## 🧪 Testing

```bash
# Backend tests
npm test

# Frontend linting
npm run test:frontend
```

## 🔧 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Kill the process or use different ports
```

**Dependencies not found:**
```bash
npm run reset  # Complete reinstall
```

**Docker issues:**
```bash
npm run clean:docker  # Clean Docker containers
docker system prune    # Remove unused Docker resources
```

### Service Status Check
```bash
npm run status  # Check all services
```

## 👥 Team

**Team Members:**
- Remy - remydidelis@gmail.com
- Mohid - mohidkhanzada@gmail.com
- Emily - emilysalievski@gmail.com
- Zaid - zaidbtariq@gmail.com
- Aryaman - aryamanrajpal04@gmail.com
- Yao - yueyaoyan@gmail.com
- Rohith - sivasvg1rohith@gmail.com
- Amaan - amaan.muhammad@outlook.com
- Achal - achal1739@gmail.com
- Tommy - tommykiprillis@gmail.com
- Joel - gulityeaten@gmail.com
- Lisa - lisagorman00@gmail.com
- Farhan - farhan.hasan3135@gmail.com
- Gunnraj - gunnraj@hotmail.com
- Eamon - esom181002@gmail.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Docker Documentation](https://docs.docker.com/)

---

**Need help?** Run `npm run help` for a complete list of available commands!
