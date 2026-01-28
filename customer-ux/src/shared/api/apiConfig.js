/**
 * API configuration
 * Central place for base URL, headers, and other API settings
 */
export const API_CONFIG = {
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
};

/**
 * Get default headers for API requests
 * Can be extended to include authentication tokens
 */
export const getDefaultHeaders = () => {
  const headers = { ...API_CONFIG.headers };
  
  // Example: Add auth token if available
  // const token = localStorage.getItem('authToken');
  // if (token) {
  //   headers['Authorization'] = `Bearer ${token}`;
  // }
  
  return headers;
};

