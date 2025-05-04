import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/main.css';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  created_at: string;
  last_login: string;
}

const UserDashboard: React.FC = () => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string>('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/user/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user profile');
      }

      const data = await response.json();
      setUserProfile(data);
    } catch (err) {
      setError('Failed to load user profile');
      console.error(err);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/user/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: passwordForm.currentPassword,
          new_password: passwordForm.newPassword
        })
      });

      if (!response.ok) {
        throw new Error('Failed to change password');
      }

      setIsChangingPassword(false);
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      alert('Password changed successfully');
    } catch (err) {
      setError('Failed to change password');
      console.error(err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  if (!userProfile) {
    return <div>Loading...</div>;
  }

  return (
    <div className="user-dashboard">
      <header className="dashboard-header">
        <h1>Welcome, {userProfile.username}</h1>
        <button onClick={handleLogout} className="logout-button">Logout</button>
      </header>

      <div className="profile-section">
        <h2>Profile Information</h2>
        <div className="profile-details">
          <p><strong>Email:</strong> {userProfile.email}</p>
          <p><strong>Account Created:</strong> {new Date(userProfile.created_at).toLocaleDateString()}</p>
          <p><strong>Last Login:</strong> {new Date(userProfile.last_login).toLocaleString()}</p>
        </div>

        <div className="password-section">
          {!isChangingPassword ? (
            <button onClick={() => setIsChangingPassword(true)}>Change Password</button>
          ) : (
            <form onSubmit={handlePasswordChange}>
              <h3>Change Password</h3>
              {error && <div className="error-message">{error}</div>}
              <div>
                <label htmlFor="currentPassword">Current Password:</label>
                <input
                  type="password"
                  id="currentPassword"
                  value={passwordForm.currentPassword}
                  onChange={(e) => setPasswordForm({...passwordForm, currentPassword: e.target.value})}
                  required
                />
              </div>
              <div>
                <label htmlFor="newPassword">New Password:</label>
                <input
                  type="password"
                  id="newPassword"
                  value={passwordForm.newPassword}
                  onChange={(e) => setPasswordForm({...passwordForm, newPassword: e.target.value})}
                  required
                  minLength={8}
                />
              </div>
              <div>
                <label htmlFor="confirmPassword">Confirm New Password:</label>
                <input
                  type="password"
                  id="confirmPassword"
                  value={passwordForm.confirmPassword}
                  onChange={(e) => setPasswordForm({...passwordForm, confirmPassword: e.target.value})}
                  required
                  minLength={8}
                />
              </div>
              <div className="button-group">
                <button type="submit">Update Password</button>
                <button type="button" onClick={() => setIsChangingPassword(false)}>Cancel</button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;
