import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';

const GitHubCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('Processing...');
  const code = searchParams.get('code');

  useEffect(() => {
    console.log('GitHubCallback component mounted');
    console.log('Code from URL:', code);
    
    const handleCallback = async () => {
      console.log('handleCallback started');
      
      if (!code) {
        console.error('No authorization code received');
        setError('No authorization code received');
        setStatus('No code found');
        setTimeout(() => navigate('/login?error=no_code'), 2000);
        return;
      }

      try {
        setStatus('Exchanging code for token...');
        console.log('Processing OAuth callback with code:', code.substring(0, 10) + '...');
        console.log('Making API call to:', `/api/auth/github/callback?code=${code}`);
        
        // Call backend to exchange code for tokens
        const response = await api.get(`/auth/github/callback?code=${code}`);
        console.log('API response received:', response);
        const data = response.data;
        console.log('Response data:', data);

        if (data.access_token) {
          setStatus('Authentication successful! Redirecting...');
          console.log('Access token received, storing...');
          
          // Store tokens and user data
          setTokens(data.access_token, data.refresh_token);
          setUser(data.user);
          
          console.log('Tokens stored, redirecting to dashboard');
          // Redirect to dashboard
          setTimeout(() => navigate('/'), 500);
        } else {
          console.error('OAuth callback failed - no access token:', data);
          setError(data.error || 'Authentication failed');
          setStatus('Authentication failed');
          setTimeout(() => navigate('/login?error=oauth_failed'), 3000);
        }
      } catch (error) {
        console.error('Error processing OAuth callback:', error);
        console.error('Error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        });
        const errorMessage = error.response?.data?.error || error.response?.data?.message || error.message || 'Authentication error';
        setError(errorMessage);
        setStatus('Error occurred');
        setTimeout(() => navigate('/login?error=oauth_error'), 3000);
      }
    };

    handleCallback();
  }, [code, navigate, setTokens, setUser]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-cyber-darker via-cyber-dark to-cyber-darker">
      <div className="card text-center max-w-md">
        {error ? (
          <>
            <div className="text-red-500 text-4xl mb-4">⚠️</div>
            <h2 className="text-xl font-bold text-red-500 mb-2">Authentication Failed</h2>
            <p className="text-gray-400 mb-2">{error}</p>
            <p className="text-sm text-gray-500 mb-2">Status: {status}</p>
            <p className="text-xs text-gray-600">Check browser console (F12) for details</p>
            <p className="text-sm text-gray-500 mt-4">Redirecting to login...</p>
          </>
        ) : (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-blue mx-auto mb-4"></div>
            <h2 className="text-xl font-bold text-cyber-blue mb-2">Processing GitHub OAuth...</h2>
            <p className="text-gray-400 mb-2">{status}</p>
            <p className="text-xs text-gray-600">Check browser console (F12) for progress</p>
          </>
        )}
      </div>
    </div>
  );
};

export default GitHubCallback;

