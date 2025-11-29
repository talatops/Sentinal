import { useState, useEffect } from 'react';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import { threatService } from '../services/threatService';
import DREADScorer from '../components/DREADScorer';
import ThreatDiagram from '../components/ThreatDiagram';
import ThreatMatrix from '../components/ThreatMatrix';
import { z } from 'zod';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon, 
  InformationCircleIcon,
  CheckCircleIcon,
  LightBulbIcon,
  ChartBarIcon,
  Squares2X2Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';


// Component to render mitigation recommendations with better styling
const MitigationList = ({ mitigation, riskLevel }) => {
  // Parse mitigation text into individual recommendations
  const parseMitigations = (text) => {
    if (!text) return [];
    
    // Split by common delimiters (newlines, periods followed by space, numbered lists, etc.)
    const lines = text
      .split(/\n+|(?<=\.)\s+(?=[A-Z])|(?<=\d+\.)\s+/)
      .map(line => line.trim())
      .filter(line => line.length > 0);
    
    return lines;
  };

  const recommendations = parseMitigations(mitigation);

  const getRecommendationType = (rec) => {
    const lower = rec.toLowerCase();
    if (lower.includes('urgent') || lower.includes('immediate') || lower.includes('critical')) {
      return 'urgent';
    }
    if (lower.includes('consider') || lower.includes('recommend') || lower.includes('should')) {
      return 'suggestion';
    }
    if (lower.includes('implement') || lower.includes('use') || lower.includes('enable')) {
      return 'action';
    }
    return 'info';
  };

  const getIcon = (type) => {
    switch (type) {
      case 'urgent':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-400 flex-shrink-0" />;
      case 'action':
        return <CheckCircleIcon className="w-5 h-5 text-green-400 flex-shrink-0" />;
      case 'suggestion':
        return <LightBulbIcon className="w-5 h-5 text-yellow-400 flex-shrink-0" />;
      default:
        return <InformationCircleIcon className="w-5 h-5 text-cyber-blue flex-shrink-0" />;
    }
  };

  const getRecommendationStyle = (type) => {
    switch (type) {
      case 'urgent':
        return 'bg-red-500/10 border-red-500/30 text-red-300';
      case 'action':
        return 'bg-green-500/10 border-green-500/30 text-green-300';
      case 'suggestion':
        return 'bg-yellow-500/10 border-yellow-500/30 text-yellow-300';
      default:
        return 'bg-cyber-blue/10 border-cyber-blue/30 text-gray-300';
    }
  };

  if (recommendations.length === 0) {
    return (
      <div className="flex items-center gap-2 text-gray-400">
        <InformationCircleIcon className="w-5 h-5" />
        <p className="text-sm">No specific recommendations available</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {recommendations.map((rec, index) => {
        const type = getRecommendationType(rec);
        const isUrgent = type === 'urgent' || riskLevel === 'High';
        
        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`flex items-start gap-3 p-3 rounded-lg border ${
              isUrgent 
                ? 'bg-red-500/10 border-red-500/30' 
                : getRecommendationStyle(type)
            }`}
          >
            <div className="mt-0.5">
              {getIcon(type)}
            </div>
            <div className="flex-1">
              <p className={`text-sm leading-relaxed ${
                isUrgent ? 'text-red-300 font-medium' : 'text-gray-300'
              }`}>
                {rec}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

const ThreatModeling = () => {
  const [formData, setFormData] = useState({
    asset: '',
    flow: '',
    trust_boundary: '',
    damage: 5,
    reproducibility: 5,
    exploitability: 5,
    affected_users: 5,
    discoverability: 5,
  });
  const [autoScore, setAutoScore] = useState(true);
  const [dreadScores, setDreadScores] = useState(null);
  const [threats, setThreats] = useState([]);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [showResultModal, setShowResultModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [selectedThreatForDiagram, setSelectedThreatForDiagram] = useState(null);
  const [viewMode, setViewMode] = useState('list'); // 'list', 'diagram', 'matrix'

  useEffect(() => {
    loadThreats();
  }, []);

  const loadThreats = async () => {
    try {
      const data = await threatService.getThreats();
      setThreats(data.threats || []);
    } catch (error) {
      console.error('Failed to load threats:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    try {
      // Build request data
      const requestData = {
        asset: formData.asset,
        flow: formData.flow,
        trust_boundary: formData.trust_boundary || undefined,
        auto_score: autoScore,
      };

      // Add DREAD scores only if not auto-scoring or if user has manually set them
      if (!autoScore) {
        // Manual mode - require all scores
        const threatSchemaManual = z.object({
          asset: z.string().min(1, 'Asset is required'),
          flow: z.string().min(1, 'Flow description is required'),
          trust_boundary: z.string().optional(),
          damage: z.number().min(0).max(10),
          reproducibility: z.number().min(0).max(10),
          exploitability: z.number().min(0).max(10),
          affected_users: z.number().min(0).max(10),
          discoverability: z.number().min(0).max(10),
        });
        const validated = threatSchemaManual.parse(formData);
        Object.assign(requestData, {
          damage: validated.damage,
          reproducibility: validated.reproducibility,
          exploitability: validated.exploitability,
          affected_users: validated.affected_users,
          discoverability: validated.discoverability,
        });
      } else if (dreadScores) {
        // Auto-score mode but user has adjusted scores
        Object.assign(requestData, dreadScores);
      }

      const result = await threatService.analyzeThreat(requestData);
      setAnalysisResult(result);
      setShowResultModal(true);
      console.log('Analysis complete, showing modal');
      await loadThreats();
      // Reset form after successful analysis
      setFormData({
        asset: '',
        flow: '',
        trust_boundary: '',
        damage: 5,
        reproducibility: 5,
        exploitability: 5,
        affected_users: 5,
        discoverability: 5,
      });
      setDreadScores(null);
    } catch (error) {
      if (error.errors) {
        const zodErrors = {};
        error.errors.forEach((err) => {
          zodErrors[err.path[0]] = err.message;
        });
        setErrors(zodErrors);
      } else {
        setErrors({ submit: error.response?.data?.error || 'Failed to analyze threat' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'High':
        return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'Medium':
        return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      case 'Low':
        return 'text-green-400 bg-green-500/20 border-green-500/30';
      default:
        return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white mb-2">Threat Modeling</h1>
        <p className="text-gray-400">STRIDE/DREAD threat analysis</p>
      </motion.div>

      {/* Form */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="card max-w-2xl mx-auto"
      >
        <h2 className="text-xl font-bold text-white mb-4">Analyze Threat</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Asset</label>
            <input
              type="text"
              value={formData.asset}
              onChange={(e) => handleInputChange('asset', e.target.value)}
              className="input-field w-full"
              placeholder="e.g., User Database"
            />
            {errors.asset && <p className="text-red-400 text-sm mt-1">{errors.asset}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Data Flow</label>
            <textarea
              value={formData.flow}
              onChange={(e) => handleInputChange('flow', e.target.value)}
              className="input-field w-full h-24"
              placeholder="Describe the data flow..."
            />
            {errors.flow && <p className="text-red-400 text-sm mt-1">{errors.flow}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Trust Boundary (Optional)</label>
            <input
              type="text"
              value={formData.trust_boundary}
              onChange={(e) => handleInputChange('trust_boundary', e.target.value)}
              className="input-field w-full"
              placeholder="e.g., Internal Network"
            />
          </div>

          <div className="flex items-center gap-3 p-3 bg-cyber-dark rounded-lg border border-gray-700/50">
            <input
              type="checkbox"
              id="auto-score"
              checked={autoScore}
              onChange={(e) => setAutoScore(e.target.checked)}
              className="w-4 h-4 text-cyber-blue bg-gray-700 border-gray-600 rounded focus:ring-cyber-blue"
            />
            <label htmlFor="auto-score" className="text-sm text-gray-300 cursor-pointer">
              Enable automatic DREAD scoring (pattern-based suggestions)
            </label>
          </div>

          {autoScore ? (
            <div className="bg-cyber-blue/10 border border-cyber-blue/30 p-3 rounded-lg">
              <p className="text-sm text-cyber-blue">
                <InformationCircleIcon className="w-4 h-4 inline mr-1" />
                DREAD scores will be automatically suggested based on threat pattern matching and component detection. Uses regex patterns and keyword analysis, not machine learning.
              </p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Damage (0-10)</label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={formData.damage}
                    onChange={(e) => handleInputChange('damage', parseInt(e.target.value))}
                    className="input-field w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Reproducibility (0-10)</label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={formData.reproducibility}
                    onChange={(e) => handleInputChange('reproducibility', parseInt(e.target.value))}
                    className="input-field w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Exploitability (0-10)</label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={formData.exploitability}
                    onChange={(e) => handleInputChange('exploitability', parseInt(e.target.value))}
                    className="input-field w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Affected Users (0-10)</label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={formData.affected_users}
                    onChange={(e) => handleInputChange('affected_users', parseInt(e.target.value))}
                    className="input-field w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Discoverability (0-10)</label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={formData.discoverability}
                  onChange={(e) => handleInputChange('discoverability', parseInt(e.target.value))}
                  className="input-field w-full"
                />
              </div>
            </>
          )}

          {errors.submit && (
            <div className="bg-red-500/20 border border-red-500 text-red-400 px-4 py-2 rounded">
              {errors.submit}
            </div>
          )}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing Threat...
              </span>
            ) : (
              'Analyze Threat'
            )}
          </button>
        </form>
      </motion.div>

      {/* Results Modal */}
      <AnimatePresence>
        {showResultModal && analysisResult && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
            onClick={() => {
              setShowResultModal(false);
              setAnalysisResult(null); // Clear results when closing
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="card max-w-4xl w-full max-h-[90vh] overflow-y-auto relative"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close Button */}
              <button
                onClick={() => {
                  setShowResultModal(false);
                  setAnalysisResult(null); // Clear results when closing
                }}
                className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors z-10 bg-cyber-dark/80 rounded-full p-1 hover:bg-cyber-dark"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>

              {/* Header */}
              <div className="mb-6 pr-10">
                <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                  <ShieldCheckIcon className="w-8 h-8 text-cyber-blue" />
                  Threat Analysis Results
                </h2>
                <p className="text-gray-400">STRIDE/DREAD analysis completed</p>
              </div>

              <div className="space-y-6">
                {/* Risk Level */}
                <div>
                  <p className="text-sm text-gray-400 mb-2">Risk Level</p>
                  <div className={`px-6 py-3 rounded-lg border text-center ${getRiskColor(analysisResult.analysis.risk_level)}`}>
                    <span className="text-xl font-bold">{analysisResult.analysis.risk_level}</span>
                  </div>
                </div>

                {/* STRIDE Categories */}
                <div>
                  <p className="text-sm text-gray-400 mb-3 font-medium">STRIDE Categories</p>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.analysis.stride_categories.map((category) => {
                      const confidence = analysisResult.analysis.stride_confidence?.[category];
                      return (
                        <span
                          key={category}
                          className="px-4 py-2 bg-cyber-blue/20 text-cyber-blue rounded-lg text-sm relative group border border-cyber-blue/30"
                          title={confidence !== undefined ? `Confidence: ${(confidence * 100).toFixed(0)}%` : ''}
                        >
                          {category}
                          {confidence !== undefined && (
                            <span className="ml-2 text-xs opacity-75">
                              ({(confidence * 100).toFixed(0)}%)
                            </span>
                          )}
                        </span>
                      );
                    })}
                  </div>
                  {analysisResult.analysis.matched_patterns?.length > 0 && (
                    <p className="text-xs text-gray-500 mt-3">
                      <span className="font-medium">Detected patterns:</span> {analysisResult.analysis.matched_patterns.join(', ')}
                    </p>
                  )}
                  {analysisResult.analysis.component_types?.length > 0 && (
                    <p className="text-xs text-gray-500 mt-1">
                      <span className="font-medium">Component types:</span> {analysisResult.analysis.component_types.join(', ')}
                    </p>
                  )}
                </div>

                {/* DREAD Score */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-400 mb-2">DREAD Score</p>
                    <div className="bg-cyber-dark p-4 rounded-lg border border-gray-700/50">
                      <p className="text-3xl font-bold text-white">{analysisResult.analysis.dread_score.toFixed(2)}</p>
                      <p className="text-xs text-gray-500 mt-1">Out of 10.0</p>
                    </div>
                  </div>
                  {analysisResult.analysis.primary_pattern && (
                    <div>
                      <p className="text-sm text-gray-400 mb-2">Primary Pattern</p>
                      <div className="bg-cyber-dark p-4 rounded-lg border border-gray-700/50">
                        <p className="text-lg font-medium text-white">{analysisResult.analysis.primary_pattern}</p>
                        {analysisResult.analysis.pattern_confidence && (
                          <p className="text-xs text-gray-500 mt-1">
                            Confidence: {(analysisResult.analysis.pattern_confidence * 100).toFixed(0)}%
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* DREAD Scoring Details */}
                {analysisResult.analysis.dread_suggestions && (
                  <div>
                    <p className="text-sm text-gray-400 mb-3 font-medium">DREAD Scoring Details</p>
                    <div className="bg-cyber-dark p-4 rounded-lg border border-gray-700/50">
                      <DREADScorer
                        suggestedScores={analysisResult.analysis.dread_suggestions.suggested_scores}
                        confidence={analysisResult.analysis.dread_suggestions.confidence}
                        explanations={analysisResult.analysis.dread_suggestions.explanations}
                        onScoresChange={setDreadScores}
                        autoScore={true}
                      />
                    </div>
                  </div>
                )}

                {/* Mitigation Recommendations */}
                <div>
                  <p className="text-sm text-gray-400 mb-3 font-medium flex items-center gap-2">
                    <LightBulbIcon className="w-5 h-5" />
                    Mitigation Recommendations
                  </p>
                  <div className="bg-cyber-dark p-4 rounded-lg border border-gray-700/50">
                    <MitigationList mitigation={analysisResult.analysis.mitigation} riskLevel={analysisResult.analysis.risk_level} />
                  </div>
                </div>

                {/* Enhanced Mitigations */}
                {analysisResult.analysis.enhanced_mitigations && (
                  <div>
                    <p className="text-sm text-gray-400 mb-3 font-medium">Enhanced Mitigations</p>
                    <div className="bg-cyber-dark p-4 rounded-lg border border-gray-700/50">
                      {analysisResult.analysis.enhanced_mitigations.mitigations?.map((mit, idx) => (
                        <div key={idx} className="mb-3 last:mb-0">
                          <div className="flex items-start gap-2">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              mit.priority >= 9 ? 'bg-red-500/20 text-red-300' :
                              mit.priority >= 7 ? 'bg-yellow-500/20 text-yellow-300' :
                              'bg-green-500/20 text-green-300'
                            }`}>
                              Priority {mit.priority}
                            </span>
                            <p className="text-sm text-gray-300 flex-1">{mit.text}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4 border-t border-gray-700/50">
                  <button
                    onClick={() => {
                      setShowResultModal(false);
                      setAnalysisResult(null); // Clear results when closing
                    }}
                    className="btn-primary flex-1"
                  >
                    Close
                  </button>
                  <button
                    onClick={() => {
                      setShowResultModal(false);
                      setViewMode('diagram');
                      if (analysisResult.threat) {
                        setSelectedThreatForDiagram(analysisResult.threat);
                      }
                    }}
                    className="btn-secondary flex-1 flex items-center justify-center gap-2"
                  >
                    <ChartBarIcon className="w-5 h-5" />
                    View Diagram
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Threats List */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">Previous Analyses</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1 rounded text-sm ${
                viewMode === 'list'
                  ? 'bg-cyber-blue text-white'
                  : 'bg-cyber-dark text-gray-400 hover:bg-gray-700'
              }`}
            >
              List
            </button>
            <button
              onClick={() => {
                setViewMode('diagram');
                if (threats.length > 0 && !selectedThreatForDiagram) {
                  setSelectedThreatForDiagram(threats[0]);
                }
              }}
              className={`px-3 py-1 rounded text-sm flex items-center gap-1 ${
                viewMode === 'diagram'
                  ? 'bg-cyber-blue text-white'
                  : 'bg-cyber-dark text-gray-400 hover:bg-gray-700'
              }`}
            >
              <ChartBarIcon className="w-4 h-4" />
              Diagram
            </button>
            <button
              onClick={() => setViewMode('matrix')}
              className={`px-3 py-1 rounded text-sm flex items-center gap-1 ${
                viewMode === 'matrix'
                  ? 'bg-cyber-blue text-white'
                  : 'bg-cyber-dark text-gray-400 hover:bg-gray-700'
              }`}
            >
              <Squares2X2Icon className="w-4 h-4" />
              Matrix
            </button>
          </div>
        </div>

        {viewMode === 'list' && (
          <div className="space-y-2">
            {threats.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No threats analyzed yet</p>
            ) : (
              threats.map((threat) => (
                <div
                  key={threat.id}
                  className="flex items-center justify-between p-4 bg-cyber-dark rounded-lg hover:bg-gray-800/50 cursor-pointer transition"
                  onClick={() => {
                    setSelectedThreatForDiagram(threat);
                    setViewMode('diagram');
                  }}
                >
                  <div>
                    <p className="font-medium text-white">{threat.asset}</p>
                    <p className="text-sm text-gray-400">{threat.flow.substring(0, 100)}...</p>
                  </div>
                  <div className={`px-4 py-2 rounded border ${getRiskColor(threat.risk_level)}`}>
                    {threat.risk_level}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {viewMode === 'diagram' && (
          <div className="space-y-4">
            {threats.length > 0 && (
              <>
                <div className="flex items-center gap-2 mb-4">
                  <label className="text-sm text-gray-400">Select Threat:</label>
                  <select
                    value={selectedThreatForDiagram?.id || ''}
                    onChange={(e) => {
                      const threat = threats.find(t => t.id === parseInt(e.target.value));
                      setSelectedThreatForDiagram(threat);
                    }}
                    className="input-field"
                  >
                    {threats.map(threat => (
                      <option key={threat.id} value={threat.id}>
                        {threat.asset} - {threat.risk_level}
                      </option>
                    ))}
                  </select>
                </div>
                <ThreatDiagram
                  threat={selectedThreatForDiagram}
                  onNodeClick={(event, node) => {
                    console.log('Node clicked:', node);
                  }}
                />
              </>
            )}
            {threats.length === 0 && (
              <p className="text-gray-400 text-center py-8">No threats available for diagram</p>
            )}
          </div>
        )}

        {viewMode === 'matrix' && (
          <ThreatMatrix threats={threats} />
        )}
      </motion.div>
    </div>
  );
};

export default ThreatModeling;

