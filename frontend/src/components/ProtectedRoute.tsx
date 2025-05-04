import React from 'react';
import { Navigate } from 'react-router-dom';

export interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requireAdmin = false }) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('role');
  
  if (!token) {
    // Redirect to login if there's no token
    return <Navigate to="/login" />;
  }

  if (requireAdmin && userRole !== 'admin') {
    // Redirect to dashboard if user is not an admin but tries to access admin routes
    return <Navigate to="/dashboard" />;
  }

  // If there is a token and user has proper permissions, render the protected component
  return <>{children}</>;
};

export default ProtectedRoute;