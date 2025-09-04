// src/config/api.js
export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const API_ENDPOINTS = {
  TRANSCRIBE: `${API_BASE}/transcribe/`,
  DOWNLOAD: `${API_BASE}/download/`,
  GENERATE: `${API_BASE}/generate/`,
  PROJECT: `${API_BASE}/projects`,

  listProjectTranscriptions: (projectId) => `${API_BASE}/projects/${projectId}/transcriptions`,
  getProjectTranscription: (projectId, transcriptionId) => `${API_BASE}/projects/${projectId}/transcriptions/${transcriptionId}`
};