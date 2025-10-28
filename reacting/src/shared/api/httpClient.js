import { API_CONFIG, getDefaultHeaders } from './apiConfig';
import { ApiError } from './apiError';

/**
 * HTTP Client - Abstraction over fetch API
 * Handles HTTP communication, error parsing, and response transformation
 */

/**
 * Make a request to the API
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {Object} options - Fetch options
 * @returns {Promise<any>} Response data
 */
export const request = async (endpoint, options = {}) => {
  const url = `${API_CONFIG.baseURL}${endpoint}`;
  
  const config = {
    ...options,
    headers: {
      ...getDefaultHeaders(),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    // Parse response body
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // Handle error responses
    if (!response.ok) {
      throw ApiError.fromResponse(response, data);
    }

    return data;
  } catch (error) {
    // Re-throw ApiError as is
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Wrap network errors
    throw new ApiError(
      error.message || 'Network request failed',
      0,
      null
    );
  }
};

/**
 * GET request
 */
export const get = (endpoint, options = {}) => {
  return request(endpoint, {
    ...options,
    method: 'GET',
  });
};

/**
 * POST request
 */
export const post = (endpoint, body, options = {}) => {
  return request(endpoint, {
    ...options,
    method: 'POST',
    body: JSON.stringify(body),
  });
};

/**
 * PUT request
 */
export const put = (endpoint, body, options = {}) => {
  return request(endpoint, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(body),
  });
};

/**
 * DELETE request
 */
export const del = (endpoint, options = {}) => {
  return request(endpoint, {
    ...options,
    method: 'DELETE',
  });
};

export default {
  get,
  post,
  put,
  del,
  request,
};

