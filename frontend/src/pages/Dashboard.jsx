import { useState, useEffect, useCallback } from 'react';
// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { cicdService } from '../services/cicdService';
import wsService from '../services/websocket';
import {
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ShieldExclamationIcon,
  CodeBracketIcon,
  BugAntIcon,
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanSummaries, setScanSummaries] = useState({
    sonarqube: null,
    zap: null,
    trivy: null,
  });

  const loadDashboard = useCallback(async () => {
    try {
      const data = await cicdService.getDashboard();
      setDashboardData(data);
      
      // Load latest scan summaries
      try {
        const [sonarqube, zap, trivy] = await Promise.allSettled([
          cicdService.getLatestSonarQube(),
          cicdService.getLatestZAP(),
          cicdService.getLatestTrivy(),
        ]);
        
        setScanSummaries({
          sonarqube: sonarqube.status === 'fulfilled' && sonarqube.value.sast_results ? sonarqube.value.sast_results : null,
          zap: zap.status === 'fulfilled' && zap.value.dast_results ? zap.value.dast_results : null,
          trivy: trivy.status === 'fulfilled' && trivy.value.trivy_results ? trivy.value.trivy_results : null,
        });
      } catch (error) {
        console.error('Failed to load scan summaries:', error);
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDashboardUpdate = useCallback((update) => {
    console.log('Dashboard update received:', update);
    
    if (update.type === 'new_run' || update.type === 'scan_completed') {
      // Reload dashboard data when new run is created or scan completes
      loadDashboard();
    }
  }, [loadDashboard]);

  useEffect(() => {
    // Connect to WebSocket
    wsService.connect();
    
    // Subscribe to dashboard updates
    wsService.on('dashboard_update', handleDashboardUpdate);
    wsService.on('connected', () => {
      console.log('WebSocket connected, subscribing to dashboard');
      wsService.emit('subscribe_dashboard');
    });

    // Load initial dashboard data
    loadDashboard();

    // Cleanup on unmount
    return () => {
      wsService.off('dashboard_update', handleDashboardUpdate);
    };
  }, [handleDashboardUpdate, loadDashboard]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-blue"></div>
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Runs',
      value: dashboardData?.total_runs || 0,
      icon: ChartBarIcon,
      color: 'text-cyber-blue',
    },
    {
      name: 'Successful',
      value: dashboardData?.successful_runs || 0,
      icon: CheckCircleIcon,
      color: 'text-cyber-green',
    },
    {
      name: 'Failed',
      value: dashboardData?.failed_runs || 0,
      icon: XCircleIcon,
      color: 'text-red-500',
    },
    {
      name: 'Blocked',
      value: dashboardData?.blocked_runs || 0,
      icon: ClockIcon,
      color: 'text-yellow-500',
    },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">Overview of your security pipeline</p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">{stat.name}</p>
                <p className="text-3xl font-bold text-white mt-2">{stat.value}</p>
              </div>
              <stat.icon className={`w-12 h-12 ${stat.color}`} />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Success Rate */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h2 className="text-xl font-bold text-white mb-4">Success Rate</h2>
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyber-green transition-all duration-500"
                style={{ width: `${dashboardData?.success_rate || 0}%` }}
              />
            </div>
          </div>
          <span className="text-2xl font-bold text-cyber-green">
            {dashboardData?.success_rate || 0}%
          </span>
        </div>
      </motion.div>

      {/* Vulnerability Trend */}
      {dashboardData?.vulnerability_trend && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Vulnerability Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dashboardData.vulnerability_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#0A0E27', border: '1px solid #00D9FF' }} />
              <Legend />
              <Line type="monotone" dataKey="critical" stroke="#EF4444" name="Critical" />
              <Line type="monotone" dataKey="total" stroke="#00D9FF" name="Total" />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      )}

      {/* Scan Summary Cards */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {/* SonarQube Card */}
        <div className="card cursor-pointer hover:border-cyber-blue transition-colors" onClick={() => navigate('/scans/sonarqube')}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <CodeBracketIcon className="w-6 h-6 text-cyber-blue" />
              SonarQube (SAST)
            </h3>
            {scanSummaries.sonarqube && (
              <span className={`px-2 py-1 rounded text-xs ${
                scanSummaries.sonarqube.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {scanSummaries.sonarqube.status}
              </span>
            )}
          </div>
          {scanSummaries.sonarqube ? (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Critical Issues:</span>
                <span className="text-red-400 font-bold">{scanSummaries.sonarqube.critical || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total Issues:</span>
                <span className="text-white font-bold">{scanSummaries.sonarqube.total || 0}</span>
              </div>
              {scanSummaries.sonarqube.quality_gate && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Quality Gate:</span>
                  <span className={`font-bold ${
                    scanSummaries.sonarqube.quality_gate.status === 'PASSED' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {scanSummaries.sonarqube.quality_gate.status}
                  </span>
                </div>
              )}
              {scanSummaries.sonarqube.metrics?.coverage !== undefined && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Coverage:</span>
                  <span className="text-cyber-green font-bold">{scanSummaries.sonarqube.metrics.coverage.toFixed(1)}%</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No scan data available</p>
          )}
          <button className="mt-4 text-cyber-blue hover:text-cyber-blue/80 text-sm font-medium">
            View Details →
          </button>
        </div>

        {/* ZAP Card */}
        <div className="card cursor-pointer hover:border-cyber-blue transition-colors" onClick={() => navigate('/scans/zap')}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <ShieldExclamationIcon className="w-6 h-6 text-orange-500" />
              OWASP ZAP (DAST)
            </h3>
            {scanSummaries.zap && (
              <span className={`px-2 py-1 rounded text-xs ${
                scanSummaries.zap.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {scanSummaries.zap.status}
              </span>
            )}
          </div>
          {scanSummaries.zap ? (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">High Risk Alerts:</span>
                <span className="text-red-400 font-bold">{scanSummaries.zap.high || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total Alerts:</span>
                <span className="text-white font-bold">{scanSummaries.zap.total || 0}</span>
              </div>
              {scanSummaries.zap.spider_results && (
                <div className="flex justify-between">
                  <span className="text-gray-400">URLs Scanned:</span>
                  <span className="text-white font-bold">{scanSummaries.zap.spider_results.urls_found || 0}</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No scan data available</p>
          )}
          <button className="mt-4 text-cyber-blue hover:text-cyber-blue/80 text-sm font-medium">
            View Details →
          </button>
        </div>

        {/* Trivy Card */}
        <div className="card cursor-pointer hover:border-cyber-blue transition-colors" onClick={() => navigate('/scans/trivy')}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <BugAntIcon className="w-6 h-6 text-purple-500" />
              Trivy (Container)
            </h3>
            {scanSummaries.trivy && (
              <span className={`px-2 py-1 rounded text-xs ${
                scanSummaries.trivy.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {scanSummaries.trivy.status}
              </span>
            )}
          </div>
          {scanSummaries.trivy ? (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Critical CVEs:</span>
                <span className="text-red-400 font-bold">{scanSummaries.trivy.critical || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total Vulnerabilities:</span>
                <span className="text-white font-bold">{scanSummaries.trivy.total || 0}</span>
              </div>
              {scanSummaries.trivy.os_packages && (
                <div className="flex justify-between">
                  <span className="text-gray-400">OS Packages:</span>
                  <span className="text-white font-bold">{scanSummaries.trivy.os_packages.total || 0}</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No scan data available</p>
          )}
          <button className="mt-4 text-cyber-blue hover:text-cyber-blue/80 text-sm font-medium">
            View Details →
          </button>
        </div>
      </motion.div>

      {/* Recent Runs */}
      {dashboardData?.recent_runs && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Recent Runs</h2>
          <div className="space-y-2">
            {dashboardData.recent_runs.map((run) => (
              <div
                key={run.id}
                className="flex items-center justify-between p-3 bg-cyber-dark rounded-lg cursor-pointer hover:bg-gray-800 transition-colors"
                onClick={() => navigate(`/cicd/runs/${run.id}`)}
              >
                <div>
                  <p className="text-sm font-medium text-white">
                    {run.commit_hash?.substring(0, 8)} - {run.branch}
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(run.created_at).toLocaleString()}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded text-xs font-medium ${
                    run.status === 'Success'
                      ? 'bg-green-500/20 text-green-400'
                      : run.status === 'Failed'
                      ? 'bg-red-500/20 text-red-400'
                      : run.status === 'Blocked'
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-gray-500/20 text-gray-400'
                  }`}
                >
                  {run.status}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Dashboard;

