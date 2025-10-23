// src/config/api.js
export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const API_ENDPOINTS = {
  TRANSCRIBE: `${API_BASE}/transcribe/`,
  DOWNLOAD: `${API_BASE}/download/`,
  GENERATE: `${API_BASE}/generate/`,
  PROJECT: `${API_BASE}/projects`,
  HIGHLIGHTS: `${API_BASE}/highlights`,
  AI_ASK: `${API_BASE}/prompt/ask_highlights`,
  PROMPT: `${API_BASE}/prompt`,
  ASK_HIGHLIGHTS: `${API_BASE}/prompt/ask_highlights`,

  listProjectTranscriptions: (projectId) => `${API_BASE}/projects/${projectId}/transcriptions`,
  getProjectTranscription: (projectId, transcriptionId) => `${API_BASE}/projects/${projectId}/transcriptions/${transcriptionId}`,
  updateProjectTranscription: (projectId, transcriptionId) => `${API_BASE}/projects/${projectId}/transcriptions/${transcriptionId}`,
  deleteProjectTranscription: (projectId, transcriptionId) => `${API_BASE}/projects/${projectId}/transcriptions/${transcriptionId}`,
  getHighlights: (transcriptionId) => `${API_BASE}/highlights/${transcriptionId}`,
  getHighlighters: (projectId) => `${API_BASE}/projects/${projectId}/highlighters/`,
};