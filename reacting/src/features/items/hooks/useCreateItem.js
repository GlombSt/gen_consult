import { useState } from 'react';
import { createItem } from '../api/itemsApi';

/**
 * Hook for creating items
 * Orchestrates API call and manages UI state (loading, errors)
 * 
 * @returns {Object} Hook state and methods
 */
export const useCreateItem = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  /**
   * Create a new item
   * @param {Object} itemData - Item data to create
   * @returns {Promise<Object>} Created item or null on error
   */
  const create = async (itemData) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const result = await createItem(itemData);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to create item');
      return null;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset the hook state
   */
  const reset = () => {
    setLoading(false);
    setError(null);
    setData(null);
  };

  return {
    create,
    loading,
    error,
    data,
    reset,
  };
};

