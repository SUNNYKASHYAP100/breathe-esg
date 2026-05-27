import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const Dashboard = () => {
  const [records, setRecords] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('pending_review');
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    setLoading(true);

    try {
      const companyId = 1;

      // Load records
      const recordsResponse = await axios.get(
        `${API_BASE_URL}/review/records/?company_id=${companyId}&status=${filter}`
      );

      setRecords(recordsResponse.data.results || recordsResponse.data);

      // Load statistics
      const statsResponse = await axios.get(
        `${API_BASE_URL}/review/records/statistics/?company_id=${companyId}`
      );

      setStats(statsResponse.data);

      setError(null);
    } catch (err) {
      setError('Failed to load data: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleApprove = async (recordId) => {
    try {
      await axios.post(
        `${API_BASE_URL}/review/records/${recordId}/approve/`,
        { notes: 'Approved by analyst' }
      );

      loadData();
      setSelectedRecord(null);
    } catch (err) {
      setError('Failed to approve record: ' + err.message);
    }
  };

  const handleFlag = async (recordId, reason) => {
    try {
      await axios.post(
        `${API_BASE_URL}/review/records/${recordId}/flag/`,
        { reason }
      );

      loadData();
      setSelectedRecord(null);
    } catch (err) {
      setError('Failed to flag record: ' + err.message);
    }
  };

  const handleLock = async (recordId) => {
    try {
      await axios.post(
        `${API_BASE_URL}/review/records/${recordId}/lock/`
      );

      loadData();
      setSelectedRecord(null);
    } catch (err) {
      setError('Failed to lock record: ' + err.message);
    }
  };

  if (loading) {
    return <div className="dashboard-loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Breathe ESG - Analyst Review Dashboard</h1>
        <p>Review and approve emission records before audit lock</p>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="dashboard-container">
        <aside className="sidebar">
          <div className="statistics-card">
            <h2>Statistics</h2>

            {stats && (
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Total Records</span>
                  <span className="stat-value">{stats.total}</span>
                </div>

                <div className="stat-item">
                  <span className="stat-label">Pending Review</span>
                  <span className="stat-value pending">
                    {stats.pending_review}
                  </span>
                </div>

                <div className="stat-item">
                  <span className="stat-label">Flagged</span>
                  <span className="stat-value flagged">
                    {stats.flagged}
                  </span>
                </div>

                <div className="stat-item">
                  <span className="stat-label">Approved</span>
                  <span className="stat-value approved">
                    {stats.approved}
                  </span>
                </div>

                <div className="stat-item">
                  <span className="stat-label">Locked</span>
                  <span className="stat-value locked">
                    {stats.locked}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="filter-card">
            <h3>Filter by Status</h3>

            <button
              className={`filter-btn ${filter === 'pending_review' ? 'active' : ''}`}
              onClick={() => setFilter('pending_review')}
            >
              Pending Review
            </button>

            <button
              className={`filter-btn ${filter === 'flagged' ? 'active' : ''}`}
              onClick={() => setFilter('flagged')}
            >
              Flagged
            </button>

            <button
              className={`filter-btn ${filter === 'approved' ? 'active' : ''}`}
              onClick={() => setFilter('approved')}
            >
              Approved
            </button>

            <button
              className={`filter-btn ${filter === 'locked' ? 'active' : ''}`}
              onClick={() => setFilter('locked')}
            >
              Locked
            </button>
          </div>
        </aside>

        <main className="main-content">
          <div className="records-table-container">
            <h2>Activity Records</h2>

            {records.length === 0 ? (
              <p className="no-records">No records found</p>
            ) : (
              <table className="records-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Scope</th>
                    <th>Quantity</th>
                    <th>Source</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>

                <tbody>
                  {records.map((record) => (
                    <tr
                      key={record.id}
                      className={`record-row ${record.is_flagged ? 'flagged' : ''}`}
                    >
                      <td>{record.activity_date}</td>

                      <td>{record.activity_type}</td>

                      <td>
                        <span className={`scope-badge ${record.scope}`}>
                          {record.scope}
                        </span>
                      </td>

                      <td>
                        {record.quantity} {record.unit}
                      </td>

                      <td>{record.source_system}</td>

                      <td>
                        <span className={`status-badge ${record.status}`}>
                          {record.status}
                        </span>
                      </td>

                      <td>
                        <button
                          className="action-btn view-btn"
                          onClick={() => setSelectedRecord(record)}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </main>
      </div>

      {selectedRecord && (
        <div
          className="modal-overlay"
          onClick={() => setSelectedRecord(null)}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2>Record Details</h2>

              <button
                className="close-btn"
                onClick={() => setSelectedRecord(null)}
              >
                &times;
              </button>
            </div>

            <div className="modal-body">
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">Activity Type:</span>
                  <span className="detail-value">
                    {selectedRecord.activity_type}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Scope:</span>
                  <span className="detail-value">
                    {selectedRecord.scope}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Quantity:</span>
                  <span className="detail-value">
                    {selectedRecord.quantity} {selectedRecord.unit}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Date:</span>
                  <span className="detail-value">
                    {selectedRecord.activity_date}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Source:</span>
                  <span className="detail-value">
                    {selectedRecord.source_system}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Confidence:</span>
                  <span className="detail-value">
                    {(selectedRecord.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>

                {selectedRecord.flag_reason && (
                  <div className="detail-item full-width">
                    <span className="detail-label">Flag Reason:</span>

                    <span className="detail-value">
                      {selectedRecord.flag_reason}
                    </span>
                  </div>
                )}
              </div>

              <div className="modal-actions">
                <button
                  className="action-btn approve-btn"
                  onClick={() => handleApprove(selectedRecord.id)}
                >
                  Approve
                </button>

                <button
                  className="action-btn flag-btn"
                  onClick={() => {
                    const reason = prompt('Reason for flagging:');

                    if (reason) {
                      handleFlag(selectedRecord.id, reason);
                    }
                  }}
                >
                  Flag for Review
                </button>

                <button
                  className="action-btn lock-btn"
                  onClick={() => handleLock(selectedRecord.id)}
                >
                  Lock for Audit
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;