import React, { useState } from 'react';
import IngestionForm from './IngestionForm';
import Dashboard from './Dashboard';
import './App.css';

function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = () => {
    // Trigger Dashboard refresh
    setRefreshKey(refreshKey + 1);
  };

  return (
    <div className="App">
      <div className="app-container">
        <IngestionForm onSuccess={handleUploadSuccess} />
        <Dashboard key={refreshKey} />
      </div>
    </div>
  );
}

export default App;
