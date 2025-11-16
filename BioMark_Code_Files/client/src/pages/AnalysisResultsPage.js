import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import AnalysisReport from '../components/step9_AnalysisReport';
import '../css/AnalysisResultsPage.css';

export default function AnalysisResultsPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analyses, setAnalyses] = useState([]);
  const [error, setError] = useState('');
  const [reportData, setReportData] = useState(null);
  const reportTriggerRef = useRef(null);

  useEffect(() => {
    fetchAnalyses();
  }, []);

  useEffect(() => {
    // Trigger PDF generation when reportData is set
    if (reportData && reportTriggerRef.current) {
      const btn = reportTriggerRef.current.querySelector('.generate-report-button');
      if (btn) {
        setTimeout(() => btn.click(), 100);
        // Clear reportData after triggering
        setTimeout(() => setReportData(null), 500);
      }
    }
  }, [reportData]);

  const fetchAnalyses = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/api/user/analyses', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setAnalyses(response.data.analyses);
      }
    } catch (err) {
      console.error('Error fetching analyses:', err);
      setError('Failed to load analysis results');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      completed: 'status-completed',
      pending: 'status-pending',
      failed: 'status-failed'
    };

    return (
      <span className={`status-badge ${statusClasses[status] || ''}`}>
        {status || 'unknown'}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    // The database stores UTC time, convert to user's local timezone
    const date = new Date(dateString + 'Z'); // Add 'Z' to indicate UTC
    return date.toLocaleString();
  };

  const handleViewResults = (analysis) => {
    if (!analysis.result_path) return;
    
    // Navigate to a dedicated results page with the analysis ID
    navigate(`/analysis/${analysis.id}`);
  };

  const handleDownloadReport = async (analysis) => {
    if (!analysis.result_path) return;
    
    try {
      // Fetch full analysis data including metadata
      const token = localStorage.getItem('token');
      const response = await api.get(`/api/user/analyses/${analysis.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.data.success) return;

      const fullAnalysis = response.data.analysis;
      const metadata = fullAnalysis.metadata || {};

      // Prepare report data from the analysis with proper metadata
      const images = fullAnalysis.result_path.split(',').map((path, index) => {
        const trimmedPath = path.trim();
        return {
          id: `img-${index}`,
          path: trimmedPath,
          caption: trimmedPath.split('/').pop()
        };
      });

      const analysisResults = [{
        title: `Analysis Results`,
        images: images,
        classPair: metadata.selectedClasses ? metadata.selectedClasses.join(' vs ') : 'N/A',
        date: formatDate(fullAnalysis.created_at),
        time: metadata.executionTime || 'N/A',
        types: {
          differential: metadata.analysisMethods?.differential || [],
          clustering: metadata.analysisMethods?.clustering || [],
          classification: metadata.analysisMethods?.classification || []
        },
        parameters: metadata
      }];

      setReportData({
        analysisResults,
        analysisDate: formatDate(fullAnalysis.created_at),
        executionTime: metadata.executionTime || 'N/A',
        filename: fullAnalysis.filename || 'Unknown',
        selectedClasses: metadata.selectedClasses || [],
        selectedIllnessColumn: metadata.illnessColumn || '',
        selectedAnalyzes: [
          ...(metadata.analysisMethods?.differential || []),
          ...(metadata.analysisMethods?.clustering || []),
          ...(metadata.analysisMethods?.classification || [])
        ],
        featureCount: 20,
        nonFeatureColumns: metadata.nonFeatureColumns || []
      });
    } catch (err) {
      console.error('Error preparing report:', err);
    }
  };

  if (loading) {
    return (
      <div className="analysis-results-page">
        <div className="analysis-container">
          <p>Loading analyses...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analysis-results-page">
      <div className="analysis-container">
        <div className="analysis-header">
          <button className="back-button" onClick={() => navigate('/')}>
            &#11013; Back to Home
          </button>
          <h1>My Analysis Results</h1>
          <p className="subtitle">View and manage your analysis history</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        {analyses.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">&#129335;</div>
            <h3>No analyses yet</h3>
            <p>Upload data and run analyses to see your results here</p>
            <button className="primary-button" onClick={() => navigate('/')}>
              Start New Analysis
            </button>
          </div>
        ) : (
          <div className="analyses-list">
            {analyses.map((analysis) => (
              <div key={analysis.id} className="analysis-card">
                <div className="analysis-card-header">
                  <div className="analysis-main-info">
                    <h3>{analysis.filename || 'Unknown File'}</h3>
                    <div className="analysis-meta">
                      <span className="analysis-id">ID: {analysis.id.substring(0, 8)}...</span>
                      <span className="analysis-date">{formatDate(analysis.created_at)}</span>
                    </div>
                  </div>
                  {getStatusBadge(analysis.status)}
                </div>

                {analysis.result_path && (
                  <div className="analysis-actions">
                    <button 
                      className="view-button"
                      onClick={() => handleViewResults(analysis)}
                    >
                      &#128270; View Details
                    </button>
                    <button 
                      className="download-button"
                      onClick={() => handleDownloadReport(analysis)}
                    >
                      &#128229; Download Report
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Hidden AnalysisReport component for PDF generation */}
      {reportData && (
        <div style={{ position: 'absolute', left: '-9999px' }} ref={reportTriggerRef}>
          <AnalysisReport
            analysisResults={reportData.analysisResults}
            analysisDate={reportData.analysisDate}
            executionTime={reportData.executionTime}
            selectedClasses={reportData.selectedClasses}
            selectedIllnessColumn={reportData.selectedIllnessColumn}
            selectedAnalyzes={reportData.selectedAnalyzes}
            featureCount={reportData.featureCount}
            summaryImagePath=""
            summarizeAnalyses={[]}
            datasetFileName={reportData.filename}
          />
        </div>
      )}
    </div>
  );
}
