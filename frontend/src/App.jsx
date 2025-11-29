import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useAuthStore } from "./store/authStore";
import Dashboard from "./pages/Dashboard";
import ThreatModeling from "./pages/ThreatModeling";
import Requirements from "./pages/Requirements";
import Login from "./pages/Login";
import SonarQubeResults from "./pages/SonarQubeResults";
import ZAPResults from "./pages/ZAPResults";
import TrivyResults from "./pages/TrivyResults";
import APITokens from "./pages/APITokens";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import GitHubCallback from "./pages/GitHubCallback";
import OnboardingTour from "./components/OnboardingTour";

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={!isAuthenticated ? <Login /> : <Navigate to="/" />}
        />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/threats"
          element={
            <ProtectedRoute>
              <Layout>
                <ThreatModeling />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/requirements"
          element={
            <ProtectedRoute>
              <Layout>
                <Requirements />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/scans/sonarqube"
          element={
            <ProtectedRoute>
              <Layout>
                <SonarQubeResults />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/scans/sonarqube/:runId"
          element={
            <ProtectedRoute>
              <Layout>
                <SonarQubeResults />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/scans/zap"
          element={
            <ProtectedRoute>
              <Layout>
                <ZAPResults />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/scans/zap/:runId"
          element={
            <ProtectedRoute>
              <Layout>
                <ZAPResults />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/scans/trivy"
          element={
            <ProtectedRoute>
              <Layout>
                <TrivyResults />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/scans/trivy/:runId"
          element={
            <ProtectedRoute>
              <Layout>
                <TrivyResults />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/api-tokens"
          element={
            <ProtectedRoute>
              <Layout>
                <APITokens />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route path="/callback" element={<GitHubCallback />} />
      </Routes>
      {isAuthenticated && <OnboardingTour />}
    </Router>
  );
}

export default App;
