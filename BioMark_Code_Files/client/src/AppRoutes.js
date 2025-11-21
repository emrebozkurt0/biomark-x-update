import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import App from './App';
import ResultsViewer from './components/ResultsViewer';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import AnalysisResultsPage from './pages/AnalysisResultsPage';
import AnalysisDetailPage from './pages/AnalysisDetailPage';

// Protected Route Component
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" replace />;
}

export default function AppRoutes() {
  return (
    <Router basename="/biomark">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <App />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/my-analyses" 
          element={
            <ProtectedRoute>
              <AnalysisResultsPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/analysis/:analysisId" 
          element={
            <ProtectedRoute>
              <AnalysisDetailPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/results/:analysisId" 
          element={
            <ProtectedRoute>
              <ResultsViewer />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Router>
  );
}

