# 2025W2-QualAI <br>
## Project Overview

An AI-driven Virtual Research Assistant. Use our conversartional AI chatbot to assist you in analysing your qualitative data derived from audio, text, and video files. This tool contains the following features:
- Transcribe your uploaded file into text files you can view, edit and download.
- Customise highlighter to adjust the importance and weight of certain parts of your transcription
- Conversartional chat bot
   - Online/offline mode for AI chatbot to accomandate your budget needs
   - Engage with the data and offer alternative interpretations
   - Summaries, explain and rewrite the transcript or chat

For details on our user guide please visit [here](https://docs.google.com/document/d/1jQlEi8dnG2bbzocHSbcGuCL-hawkmtVE5QyP_P1fepw/edit?usp=sharing)

## All Team Member
_*If you have any issues, your main point of contact would be: Yao, Amaan or Farhan._

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

## ✨ Completed Epics and tasks
- **UI**
  - Homepage
  - Dialogues
  - Setting page
- **Conversational AI chatbot**
    - Online/offline mode
    - Conversation template: "Summarise", "Find Themes", "Find Outliners", "Find Quotes"
    - Bubble action for chat response: "Summarise", "Explain", "Rewrite"
    - Weight response using highlighter weight (E.g. If a section is highlighted with weight-ignore it wil be ignored by the chatbot)
- **Transcribe**
    - Upload and transcribe audio and video files
    - Upload text files
    - Display loading status while media is being processed
- **Text editor**
    - Display selected transcript
    - Highlighting contents
    - Edit, save and delete transcript
    - Download transcript
- **Setting page**
    - Custom highlighters
    - Update project details
- **Landing page**

## 🔗 Project Management

This project is managed using a [Notion](https://www.notion.so/Product-Backlog-Qual-AI-1c2a077291a4801ab085ffc3b73abb7e) product backlog which includes:
- **User stories**
- **Tasks**
- **Assigned agile teams**
- **Subtasks with individual assignees**
    
➡️ You can view it here: [QualAI Product Backlog](https://www.notion.so/Product-Backlog-Qual-AI-1c2a077291a4801ab085ffc3b73abb7e)

---
# QualAI – Docker Setup Guide

This project uses **Docker** to containerize the full QualAI stack, including:

- **FastAPI backend**
- **Qdrant vector database**
- **React frontend**

---
## Required Software and hardware

Docker Desktop (https://docs.docker.com/desktop/)

In terms of hardware requirements, we recommend a device with at least 16GB of RAM to ensure smooth project performance and at least 5GB of available hard drive space for installation of required libraries.

## ✨ Setting up the Project

Firstly clone the project Git repository locally with the following command:
 `git clone https://github.com/Monash-FIT3170/2025W2-QualAI`

It will have a .env file which contains the following variables:
```
QDRANT_HOST=ENTER_YOUR_QDRANT_HOST_URL
DATABASE_URL=ENTER_YOUR_DATABASE_URL
GEMINI_API_KEY=ENTER_YOUR_API_KEY
```
NOTE: The project will not run properly if the .env file doesn’t contain a valid Gemini API Key. A valid key can be obtained [here](https://aistudio.google.com/welcome?utm_source=google&utm_medium=cpc&utm_campaign=FY25-global-DR-gsem-BKWS-1710442&utm_content=text-ad-none-any-DEV_c-CRE_731129942539-ADGP_Hybrid%20%7C%20BKWS%20-%20EXA%20%7C%20Txt-Gemini-Gemini%20API%20Docs-KWID_43700081668090798-kwd-2088805677811&utm_term=KW_gemini%20api%20documentation-ST_gemini%20api%20documentation&gclsrc=aw.ds&gad_source=1&gad_campaignid=22184668741&gbraid=0AAAAACn9t64GgMjJfg3pYLY4LWrE2kzJu&gclid=CjwKCAjwlOrFBhBaEiwAw4bYDe25lOw-Limmf7HGDgV5QAD6OtU9aiMg3VI_kLUCKwA2Q8MIYlKqLRoC8FgQAvD_BwE)

After obtaining a valid Gemini API Key replace the ENTER_YOUR_API_KEY in the `.env` file with the actual key.


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


## FAQ (common problems)
<details>
<summary>Changes I just made have not been updated when I run docker compose</summary>
   This is usually because docker build hasn’t been run and the new changes are not pushed to docker
</details>
<details>
<summary>Docker is taking a long time to load</summary>
If in terminal, if it doesn't say application start up complete, then backend is still loading
The colour of the terminal command will be green if Docker has successfully updated
</details>
<details>
<summary>If the terminal is stuck on `pulling manifest`</summary>
   This is expected as Ollam takes a while to install. Please wait for the installation to complete.
</details>
<details>
<summary>Offline chatbot is not responding to queries</summary>
	This is expected, the offline model is much slower so please allow it more time to generate a response
</details>
<details>
<summary>What shall I do if I want to contribute?</summary>
   You should follow the following steps to contribute to this project:
	1. Make an issue on this repository. 
   2. Create a feature branch referencing the issue.
   3. Create a pull request and fill in all the sections addressed on the template.
   4. Request at least 2 team member to review your pull request.
   5. If all two pull request is approved and you have no merge conflict you are free to merge your branch onto develop! :D ✨ 
</details>

