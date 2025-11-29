import { useState, useEffect } from 'react';
// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion';
import { apiTokenService } from '../services/apiTokenService';
import { useAuthStore } from '../store/authStore';
import {
  KeyIcon,
  PlusIcon,
  TrashIcon,
  ClipboardDocumentIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

const APITokens = () => {
  const { user } = useAuthStore();
  const [tokens, setTokens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newToken, setNewToken] = useState(null);
  const [copiedToken, setCopiedToken] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    expires_in_days: '',
    scopes: ['webhook:write'],
  });

  useEffect(() => {
    if (user?.role === 'Admin') {
      loadTokens();
    } else {
      setError('Admin access required');
      setLoading(false);
    }
  }, [user]);

  const loadTokens = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiTokenService.listTokens();
      setTokens(data.tokens || []);
    } catch (err) {
      console.error('Failed to load API tokens:', err);
      setError(err.response?.data?.error || 'Failed to load API tokens');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateToken = async (e) => {
    e.preventDefault();
    try {
      setError(null);
      const payload = {
        name: formData.name,
        expires_in_days: formData.expires_in_days ? parseInt(formData.expires_in_days) : null,
        scopes: formData.scopes,
      };
      
      const data = await apiTokenService.createToken(payload);
      setNewToken(data.token);
      setFormData({ name: '', expires_in_days: '', scopes: ['webhook:write'] });
      setShowCreateForm(false);
      await loadTokens();
    } catch (err) {
      console.error('Failed to create API token:', err);
      setError(err.response?.data?.error || 'Failed to create API token');
    }
  };

  const handleRevokeToken = async (tokenId) => {
    if (!window.confirm('Are you sure you want to revoke this token? This action cannot be undone.')) {
      return;
    }
    
    try {
      setError(null);
      await apiTokenService.revokeToken(tokenId);
      await loadTokens();
    } catch (err) {
      console.error('Failed to revoke API token:', err);
      setError(err.response?.data?.error || 'Failed to revoke API token');
    }
  };

  const copyToClipboard = (text, tokenId) => {
    navigator.clipboard.writeText(text);
    setCopiedToken(tokenId);
    setTimeout(() => setCopiedToken(null), 2000);
  };

  if (user?.role !== 'Admin') {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <XCircleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Access Denied</h2>
          <p className="text-gray-400">Admin role required to manage API tokens</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-blue"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">API Tokens</h1>
          <p className="text-gray-400">Manage API tokens for webhook authentication</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn-primary flex items-center gap-2"
        >
          <PlusIcon className="w-5 h-5" />
          Create Token
        </button>
      </motion.div>

      {error && (
        <div className="card bg-red-500/10 border-red-500/50">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* New Token Display */}
      {newToken && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card bg-green-500/10 border-green-500/50"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="w-6 h-6 text-green-400" />
              <h3 className="text-lg font-bold text-white">Token Created Successfully</h3>
            </div>
            <button
              onClick={() => setNewToken(null)}
              className="text-gray-400 hover:text-white"
            >
              <XCircleIcon className="w-5 h-5" />
            </button>
          </div>
          <p className="text-gray-300 mb-4">
            <strong className="text-yellow-400">Important:</strong> Copy this token now. You won't be able to see it again!
          </p>
          <div className="flex items-center gap-2 mb-4">
            <code className="flex-1 p-3 bg-cyber-dark rounded border border-cyber-blue/30 text-sm text-gray-300 break-all">
              {newToken}
            </code>
            <button
              onClick={() => copyToClipboard(newToken, 'new')}
              className="p-3 bg-cyber-blue hover:bg-cyber-blue/80 rounded transition-colors"
              title="Copy token"
            >
              {copiedToken === 'new' ? (
                <CheckCircleIcon className="w-5 h-5 text-green-400" />
              ) : (
                <ClipboardDocumentIcon className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </motion.div>
      )}

      {/* Create Token Form */}
      {showCreateForm && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Create New API Token</h2>
          <form onSubmit={handleCreateToken} className="space-y-4">
            <div>
              <label className="block text-gray-400 text-sm font-medium mb-2">
                Token Name *
              </label>
              <input
                type="text"
                className="input-field w-full"
                placeholder="e.g., GitHub Actions Webhook"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            
            <div>
              <label className="block text-gray-400 text-sm font-medium mb-2">
                Expires In (Days)
              </label>
              <input
                type="number"
                className="input-field w-full"
                placeholder="Leave empty for no expiration"
                value={formData.expires_in_days}
                onChange={(e) => setFormData({ ...formData, expires_in_days: e.target.value })}
                min="1"
              />
              <p className="text-xs text-gray-500 mt-1">Leave empty for tokens that never expire</p>
            </div>

            <div>
              <label className="block text-gray-400 text-sm font-medium mb-2">
                Scopes
              </label>
              <div className="space-y-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.scopes.includes('webhook:write')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData({
                          ...formData,
                          scopes: [...formData.scopes, 'webhook:write'].filter((v, i, a) => a.indexOf(v) === i),
                        });
                      } else {
                        setFormData({
                          ...formData,
                          scopes: formData.scopes.filter((s) => s !== 'webhook:write'),
                        });
                      }
                    }}
                    className="rounded"
                  />
                  <span className="text-gray-300">webhook:write - Send webhook data</span>
                </label>
              </div>
            </div>

            <div className="flex gap-3">
              <button type="submit" className="btn-primary">
                Create Token
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setFormData({ name: '', expires_in_days: '', scopes: ['webhook:write'] });
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </motion.div>
      )}

      {/* Tokens List */}
      <div className="card">
        <h2 className="text-xl font-bold text-white mb-4">Existing Tokens</h2>
        {tokens.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No API tokens created yet</p>
        ) : (
          <div className="space-y-3">
            {tokens.map((token) => (
              <div
                key={token.id}
                className="p-4 bg-cyber-dark rounded-lg border border-cyber-blue/20 flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <KeyIcon className="w-5 h-5 text-cyber-blue" />
                    <h3 className="text-white font-medium">{token.name}</h3>
                    {token.is_active ? (
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">
                        Active
                      </span>
                    ) : (
                      <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">
                        Revoked
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-400 space-y-1">
                    <p>Created: {new Date(token.created_at).toLocaleString()}</p>
                    {token.expires_at && (
                      <p>
                        Expires: {new Date(token.expires_at).toLocaleString()}
                        {new Date(token.expires_at) < new Date() && (
                          <span className="text-red-400 ml-2">(Expired)</span>
                        )}
                      </p>
                    )}
                    {token.last_used_at && (
                      <p>Last used: {new Date(token.last_used_at).toLocaleString()}</p>
                    )}
                    {token.scopes && token.scopes.length > 0 && (
                      <p>Scopes: {Array.isArray(token.scopes) ? token.scopes.join(', ') : token.scopes}</p>
                    )}
                  </div>
                </div>
                {token.is_active && (
                  <button
                    onClick={() => handleRevokeToken(token.id)}
                    className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors"
                    title="Revoke token"
                  >
                    <TrashIcon className="w-5 h-5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default APITokens;

