import React, { useState, useEffect } from 'react';
import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import '../styles/main.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface LoginAttempt {
  ip_address: string;
  timestamp: string;
  success: boolean;
  location: string;
  device_info: string;
  browser_info: string;
  latitude: number;
  longitude: number;
  accuracy_radius: number;
  city: string;
  country: string;
  timezone: string;
  isp: string;
  connection_type: string;
}

interface Analytics {
  total_attempts: number;
  successful_attempts: number;
  failed_attempts: number;
  recent_attempts: LoginAttempt[];
  hourly_attempts: {
    hour: string;
    successful: number;
    failed: number;
  }[];
}

const Analytics: React.FC = () => {  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [error, setError] = useState<string>('');
  const [selectedMarker, setSelectedMarker] = useState<LoginAttempt | null>(null);
  const [mapCenter, setMapCenter] = useState({ lat: 0, lng: 0 });
  const [mapZoom, setMapZoom] = useState(2);

  const mapContainerStyle = {
    width: '100%',
    height: '400px'
  };

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:5000/api/auth/analytics', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error('Failed to fetch analytics data');
        }

        const data = await response.json();
        setAnalytics(data);

        // Set map center to the most recent login attempt with valid coordinates
        const recentWithCoords = data.recent_attempts.find(
          attempt => attempt.latitude && attempt.longitude
        );
        if (recentWithCoords) {
          setMapCenter({ 
            lat: recentWithCoords.latitude, 
            lng: recentWithCoords.longitude 
          });
          setMapZoom(4);
        }
      } catch (error) {
        console.error('Error fetching analytics:', error);
        setError('Failed to load analytics data');
      }
    };

    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!analytics) {
    return <div className="loading">Loading...</div>;
  }

  const chartData = {
    labels: analytics.hourly_attempts.map(item => item.hour),
    datasets: [
      {
        label: 'Successful Attempts',
        data: analytics.hourly_attempts.map(item => item.successful),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
      {
        label: 'Failed Attempts',
        data: analytics.hourly_attempts.map(item => item.failed),
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Login Attempts Over Time',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="analytics-container">
      <h2>Security Analytics Dashboard</h2>
      
      <div className="stats-summary">
        <div className="stat-card">
          <h3>Total Login Attempts</h3>
          <p>{analytics.total_attempts}</p>
        </div>
        <div className="stat-card">
          <h3>Successful Logins</h3>
          <p>{analytics.successful_attempts}</p>
        </div>
        <div className="stat-card">
          <h3>Failed Attempts</h3>
          <p>{analytics.failed_attempts}</p>
        </div>
      </div>

      <div className="chart-container">
        <Line data={chartData} options={chartOptions} />
      </div>

      <div className="map-container">
        <MapContainer
          center={[0, 0]}
          zoom={2}
          style={{ height: '400px', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          {analytics.recent_attempts.map((attempt, index) => (
            attempt.latitude && attempt.longitude ? (
              <Marker
                key={index}
                position={[attempt.latitude, attempt.longitude]}
              >
                <Popup>
                  <div>
                    <strong>IP:</strong> {attempt.ip_address}<br />
                    <strong>Time:</strong> {new Date(attempt.timestamp).toLocaleString()}<br />
                    <strong>Status:</strong> {attempt.success ? 'Success' : 'Failed'}<br />
                    <strong>Device:</strong> {attempt.device_info}
                  </div>
                </Popup>
              </Marker>
            ) : null
          ))}
        </MapContainer>
      </div>

      <div className="recent-activity">
        <h3>Recent Login Attempts</h3>
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>IP Address</th>
              <th>Status</th>
              <th>Location</th>
              <th>Device</th>
            </tr>
          </thead>
          <tbody>
            {analytics.recent_attempts.map((attempt, index) => (
              <tr key={index} className={attempt.success ? 'success' : 'failure'}>
                <td>{new Date(attempt.timestamp).toLocaleString()}</td>
                <td>{attempt.ip_address}</td>
                <td>{attempt.success ? 'Success' : 'Failed'}</td>
                <td>{attempt.location}</td>
                <td>{attempt.device_info}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Analytics;
