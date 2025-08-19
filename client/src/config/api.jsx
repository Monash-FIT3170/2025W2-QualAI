// src/config/api.js
const BASE_URL = "http://localhost:8000";

export const API_ENDPOINTS = {
  TRANSCRIBE: `${BASE_URL}/transcribe/`,
  DOWNLOAD: `${BASE_URL}/download/`,
  GENERATE: `${BASE_URL}/generate/`,
};
