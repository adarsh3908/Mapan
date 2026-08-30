import React, { useState } from 'react';
import Assessment from './components/Assessment';
import Dashboard from './components/Dashboard';

export default function App() {
  const [view, setView] = useState('assessment'); // 'assessment' or 'dashboard'
  const [completedAssessmentId, setCompletedAssessmentId] = useState(null);

  const handleAssessmentComplete = (id) => {
    setCompletedAssessmentId(id);
    setView('dashboard');
  };

  const handleRetake = () => {
    setCompletedAssessmentId(null);
    setView('assessment');
  };

  return (
    <div className="app-container">
      {view === 'assessment' ? (
        <Assessment onComplete={handleAssessmentComplete} />
      ) : (
        <Dashboard assessmentId={completedAssessmentId} onRetake={handleRetake} />
      )}
    </div>
  );
}
