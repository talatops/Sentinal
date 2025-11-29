import api from "./api";

export const threatService = {
  analyzeThreat: async (threatData) => {
    const response = await api.post("/threats/analyze", threatData);
    return response.data;
  },

  getThreats: async () => {
    const response = await api.get("/threats");
    return response.data;
  },

  getThreat: async (id) => {
    const response = await api.get(`/threats/${id}`);
    return response.data;
  },

  updateThreat: async (id, data) => {
    const response = await api.put(`/threats/${id}`, data);
    return response.data;
  },

  deleteThreat: async (id) => {
    const response = await api.delete(`/threats/${id}`);
    return response.data;
  },
};
