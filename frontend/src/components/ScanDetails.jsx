// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion';
import { CheckCircleIcon, XCircleIcon, ClockIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const ScanDetails = ({ scan, onRetry, onCancel, onExport }) => {
  if (!scan) return null;

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
      case 'Success':
        return <CheckCircleIcon className="w-6 h-6 text-green-400" />;
      case 'failed':
      case 'Failed':
        return <XCircleIcon className="w-6 h-6 text-red-400" />;
      case 'running':
      case 'Running':
        return <ClockIcon className="w-6 h-6 text-yellow-400 animate-spin" />;
      default:
        return <ExclamationTriangleIcon className="w-6 h-6 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
      case 'Success':
        return 'bg-green-500/20 text-green-400';
      case 'failed':
      case 'Failed':
        return 'bg-red-500/20 text-red-400';
      case 'running':
      case 'Running':
        return 'bg-yellow-500/20 text-yellow-400';
      default:
        return 'bg-gray-500/20 text-gray-400';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {getStatusIcon(scan.status)}
          <div>
            <h3 className="text-lg font-bold text-white">Scan Details</h3>
            <p className="text-sm text-gray-400">
              {scan.scan_timestamp || scan.created_at
                ? new Date(scan.scan_timestamp || scan.created_at).toLocaleString()
                : 'No timestamp'}
            </p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(scan.status)}`}>
          {scan.status}
        </span>
      </div>

      {scan.status === 'running' && scan.active_scan_progress !== undefined && (
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>Progress</span>
            <span>{scan.active_scan_progress}%</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyber-blue transition-all duration-300"
              style={{ width: `${scan.active_scan_progress}%` }}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-4">
        {scan.target && (
          <div>
            <p className="text-sm text-gray-400">Target</p>
            <p className="text-white font-medium">{scan.target}</p>
          </div>
        )}
        {scan.image && (
          <div>
            <p className="text-sm text-gray-400">Image</p>
            <p className="text-white font-medium">{scan.image}</p>
          </div>
        )}
        {scan.commit_hash && (
          <div>
            <p className="text-sm text-gray-400">Commit</p>
            <p className="text-white font-medium font-mono text-sm">{scan.commit_hash.substring(0, 8)}</p>
          </div>
        )}
        {scan.branch && (
          <div>
            <p className="text-sm text-gray-400">Branch</p>
            <p className="text-white font-medium">{scan.branch}</p>
          </div>
        )}
      </div>

      {scan.error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg">
          <p className="text-sm text-red-400">{scan.error}</p>
        </div>
      )}

      <div className="flex gap-2">
        {onRetry && (
          <button onClick={onRetry} className="btn-secondary text-sm">
            Retry
          </button>
        )}
        {onCancel && scan.status === 'running' && (
          <button onClick={onCancel} className="btn-secondary text-sm">
            Cancel
          </button>
        )}
        {onExport && scan.status === 'completed' && (
          <button onClick={onExport} className="btn-primary text-sm">
            Export
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default ScanDetails;

