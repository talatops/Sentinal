import api from './api';

export const requirementService = {
  getRequirements: async () => {
    const response = await api.get('/requirements');
    return response.data;
  },
  
  getRequirement: async (id) => {
    const response = await api.get(`/requirements/${id}`);
    return response.data;
  },
  
  createRequirement: async (data) => {
    const response = await api.post('/requirements', data);
    return response.data;
  },
  
  updateRequirement: async (id, data) => {
    const response = await api.put(`/requirements/${id}`, data);
    return response.data;
  },
  
  deleteRequirement: async (id) => {
    const response = await api.delete(`/requirements/${id}`);
    return response.data;
  },
  
  getSecurityControls: async (reqId) => {
    const response = await api.get(`/requirements/${reqId}/controls`);
    return response.data;
  },
  
  addSecurityControl: async (reqId, data) => {
    const response = await api.post(`/requirements/${reqId}/controls`, data);
    return response.data;
  },
  
  exportRequirements: async (format = 'json') => {
    const response = await api.get(`/requirements/export?format=${format}`);
    return response.data;
  },
  
  getCompliance: async () => {
    const response = await api.get('/requirements/compliance');
    return response.data;
  },
};

