import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import ResultsViewer from './components/ResultsViewer';

export default function AppRoutes() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/results/:analysisId" element={<ResultsViewer />} />
      </Routes>
    </HashRouter>
  );
}
