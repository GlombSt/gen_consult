import { useState } from 'react';
import { useCreateItem } from '../../hooks/useCreateItem';
import './ItemCreator.css';

function ItemCreator() {
  const [message, setMessage] = useState('');
  const { create, loading } = useCreateItem();

  const handleCreateItem = async () => {
    setMessage('');

    const result = await create({
      name: 'New Item',
      description: 'Created from React app'
    });
    
    if (result) {
      setMessage(`✅ Item created successfully! ID: ${result.id || 'N/A'}`);
    } else {
      setMessage(`❌ Failed to create item`);
    }
  };

  return (
    <div className="item-creator">
      <button 
        onClick={handleCreateItem} 
        disabled={loading}
        className="create-button"
      >
        {loading ? 'Creating...' : 'Create New Item'}
      </button>

      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default ItemCreator;

