import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { AgentShowcase } from './pages/AgentShowcase';
import { ControlsPage } from './pages/ControlsPage';
import { ControlDetail } from './pages/ControlDetail';
import { ToolsPage } from './pages/ToolsPage';
import { GapsPage } from './pages/GapsPage';
import { ReportPage } from './pages/ReportPage';
import { LandingPage } from './pages/LandingPage';

function App() {
  const defaultTenant = 'default';
  
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/tenant/:id/dashboard" element={<Dashboard />} />
        <Route path="/tenant/:id/agents" element={<AgentShowcase />} />
        <Route path="/tenant/:id/controls" element={<ControlsPage />} />
        <Route path="/tenant/:id/control/:controlId" element={<ControlDetail />} />
        <Route path="/tenant/:id/tools" element={<ToolsPage />} />
        <Route path="/tenant/:id/gaps" element={<GapsPage />} />
        <Route path="/tenant/:id/report" element={<ReportPage />} />
        <Route path="/tenant/:id/domain/:domain" element={<ControlsPage />} />
        <Route path="*" element={<Navigate to={`/tenant/${defaultTenant}/dashboard`} replace />} />
      </Routes>
    </Router>
  );
}

export default App;

