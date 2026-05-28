// API configuration for both development and production
// Reads from environment variables set by build process
// When REACT_APP_API_URL is not defined, default to the deployed Render backend.

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://breathe-esg-uczd.onrender.com/api';

export const API_ENDPOINTS = {
  // Ingestion
  UPLOAD: `${API_BASE_URL}/ingestion/jobs/upload/`,
  
  // Review
  RECORDS: `${API_BASE_URL}/review/records/`,
  STATISTICS: `${API_BASE_URL}/review/records/statistics/`,
  APPROVE: (id) => `${API_BASE_URL}/review/records/${id}/approve/`,
  FLAG: (id) => `${API_BASE_URL}/review/records/${id}/flag/`,
  LOCK: (id) => `${API_BASE_URL}/review/records/${id}/lock/`,
  
  // Tenants
  COMPANIES: `${API_BASE_URL}/tenants/companies/`,
};

export default API_ENDPOINTS;
