/**
 * Custom error class for API errors
 * Provides structured error information from backend responses
 */
export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }

  static fromResponse(response, data) {
    const message = data?.message || data?.error || `${response.status} - ${response.statusText}`;
    return new ApiError(message, response.status, data);
  }
}

