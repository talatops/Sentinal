import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { cicdService } from '../services/cicdService';
import {
  ShieldExclamationIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const TrivyResults = () => {
  const { runId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    severity: [],
    package: '',
    cve: '',
    package_type: '',
    cvss_min: '',
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
        ? await cicdService.getRunTrivy(parseInt(runId), filters)
        : await cicdService.getLatestTrivy();
      
      if (runId && result.results) {
        setData(result.results);
      } else if (!runId && result.trivy_results) {
        setData(result.trivy_results);
      }
    } catch (error) {
      console.error('Failed to load Trivy results:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleRow = (vulnId) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(vulnId)) {
      newExpanded.delete(vulnId);
    } else {
      newExpanded.add(vulnId);
    }
    setExpandedRows(newExpanded);
  };

  const applyFilters = (newFilters) => {
    setFilters({ ...filters, ...newFilters, page: 1 });
  };

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: 'text-red-500',
      HIGH: 'text-orange-500',
      MEDIUM: 'text-yellow-500',
      LOW: 'text-blue-500',
      UNKNOWN: 'text-gray-500',
    };
    return colors[severity] || 'text-gray-500';
  };

  const getSeverityBg = (severity) => {
    const colors = {
      CRITICAL: 'bg-red-500/20 text-red-400',
      HIGH: 'bg-orange-500/20 text-orange-400',
      MEDIUM: 'bg-yellow-500/20 text-yellow-400',
      LOW: 'bg-blue-500/20 text-blue-400',
      UNKNOWN: 'bg-gray-500/20 text-gray-400',
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
        <p className="text-gray-400">No Trivy results available</p>
      </div>
    );
  }

  const vulnerabilities = data.vulnerabilities || [];
  const pagination = data.pagination || { page: 1, per_page: 50, total: vulnerabilities.length, pages: 1 };
  const metadata = data.metadata || {};

  const stats = [
    { name: 'Total Vulnerabilities', value: data.total || 0, icon: ShieldExclamationIcon, color: 'text-cyber-blue' },
    { name: 'Critical', value: data.critical || 0, icon: ExclamationTriangleIcon, color: 'text-red-500' },
    { name: 'High', value: data.high || 0, icon: ExclamationTriangleIcon, color: 'text-orange-500' },
    { name: 'Medium', value: data.medium || 0, icon: ExclamationTriangleIcon, color: 'text-yellow-500' },
    { name: 'Low', value: data.low || 0, icon: ExclamationTriangleIcon, color: 'text-blue-500' },
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
          <h1 className="text-3xl font-bold text-white mb-2">Trivy Scan Results</h1>
          <p className="text-gray-400">
            Image: {data.image || 'N/A'} | 
            {data.scan_timestamp ? ` Scanned: ${new Date(data.scan_timestamp).toLocaleString()}` : ''}
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

      {/* Package Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Package Summary</h2>
          {data.os_packages && (
            <div className="mb-4">
              <p className="text-gray-400">OS Packages: {data.os_packages.total || 0}</p>
              <p className="text-red-400">Vulnerable: {data.os_packages.vulnerable || 0}</p>
            </div>
          )}
          {data.language_packages && Object.keys(data.language_packages).length > 0 && (
            <div>
              <p className="text-gray-400 mb-2">Language Packages:</p>
              {Object.entries(data.language_packages).map(([lang, info]) => (
                <div key={lang} className="mb-2">
                  <p className="text-sm text-gray-300 capitalize">{lang}: {info.total || 0} total, {info.vulnerable || 0} vulnerable</p>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Vulnerability Distribution</h2>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={60}
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
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
                <option value="UNKNOWN">Unknown</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Search</label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  className="input-field w-full pl-10"
                  placeholder="Search CVE or package..."
                  value={filters.search}
                  onChange={(e) => applyFilters({ search: e.target.value })}
                />
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Vulnerabilities Table */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">Vulnerabilities ({pagination.total})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400">Severity</th>
                <th className="text-left py-3 px-4 text-gray-400">CVE ID</th>
                <th className="text-left py-3 px-4 text-gray-400">Package</th>
                <th className="text-left py-3 px-4 text-gray-400">Installed</th>
                <th className="text-left py-3 px-4 text-gray-400">Fixed</th>
                <th className="text-left py-3 px-4 text-gray-400">CVSS</th>
              </tr>
            </thead>
            <tbody>
              {vulnerabilities.map((vuln) => (
                <>
                  <tr
                    key={vuln.vulnerability_id}
                    className="border-b border-gray-800 hover:bg-cyber-dark cursor-pointer"
                    onClick={() => toggleRow(vuln.vulnerability_id)}
                  >
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityBg(vuln.severity)}`}>
                        {vuln.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{vuln.vulnerability_id}</td>
                    <td className="py-3 px-4 text-gray-300">{vuln.pkg_name}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{vuln.installed_version || '-'}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{vuln.fixed_version || '-'}</td>
                    <td className="py-3 px-4 text-gray-300">
                      {vuln.cvss?.v3?.score || vuln.cvss?.v2?.score || '-'}
                    </td>
                  </tr>
                  {expandedRows.has(vuln.vulnerability_id) && (
                    <tr>
                      <td colSpan={6} className="py-4 px-4 bg-cyber-dark">
                        <div className="space-y-2">
                          <div>
                            <strong className="text-cyber-blue">Title:</strong> {vuln.title || vuln.vulnerability_id}
                          </div>
                          {vuln.description && (
                            <div>
                              <strong className="text-cyber-blue">Description:</strong>
                              <p className="text-gray-300 mt-1">{vuln.description}</p>
                            </div>
                          )}
                          {vuln.cvss && (
                            <div>
                              <strong className="text-cyber-blue">CVSS Scores:</strong>
                              {vuln.cvss.v3 && (
                                <p className="text-gray-300 mt-1">v3: {vuln.cvss.v3.score} ({vuln.cvss.v3.vector})</p>
                              )}
                              {vuln.cvss.v2 && (
                                <p className="text-gray-300">v2: {vuln.cvss.v2.score} ({vuln.cvss.v2.vector})</p>
                              )}
                            </div>
                          )}
                          {vuln.cwe_ids && vuln.cwe_ids.length > 0 && (
                            <div>
                              <strong className="text-cyber-blue">CWE IDs:</strong>{' '}
                              {vuln.cwe_ids.map(cwe => (
                                <span key={cwe} className="px-2 py-1 bg-gray-700 rounded text-xs mr-1">{cwe}</span>
                              ))}
                            </div>
                          )}
                          {vuln.references && vuln.references.length > 0 && (
                            <div>
                              <strong className="text-cyber-blue">References:</strong>
                              <ul className="list-disc list-inside mt-1">
                                {vuln.references.map((ref, idx) => (
                                  <li key={idx}>
                                    <a href={ref} target="_blank" rel="noopener noreferrer" className="text-cyber-blue hover:underline">
                                      {ref}
                                    </a>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {vuln.primary_url && (
                            <div>
                              <strong className="text-cyber-blue">Primary URL:</strong>{' '}
                              <a href={vuln.primary_url} target="_blank" rel="noopener noreferrer" className="text-cyber-blue hover:underline">
                                {vuln.primary_url}
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

export default TrivyResults;

