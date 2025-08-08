# 2025W2-QualAI <br>

Team Member Names: <br>
Remy - remydidelis@gmail.com <br>
Mohid - mohidkhanzada@gmail.com <br>
Emily - emilysalievski@gmail.com <br>
Zaid - zaidbtariq@gmail.com <br>
Aryaman - aryamanrajpal04@gmail.com <br>
Yao - yueyaoyan@gmail.com <br>
Rohith - sivasvg1rohith@gmail.com <br>
Amaan - amaan.muhammad@outlook.com <br>
Achal - achal1739@gmail.com <br>
Tommy - tommykiprillis@gmail.com <br>
Joel - gulityeaten@gmail.com <br>
Lisa - lisagorman00@gmail.com <br>
Farhan - farhan.hasan3135@gmail.com <br>
Gunnraj - gunnraj@hotmail.com <br>
Eamon - esom181002@gmail.com <br>

# QualAI – Docker Setup Guide

This project uses **Docker** to containerize the full QualAI stack, including:

- **FastAPI backend**
- **Qdrant vector database**
- **React frontend**

---

## 🚀 Running the Project with Docker

To spin up **all services**, run the following command from the root of the project:

```bash
docker compose up
```
(Note: first time running this command it would take a while)
noted for deepseek r1 to work on docker, command below need to be run while running ollama container
docker exec -it ollama ollama pull deepseek-r1:7b
## 🔧 Running Individual Services
To run individual services use the following commands in server:
```cmd
docker compose up -d [qdrant | server | client]
```
Example – running only Qdrant:
```cmd
docker compose up -d qdrant
```

## 🐳 Docker Desktop
To visually check if the containers are running:

- Open Docker Desktop
- Navigate to Containers > 2025w2-qualai

You should see the following running services:
- qdrant
- qualai-backend
- qualai-frontend

## 🌐 Accessing Services
You can access each service in your browser:
- Qdrant Dashboard: http://localhost:6333/dashboard
- Backend (FastAPI): http://localhost:8000
- Frontend (React): http://localhost:5173