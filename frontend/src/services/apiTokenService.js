import api from "./api";

export const apiTokenService = {
  createToken: async (data) => {
    const response = await api.post("/auth/api-tokens", data);
    return response.data;
  },

  listTokens: async () => {
    const response = await api.get("/auth/api-tokens");
    return response.data;
  },

  revokeToken: async (tokenId) => {
    const response = await api.post(`/auth/api-tokens/${tokenId}/revoke`);
    return response.data;
  },
};
