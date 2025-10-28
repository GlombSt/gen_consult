import { get, post, put, del } from '../../../shared/api/httpClient';

/**
 * Items API Client
 * Handles all HTTP calls related to items
 * Returns plain DTOs from backend (no transformation)
 */

/**
 * Create a new item
 * @param {Object} itemData - Item data to create
 * @returns {Promise<Object>} Created item
 */
export const createItem = async (itemData) => {
  return await post('/items', itemData);
};

/**
 * Get all items
 * @returns {Promise<Array>} List of items
 */
export const getItems = async () => {
  return await get('/items');
};

/**
 * Get a single item by ID
 * @param {string|number} id - Item ID
 * @returns {Promise<Object>} Item data
 */
export const getItemById = async (id) => {
  return await get(`/items/${id}`);
};

/**
 * Update an item
 * @param {string|number} id - Item ID
 * @param {Object} itemData - Updated item data
 * @returns {Promise<Object>} Updated item
 */
export const updateItem = async (id, itemData) => {
  return await put(`/items/${id}`, itemData);
};

/**
 * Delete an item
 * @param {string|number} id - Item ID
 * @returns {Promise<void>}
 */
export const deleteItem = async (id) => {
  return await del(`/items/${id}`);
};

