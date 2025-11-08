import api from './api';

export const cicdService = {
  getRuns: async (limit = 50) => {
    const response = await api.get(`/cicd/runs?limit=${limit}`);
    return response.data;
  },
  
  getRun: async (id) => {
    const response = await api.get(`/cicd/runs/${id}`);
    return response.data;
  },
  
  triggerRun: async (data) => {
    const response = await api.post('/cicd/trigger', data);
    return response.data;
  },
  
  getDashboard: async () => {
    const response = await api.get('/cicd/dashboard');
    return response.data;
  },
  
  // Detailed scan results
  getRunSAST: async (runId, filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => params.append(key, v));
      } else if (value) {
        params.append(key, value);
      }
    });
    const response = await api.get(`/cicd/runs/${runId}/sast?${params.toString()}`);
    return response.data;
  },
  
  getRunDAST: async (runId, filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => params.append(key, v));
      } else if (value) {
        params.append(key, value);
      }
    });
    const response = await api.get(`/cicd/runs/${runId}/dast?${params.toString()}`);
    return response.data;
  },
  
  getRunTrivy: async (runId, filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => params.append(key, v));
      } else if (value) {
        params.append(key, value);
      }
    });
    const response = await api.get(`/cicd/runs/${runId}/trivy?${params.toString()}`);
    return response.data;
  },
  
  // Latest scans
  getLatestSonarQube: async () => {
    const response = await api.get('/cicd/scans/sonarqube/latest');
    return response.data;
  },
  
  getLatestZAP: async () => {
    const response = await api.get('/cicd/scans/zap/latest');
    return response.data;
  },
  
  getLatestTrivy: async () => {
    const response = await api.get('/cicd/scans/trivy/latest');
    return response.data;
  },
  
  // Trigger scans
  triggerSonarQube: async (data) => {
    const response = await api.post('/cicd/scans/sonarqube/trigger', data);
    return response.data;
  },
  
  triggerZAP: async (data) => {
    const response = await api.post('/cicd/scans/zap/trigger', data);
    return response.data;
  },
  
  triggerTrivy: async (data) => {
    const response = await api.post('/cicd/scans/trivy/trigger', data);
    return response.data;
  },
  
  // Scan status
  getScanStatus: async (scanType, scanId) => {
    const response = await api.get(`/cicd/scans/${scanType}/status/${scanId}`);
    return response.data;
  },
};

