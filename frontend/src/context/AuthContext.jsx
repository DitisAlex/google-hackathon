import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getMe } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'));
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('auth_user');
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(!!token);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    getMe(token)
      .then((userData) => {
        setUser(userData);
        localStorage.setItem('auth_user', JSON.stringify(userData));
      })
      .catch(() => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
      })
      .finally(() => setLoading(false));
  }, [token]);

  const login = useCallback((jwt, userData) => {
    setToken(jwt);
    setUser(userData);
    localStorage.setItem('auth_token', jwt);
    localStorage.setItem('auth_user', JSON.stringify(userData));
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
