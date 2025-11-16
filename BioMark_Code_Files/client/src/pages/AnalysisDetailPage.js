import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import AnalysisReport from '../components/step9_AnalysisReport';
import '../css/AnalysisDetailPage.css';

export default function AnalysisDetailPage() {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [analysisResults, setAnalysisResults] = useState([]);

  const fetchAnalysisDetail = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await api.get(`/api/user/analyses/${analysisId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        const analysisData = response.data.analysis;
        setAnalysis(analysisData);
        
        const metadata = analysisData.metadata || {};
        
        // Format the data for the AnalysisReport component
        if (analysisData.result_path) {
          const images = analysisData.result_path.split(',').map((path, index) => {
            const trimmedPath = path.trim();
            return {
              id: `img-${index}`,
              path: trimmedPath,  // Full path like "results/xxx/shap/png/image.png"
              caption: trimmedPath.split('/').pop()  // Just the filename
            };
          });

          setAnalysisResults([{
            title: `Analysis Results`,
            images: images,
            classPair: metadata.selectedClasses ? metadata.selectedClasses.join(' vs ') : 'N/A',
            date: new Date(analysisData.created_at + 'Z').toLocaleString(),
            time: metadata.executionTime || 'N/A',
            types: {
              differential: metadata.analysisMethods?.differential || [],
              clustering: metadata.analysisMethods?.clustering || [],
              classification: metadata.analysisMethods?.classification || []
            },
            parameters: metadata
          }]);
        }
      }
    } catch (err) {
      console.error('Error fetching analysis details:', err);
      setError('Failed to load analysis details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysisDetail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [analysisId]);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString + 'Z');
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="analysis-detail-page">
        <div className="detail-container">
          <p>Loading analysis details...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="analysis-detail-page">
        <div className="detail-container">
          <div className="error-message">{error || 'Analysis not found'}</div>
          <button className="back-button" onClick={() => navigate('/my-analyses')}>
            &#11013; Back to Analyses
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="analysis-detail-page">
      <div className="detail-container">
        <button className="back-button" onClick={() => navigate('/my-analyses')}>
          &#11013; Back to My Analyses
        </button>

        <div className="detail-header">
          <h1>Analysis Details</h1>
        </div>

        {/* Analysis Information Card */}
        <div className="analysis-information-card">
          <h2>Analysis Information</h2>
          
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">File:</span>
              <span className="info-value">
                {analysis.filename || (analysis.isMerged ? analysis.sourceFiles?.join(', ') : 'Unknown')}
              </span>
            </div>
            
            {analysis.metadata && (
              <>
                <div className="info-item">
                  <span className="info-label">Illness Column:</span>
                  <span className="info-value">{analysis.metadata.illnessColumn || 'N/A'}</span>
                </div>
                
                <div className="info-item">
                  <span className="info-label">Sample Column:</span>
                  <span className="info-value">{analysis.metadata.sampleColumn || 'N/A'}</span>
                </div>
                
                {analysis.metadata.selectedClasses && analysis.metadata.selectedClasses.length > 0 && (
                  <div className="info-item">
                    <span className="info-label">Selected Classes:</span>
                    <span className="info-value">{analysis.metadata.selectedClasses.join(', ')}</span>
                  </div>
                )}
                
                {analysis.metadata.analysisMethods && (
                  <>
                    {analysis.metadata.analysisMethods.differential?.length > 0 && (
                      <div className="info-item">
                        <span className="info-label">Differential Analysis:</span>
                        <span className="info-value">{analysis.metadata.analysisMethods.differential.join(', ')}</span>
                      </div>
                    )}
                    
                    {analysis.metadata.analysisMethods.clustering?.length > 0 && (
                      <div className="info-item">
                        <span className="info-label">Clustering:</span>
                        <span className="info-value">{analysis.metadata.analysisMethods.clustering.join(', ')}</span>
                      </div>
                    )}
                    
                    {analysis.metadata.analysisMethods.classification?.length > 0 && (
                      <div className="info-item">
                        <span className="info-label">Classification:</span>
                        <span className="info-value">{analysis.metadata.analysisMethods.classification.join(', ')}</span>
                      </div>
                    )}
                  </>
                )}
                
                {analysis.metadata.nonFeatureColumns && analysis.metadata.nonFeatureColumns.length > 0 && (
                  <div className="info-item">
                    <span className="info-label">Non-Feature Columns:</span>
                    <span className="info-value">{analysis.metadata.nonFeatureColumns.join(', ')}</span>
                  </div>
                )}
              </>
            )}
            
            <div className="info-item">
              <span className="info-label">Status:</span>
              <span className={`status-badge status-${analysis.status}`}>
                {analysis.status}
              </span>
            </div>
            
            <div className="info-item">
              <span className="info-label">Created:</span>
              <span className="info-value">{formatDate(analysis.created_at)}</span>
            </div>

            {analysis.isMerged && (
              <div className="info-item">
                <span className="info-label">Type:</span>
                <span className="info-value">Merged Analysis</span>
              </div>
            )}
          </div>
        </div>

        {/* Analysis Results Images */}
        <div className="results-section">
          <h2>Analysis Results</h2>
          
          {analysis.result_path ? (
            <div className="results-grid">
              {analysis.result_path.split(',').map((path, index) => {
                const trimmedPath = path.trim();
                const isImage = trimmedPath.match(/\.(png|jpg|jpeg|gif|svg)$/i);
                
                return (
                  <div key={index} className="result-card">
                    {isImage ? (
                      <>
                        <div className="result-image-wrapper">
                          <img 
                            src={`http://localhost:5003/${trimmedPath}`} 
                            alt={`Result ${index + 1}`}
                            className="result-image"
                          />
                        </div>
                        <div className="result-caption">
                          {trimmedPath.split('/').pop()}
                        </div>
                        <a 
                          href={`http://localhost:5003/${trimmedPath}`} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="view-full-link"
                        >
                          View Full Size &#8594;
                        </a>
                      </>
                    ) : (
                      <div className="result-file-link">
                        <a 
                          href={`http://localhost:5003/${trimmedPath}`} 
                          target="_blank" 
                          rel="noopener noreferrer"
                        >
                          📄 {trimmedPath.split('/').pop()}
                        </a>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <p>No results available</p>
          )}
        </div>

        {/* Report Generation Section */}
        {analysisResults.length > 0 && (
          <div className="report-section">
            <AnalysisReport
              analysisResults={analysisResults}
              analysisDate={formatDate(analysis.created_at)}
              executionTime={analysis.metadata?.executionTime || 'N/A'}
              selectedClasses={analysis.metadata?.selectedClasses || []}
              selectedIllnessColumn={analysis.metadata?.illnessColumn || ''}
              selectedAnalyzes={[
                ...(analysis.metadata?.analysisMethods?.differential || []),
                ...(analysis.metadata?.analysisMethods?.clustering || []),
                ...(analysis.metadata?.analysisMethods?.classification || [])
              ]}
              featureCount={20}
              summaryImagePath=""
              summarizeAnalyses={[]}
              datasetFileName={analysis.filename || 'Unknown'}
            />
          </div>
        )}
      </div>
    </div>
  );
}
