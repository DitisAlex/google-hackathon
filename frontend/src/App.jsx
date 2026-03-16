import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import HomePage from './pages/HomePage';
import ResultPage from './pages/ResultPage';
import AuthCallback from './pages/AuthCallback';

function ClearTokenButton() {
  const { token, logout } = useAuth();
  if (!token) return null;
  return (
    <button
      onClick={logout}
      className="fixed bottom-4 right-4 z-50 rounded-lg bg-gray-800 text-white text-xs
        px-3 py-2 shadow-lg hover:bg-gray-700 transition opacity-70 hover:opacity-100"
    >
      Clear OAuth token
    </button>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <ClearTokenButton />
      </AuthProvider>
    </BrowserRouter>
  );
}
