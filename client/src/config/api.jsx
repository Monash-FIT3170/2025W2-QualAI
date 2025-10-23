// src/config/api.js
export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const API_ENDPOINTS = {
  TRANSCRIBE: `${API_BASE}/transcribe/`,
  DOWNLOAD: `${API_BASE}/download/`,
  GENERATE: `${API_BASE}/generate/`,
  GENERATE_CODE: `${API_BASE}/generate_code/`,
  PROJECT: `${API_BASE}/projects`,
  HIGHLIGHTS: `${API_BASE}/highlights`,
  CODES: `${API_BASE}/codes`,

  listProjectTranscriptions: (projectId) => `${API_BASE}/projects/${projectId}/transcriptions`,
  getProjectTranscription: (projectId, transcriptionId) => `${API_BASE}/projects/${projectId}/transcriptions/${transcriptionId}`,
  updateProjectTranscription: (projectId, transcriptionId) => `${API_BASE}/projects/${projectId}/transcriptions/${transcriptionId}`,
  deleteProjectTranscription: (projectId, transcriptionId) => `${API_BASE}/projects/${projectId}/transcriptions/${transcriptionId}`,
  getHighlights: (transcriptionId) => `${API_BASE}/highlights/${transcriptionId}`,
  getHighlighters: (projectId) => `${API_BASE}/projects/${projectId}/highlighters/`,
  listProjectCodes: (projectId) => `${API_BASE}/projects/${projectId}/codes`,
  deleteCode: (codeId) => `${API_BASE}/codes/${codeId}`, 
};