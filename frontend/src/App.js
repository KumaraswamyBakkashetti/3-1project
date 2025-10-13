import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import UserDashboardSimple from './pages/UserDashboardSimple';
import AdminDashboard from './pages/AdminDashboard';
import AdminUserDetail from './pages/AdminUserDetail';
import AdminPromptDetail from './pages/AdminPromptDetail';

function App() {
  const [user, setUser] = React.useState(null);

  React.useEffect(() => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    const role = localStorage.getItem('role');
    if (token && username && role) {
      setUser({ username, role, token });
    }
  }, []);

  const handleLogin = (userData) => {
    localStorage.setItem('token', userData.token);
    localStorage.setItem('username', userData.username);
    localStorage.setItem('role', userData.role);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    setUser(null);
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={
          user ? <Navigate to={user.role === 'admin' ? '/admin-dashboard' : '/dashboard'} /> : 
          <Login onLogin={handleLogin} />
        } />
        <Route path="/register" element={
          user ? <Navigate to={user.role === 'admin' ? '/admin-dashboard' : '/dashboard'} /> : 
          <Register onLogin={handleLogin} />
        } />
        <Route path="/dashboard" element={
          user && user.role === 'user' ? 
          <UserDashboardSimple user={user} onLogout={handleLogout} /> : 
          <Navigate to="/login" />
        } />
        <Route path="/admin-dashboard" element={
          user && user.role === 'admin' ? 
          <AdminDashboard user={user} onLogout={handleLogout} /> : 
          <Navigate to="/login" />
        } />
        <Route path="/admin/user/:userId" element={
          user && user.role === 'admin' ? 
          <AdminUserDetail /> : 
          <Navigate to="/login" />
        } />
        <Route path="/admin/user/:userId/prompt/:promptId" element={
          user && user.role === 'admin' ? 
          <AdminPromptDetail /> : 
          <Navigate to="/login" />
        } />
      </Routes>
    </Router>
  );
}

export default App;
