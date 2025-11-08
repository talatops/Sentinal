import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { cicdService } from '../services/cicdService';
import {
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const SonarQubeResults = () => {
  const { runId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    severity: [],
    type: [],
    status: [],
    component: '',
    rule: '',
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
        ? await cicdService.getRunSAST(parseInt(runId), filters)
        : await cicdService.getLatestSonarQube();
      
      if (runId && result.results) {
        setData(result.results);
      } else if (!runId && result.sast_results) {
        setData(result.sast_results);
      }
    } catch (error) {
      console.error('Failed to load SonarQube results:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleRow = (issueKey) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(issueKey)) {
      newExpanded.delete(issueKey);
    } else {
      newExpanded.add(issueKey);
    }
    setExpandedRows(newExpanded);
  };

  const applyFilters = (newFilters) => {
    setFilters({ ...filters, ...newFilters, page: 1 });
  };

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: 'text-red-500',
      BLOCKER: 'text-red-600',
      MAJOR: 'text-orange-500',
      MINOR: 'text-yellow-500',
      INFO: 'text-blue-500',
    };
    return colors[severity] || 'text-gray-500';
  };

  const getSeverityBg = (severity) => {
    const colors = {
      CRITICAL: 'bg-red-500/20 text-red-400',
      BLOCKER: 'bg-red-600/20 text-red-500',
      MAJOR: 'bg-orange-500/20 text-orange-400',
      MINOR: 'bg-yellow-500/20 text-yellow-400',
      INFO: 'bg-blue-500/20 text-blue-400',
    };
    return colors[severity] || 'bg-gray-500/20 text-gray-400';
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
        <p className="text-gray-400">No SonarQube results available</p>
      </div>
    );
  }

  const issues = data.issues || [];
  const metrics = data.metrics || {};
  const qualityGate = data.quality_gate || {};
  const pagination = data.pagination || { page: 1, per_page: 50, total: issues.length, pages: 1 };

  const stats = [
    { name: 'Total Issues', value: data.total || 0, icon: ExclamationTriangleIcon, color: 'text-cyber-blue' },
    { name: 'Critical', value: data.critical || 0, icon: XCircleIcon, color: 'text-red-500' },
    { name: 'High', value: data.high || 0, icon: ExclamationTriangleIcon, color: 'text-orange-500' },
    { name: 'Medium', value: data.medium || 0, icon: InformationCircleIcon, color: 'text-yellow-500' },
    { name: 'Low', value: data.low || 0, icon: InformationCircleIcon, color: 'text-blue-500' },
  ];

  const severityData = [
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
          <h1 className="text-3xl font-bold text-white mb-2">SonarQube Results</h1>
          <p className="text-gray-400">
            {data.scan_timestamp ? `Last scanned: ${new Date(data.scan_timestamp).toLocaleString()}` : 'Scan results'}
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

      {/* Quality Gate & Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Quality Gate</h2>
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${
            qualityGate.status === 'PASSED' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            {qualityGate.status === 'PASSED' ? (
              <CheckCircleIcon className="w-6 h-6" />
            ) : (
              <XCircleIcon className="w-6 h-6" />
            )}
            <span className="font-semibold">{qualityGate.status}</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Code Coverage</h2>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-cyber-green transition-all duration-500"
                  style={{ width: `${metrics.coverage || 0}%` }}
                />
              </div>
            </div>
            <span className="text-2xl font-bold text-cyber-green">
              {metrics.coverage?.toFixed(1) || 0}%
            </span>
          </div>
          {metrics.technical_debt && (
            <p className="text-sm text-gray-400 mt-2">Technical Debt: {metrics.technical_debt}</p>
          )}
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
              <label className="block text-sm font-medium mb-2">Severity</label>
              <select
                multiple
                className="input-field w-full"
                value={filters.severity}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value);
                  applyFilters({ severity: values });
                }}
              >
                <option value="CRITICAL">Critical</option>
                <option value="BLOCKER">Blocker</option>
                <option value="MAJOR">Major</option>
                <option value="MINOR">Minor</option>
                <option value="INFO">Info</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Type</label>
              <select
                multiple
                className="input-field w-full"
                value={filters.type}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value);
                  applyFilters({ type: values });
                }}
              >
                <option value="BUG">Bug</option>
                <option value="VULNERABILITY">Vulnerability</option>
                <option value="CODE_SMELL">Code Smell</option>
                <option value="SECURITY_HOTSPOT">Security Hotspot</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Search</label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  className="input-field w-full pl-10"
                  placeholder="Search issues..."
                  value={filters.search}
                  onChange={(e) => applyFilters({ search: e.target.value })}
                />
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Issues by Severity</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {severityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Issues by Type</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { name: 'Bugs', value: metrics.bugs || 0 },
              { name: 'Vulnerabilities', value: metrics.vulnerabilities || 0 },
              { name: 'Code Smells', value: metrics.code_smells || 0 },
              { name: 'Hotspots', value: metrics.security_hotspots || 0 },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#0A0E27', border: '1px solid #00D9FF' }} />
              <Bar dataKey="value" fill="#00D9FF" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Issues Table */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">Issues ({pagination.total})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400">Severity</th>
                <th className="text-left py-3 px-4 text-gray-400">Type</th>
                <th className="text-left py-3 px-4 text-gray-400">Component</th>
                <th className="text-left py-3 px-4 text-gray-400">Line</th>
                <th className="text-left py-3 px-4 text-gray-400">Message</th>
                <th className="text-left py-3 px-4 text-gray-400">Status</th>
              </tr>
            </thead>
            <tbody>
              {issues.map((issue) => (
                <>
                  <tr
                    key={issue.key}
                    className="border-b border-gray-800 hover:bg-cyber-dark cursor-pointer"
                    onClick={() => toggleRow(issue.key)}
                  >
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityBg(issue.severity)}`}>
                        {issue.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-300">{issue.type}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{issue.component?.split(':').pop()}</td>
                    <td className="py-3 px-4 text-gray-300">{issue.line || '-'}</td>
                    <td className="py-3 px-4 text-gray-300">{issue.message}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs ${
                        issue.status === 'OPEN' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'
                      }`}>
                        {issue.status}
                      </span>
                    </td>
                  </tr>
                  {expandedRows.has(issue.key) && (
                    <tr>
                      <td colSpan={6} className="py-4 px-4 bg-cyber-dark">
                        <div className="space-y-2">
                          <div>
                            <strong className="text-cyber-blue">Rule:</strong> {issue.rule_name || issue.rule}
                          </div>
                          {issue.rule_description && (
                            <div>
                              <strong className="text-cyber-blue">Description:</strong>
                              <div className="text-gray-300 mt-1" dangerouslySetInnerHTML={{ __html: issue.rule_description }} />
                            </div>
                          )}
                          {issue.effort && (
                            <div>
                              <strong className="text-cyber-blue">Effort:</strong> {issue.effort}
                            </div>
                          )}
                          {issue.tags && issue.tags.length > 0 && (
                            <div>
                              <strong className="text-cyber-blue">Tags:</strong>{' '}
                              {issue.tags.map(tag => (
                                <span key={tag} className="px-2 py-1 bg-gray-700 rounded text-xs mr-1">{tag}</span>
                              ))}
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

export default SonarQubeResults;

