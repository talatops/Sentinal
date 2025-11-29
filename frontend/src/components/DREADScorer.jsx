import { useState, useEffect } from 'react';
// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion';
import {
  InformationCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

const DREADScorer = ({ 
  suggestedScores = {}, 
  confidence = {}, 
  explanations = {},
  onScoresChange,
  autoScore = false 
}) => {
  const [scores, setScores] = useState({
    damage: suggestedScores.damage || 5,
    reproducibility: suggestedScores.reproducibility || 5,
    exploitability: suggestedScores.exploitability || 5,
    affected_users: suggestedScores.affected_users || 5,
    discoverability: suggestedScores.discoverability || 5,
  });

  useEffect(() => {
    if (autoScore && Object.keys(suggestedScores).length > 0) {
      setScores(suggestedScores);
    }
  }, [suggestedScores, autoScore]);

  useEffect(() => {
    if (onScoresChange) {
      onScoresChange(scores);
    }
  }, [scores, onScoresChange]);

  const handleSliderChange = (key, value) => {
    setScores(prev => ({
      ...prev,
      [key]: parseInt(value)
    }));
  };

  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return 'text-green-400 bg-green-500/20 border-green-500/30';
    if (conf >= 0.6) return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
    return 'text-orange-400 bg-orange-500/20 border-orange-500/30';
  };

  const getConfidenceBadge = (conf) => {
    if (conf >= 0.8) return 'High';
    if (conf >= 0.6) return 'Medium';
    return 'Low';
  };

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-red-400';
    if (score >= 5) return 'text-yellow-400';
    return 'text-green-400';
  };

  const acceptAllSuggestions = () => {
    if (Object.keys(suggestedScores).length > 0) {
      setScores(suggestedScores);
    }
  };

  const dreadLabels = {
    damage: 'Damage',
    reproducibility: 'Reproducibility',
    exploitability: 'Exploitability',
    affected_users: 'Affected Users',
    discoverability: 'Discoverability',
  };

  const totalScore = Object.values(scores).reduce((sum, val) => sum + val, 0) / 5;
  const riskLevel = totalScore > 7 ? 'High' : totalScore > 4 ? 'Medium' : 'Low';

  return (
    <div className="space-y-6">
      {autoScore && Object.keys(suggestedScores).length > 0 && (
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <InformationCircleIcon className="w-5 h-5 text-cyber-blue" />
            <p className="text-sm text-gray-400">
              Scores have been automatically suggested based on threat patterns
            </p>
          </div>
          <button
            onClick={acceptAllSuggestions}
            className="px-3 py-1 text-sm bg-cyber-blue/20 text-cyber-blue rounded hover:bg-cyber-blue/30 transition"
          >
            Accept All Suggestions
          </button>
        </div>
      )}

      <div className="space-y-4">
        {Object.entries(dreadLabels).map(([key, label]) => {
          const score = scores[key];
          const conf = confidence[key] || 0.5;
          const explanation = explanations[key] || '';

          return (
            <motion.div
              key={key}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-cyber-dark p-4 rounded-lg border border-gray-700/50"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium text-white">
                    {label}
                  </label>
                  {autoScore && (
                    <span className={`px-2 py-0.5 text-xs rounded border ${getConfidenceColor(conf)}`}>
                      {getConfidenceBadge(conf)} Confidence
                    </span>
                  )}
                </div>
                <span className={`text-lg font-bold ${getScoreColor(score)}`}>
                  {score}/10
                </span>
              </div>

              <input
                type="range"
                min="0"
                max="10"
                value={score}
                onChange={(e) => handleSliderChange(key, e.target.value)}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyber-blue"
                style={{
                  background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(score / 10) * 100}%, #374151 ${(score / 10) * 100}%, #374151 100%)`
                }}
              />

              <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                <span>Low (0)</span>
                <span>Medium (5)</span>
                <span>High (10)</span>
              </div>

              {explanation && (
                <div className="mt-3 p-2 bg-gray-800/50 rounded text-xs text-gray-400">
                  <InformationCircleIcon className="w-4 h-4 inline mr-1" />
                  {explanation}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      <div className="bg-cyber-dark p-4 rounded-lg border border-gray-700/50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400 mb-1">Total DREAD Score</p>
            <p className="text-2xl font-bold text-white">{totalScore.toFixed(2)}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-400 mb-1">Risk Level</p>
            <span
              className={`px-4 py-2 rounded-lg font-bold ${
                riskLevel === 'High'
                  ? 'text-red-400 bg-red-500/20 border border-red-500/30'
                  : riskLevel === 'Medium'
                  ? 'text-yellow-400 bg-yellow-500/20 border border-yellow-500/30'
                  : 'text-green-400 bg-green-500/20 border border-green-500/30'
              }`}
            >
              {riskLevel}
            </span>
          </div>
        </div>
      </div>

      {explanations.pattern_context && (
        <div className="p-3 bg-cyber-blue/10 border border-cyber-blue/30 rounded-lg">
          <p className="text-sm text-cyber-blue">{explanations.pattern_context}</p>
        </div>
      )}

      {explanations.component_context && (
        <div className="p-3 bg-cyber-blue/10 border border-cyber-blue/30 rounded-lg">
          <p className="text-sm text-cyber-blue">{explanations.component_context}</p>
        </div>
      )}
    </div>
  );
};

export default DREADScorer;

