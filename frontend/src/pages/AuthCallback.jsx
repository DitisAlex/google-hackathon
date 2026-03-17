import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { exchangeGitHubCode } from '../services/api';

export default function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState(null);
  const exchangedRef = useRef(false);

  useEffect(() => {
    if (exchangedRef.current) return;
    exchangedRef.current = true;

    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code) {
      setError('No authorization code received from GitHub.');
      return;
    }

    exchangeGitHubCode(code, state)
      .then(({ token, user }) => {
        console.log('========== SSO Login Success ==========');
        console.log('JWT Token:', token);
        console.log('User:', JSON.stringify(user, null, 2));
        console.log('========================================');
        login(token, user);
        sessionStorage.removeItem('oauth_state');
        navigate('/', { replace: true });
      })
      .catch((err) => {
        const msg = err.message || '';
        if (msg === 'Failed to fetch' || msg.includes('NetworkError')) {
          setError('Cannot reach the backend server. Make sure the backend is running at ' +
            (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'));
        } else {
          setError(msg || 'Failed to complete GitHub sign-in.');
        }
      });
  }, [searchParams, login, navigate]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/', { replace: true })}
            className="text-brand-600 hover:text-brand-700 underline"
          >
            Return to home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Completing GitHub sign-in...</p>
      </div>
    </div>
  );
}
