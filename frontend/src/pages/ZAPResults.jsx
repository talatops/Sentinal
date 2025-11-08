import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { cicdService } from '../services/cicdService';
import {
  ExclamationTriangleIcon,
  ShieldExclamationIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const ZAPResults = () => {
  const { runId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    risk: [],
    confidence: [],
    alert_name: '',
    url: '',
    cwe: '',
    search: '',
    page: 1,
    per_page: 50,
  });
  const [showFilters, setShowFilters] = useState(false);
  const [expandedRows, setExpandedRows] = useState(new Set());

  useEffect(() => {
    loadData();
  }, [runId, filters.page, filters.per_page]);

  const loadData = async () => {
    try {
      setLoading(true);
      const result = runId
        ? await cicdService.getRunDAST(parseInt(runId), filters)
        : await cicdService.getLatestZAP();
      
      if (runId && result.results) {
        setData(result.results);
      } else if (!runId && result.dast_results) {
        setData(result.dast_results);
      }
    } catch (error) {
      console.error('Failed to load ZAP results:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleRow = (alertId) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(alertId)) {
      newExpanded.delete(alertId);
    } else {
      newExpanded.add(alertId);
    }
    setExpandedRows(newExpanded);
  };

  const applyFilters = (newFilters) => {
    setFilters({ ...filters, ...newFilters, page: 1 });
  };

  const getRiskColor = (risk) => {
    const colors = {
      Critical: 'text-red-500',
      High: 'text-orange-500',
      Medium: 'text-yellow-500',
      Low: 'text-blue-500',
      Informational: 'text-gray-500',
    };
    return colors[risk] || 'text-gray-500';
  };

  const getRiskBg = (risk) => {
    const colors = {
      Critical: 'bg-red-500/20 text-red-400',
      High: 'bg-orange-500/20 text-orange-400',
      Medium: 'bg-yellow-500/20 text-yellow-400',
      Low: 'bg-blue-500/20 text-blue-400',
      Informational: 'bg-gray-500/20 text-gray-400',
    };
    return colors[risk] || 'bg-gray-500/20 text-gray-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-blue"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card text-center">
        <p className="text-gray-400">No ZAP results available</p>
      </div>
    );
  }

  const alerts = data.alerts || [];
  const pagination = data.pagination || { page: 1, per_page: 50, total: alerts.length, pages: 1 };

  const stats = [
    { name: 'Total Alerts', value: data.total || 0, icon: ShieldExclamationIcon, color: 'text-cyber-blue' },
    { name: 'Critical', value: data.critical || 0, icon: ExclamationTriangleIcon, color: 'text-red-500' },
    { name: 'High', value: data.high || 0, icon: ExclamationTriangleIcon, color: 'text-orange-500' },
    { name: 'Medium', value: data.medium || 0, icon: ExclamationTriangleIcon, color: 'text-yellow-500' },
    { name: 'Low', value: data.low || 0, icon: ExclamationTriangleIcon, color: 'text-blue-500' },
  ];

  const riskData = [
    { name: 'Critical', value: data.critical || 0 },
    { name: 'High', value: data.high || 0 },
    { name: 'Medium', value: data.medium || 0 },
    { name: 'Low', value: data.low || 0 },
  ].filter(item => item.value > 0);

  const COLORS = ['#EF4444', '#F97316', '#EAB308', '#3B82F6'];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">OWASP ZAP Results</h1>
          <p className="text-gray-400">
            Target: {data.target || 'N/A'} | 
            {data.scan_start ? ` Scanned: ${new Date(data.scan_start).toLocaleString()}` : ''}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center gap-2"
          >
            <FunnelIcon className="w-5 h-5" />
            Filters
          </button>
          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Back to Dashboard
          </button>
        </div>
      </motion.div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
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

      {/* Scan Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Scan Status</h2>
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${
            data.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
          }`}>
            <span className="font-semibold">{data.status?.toUpperCase()}</span>
          </div>
          {data.spider_results && (
            <p className="text-sm text-gray-400 mt-2">
              URLs Found: {data.spider_results.urls_found || 0}
            </p>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Alert Distribution</h2>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={60}
                fill="#8884d8"
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="card"
        >
          <h3 className="text-lg font-bold text-white mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Risk Level</label>
              <select
                multiple
                className="input-field w-full"
                value={filters.risk}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value);
                  applyFilters({ risk: values });
                }}
              >
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
                <option value="Informational">Informational</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Search</label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  className="input-field w-full pl-10"
                  placeholder="Search alerts..."
                  value={filters.search}
                  onChange={(e) => applyFilters({ search: e.target.value })}
                />
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Alerts Table */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">Alerts ({pagination.total})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400">Risk</th>
                <th className="text-left py-3 px-4 text-gray-400">Confidence</th>
                <th className="text-left py-3 px-4 text-gray-400">Alert Name</th>
                <th className="text-left py-3 px-4 text-gray-400">URL</th>
                <th className="text-left py-3 px-4 text-gray-400">Parameter</th>
                <th className="text-left py-3 px-4 text-gray-400">CWE</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <>
                  <tr
                    key={alert.id}
                    className="border-b border-gray-800 hover:bg-cyber-dark cursor-pointer"
                    onClick={() => toggleRow(alert.id)}
                  >
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskBg(alert.risk)}`}>
                        {alert.risk}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-300">{alert.confidence}</td>
                    <td className="py-3 px-4 text-gray-300">{alert.name}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm max-w-xs truncate">{alert.url}</td>
                    <td className="py-3 px-4 text-gray-300">{alert.param || '-'}</td>
                    <td className="py-3 px-4 text-gray-300">{alert.cweid || '-'}</td>
                  </tr>
                  {expandedRows.has(alert.id) && (
                    <tr>
                      <td colSpan={6} className="py-4 px-4 bg-cyber-dark">
                        <div className="space-y-2">
                          <div>
                            <strong className="text-cyber-blue">Description:</strong>
                            <p className="text-gray-300 mt-1">{alert.description}</p>
                          </div>
                          {alert.solution && (
                            <div>
                              <strong className="text-cyber-blue">Solution:</strong>
                              <p className="text-gray-300 mt-1">{alert.solution}</p>
                            </div>
                          )}
                          {alert.attack && (
                            <div>
                              <strong className="text-cyber-blue">Attack Vector:</strong>
                              <code className="block mt-1 p-2 bg-gray-800 rounded text-sm">{alert.attack}</code>
                            </div>
                          )}
                          {alert.evidence && (
                            <div>
                              <strong className="text-cyber-blue">Evidence:</strong>
                              <code className="block mt-1 p-2 bg-gray-800 rounded text-sm">{alert.evidence}</code>
                            </div>
                          )}
                          {alert.reference && (
                            <div>
                              <strong className="text-cyber-blue">Reference:</strong>
                              <a href={alert.reference} target="_blank" rel="noopener noreferrer" className="text-cyber-blue hover:underline ml-2">
                                {alert.reference}
                              </a>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
        {pagination.pages > 1 && (
          <div className="flex items-center justify-between mt-4">
            <button
              onClick={() => applyFilters({ page: pagination.page - 1 })}
              disabled={pagination.page === 1}
              className="btn-secondary disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-gray-400">
              Page {pagination.page} of {pagination.pages}
            </span>
            <button
              onClick={() => applyFilters({ page: pagination.page + 1 })}
              disabled={pagination.page >= pagination.pages}
              className="btn-secondary disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default ZAPResults;

