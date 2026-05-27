import React, { useState } from 'react';
import axios from 'axios';
import './IngestionForm.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const IngestionForm = ({ onSuccess }) => {
  const [file, setFile] = useState(null);
  const [sourceType, setSourceType] = useState('SAP_CSV');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const sourceTypes = [
    { value: 'SAP_CSV', label: 'SAP Export (CSV)' },
    { value: 'UTILITY_CSV', label: 'Utility Portal Export (CSV)' },
    { value: 'TRAVEL_API', label: 'Travel Data (CSV)' }
  ];

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate CSV
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('source_type', sourceType);
      formData.append('company_id', 1); // Default company for MVP

      const response = await axios.post(
        `${API_BASE_URL}/ingestion/jobs/upload/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setSuccess(`Upload successful! Job ID: ${response.data.id}`);
      setFile(null);
      setSourceType('SAP_CSV');
      
      // Reload data in parent component
      if (onSuccess) {
        setTimeout(onSuccess, 2000);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message || 'Upload failed';
      setError(`Error: ${errorMsg}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ingestion-form-container">
      <div className="ingestion-form-card">
        <h2>Upload ESG Data</h2>
        <form onSubmit={handleUpload} className="ingestion-form">
          <div className="form-group">
            <label htmlFor="source-type">Data Source Type:</label>
            <select
              id="source-type"
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="form-control"
            >
              {sourceTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="file-input">Select CSV File:</label>
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="form-control"
              disabled={loading}
            />
            {file && (
              <div className="file-info">
                <span>Selected: {file.name}</span>
              </div>
            )}
          </div>

          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <button
            type="submit"
            className="submit-btn"
            disabled={!file || loading}
          >
            {loading ? 'Uploading...' : 'Upload File'}
          </button>
        </form>

        <div className="source-info">
          <h3>Expected CSV Format:</h3>
          {sourceType === 'SAP_CSV' && (
            <ul>
              <li>Columns: Plant, Menge (or Quantity/Qty), Unit, Date, Description</li>
              <li>Unit: L (liters) or gal (gallons) for fuel</li>
              <li>Format: YYYY-MM-DD for dates</li>
            </ul>
          )}
          {sourceType === 'UTILITY_CSV' && (
            <ul>
              <li>Columns: Meter ID, Start Date, End Date, Consumption, Unit</li>
              <li>Unit: kWh (kilowatt-hours)</li>
              <li>Format: YYYY-MM-DD for dates</li>
            </ul>
          )}
          {sourceType === 'TRAVEL_API' && (
            <ul>
              <li>Columns: Employee, From Airport, To Airport, Distance (km), Date</li>
              <li>Format: YYYY-MM-DD for dates</li>
              <li>Airport codes: LAX, JFK, LHR, HND, etc.</li>
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default IngestionForm;
