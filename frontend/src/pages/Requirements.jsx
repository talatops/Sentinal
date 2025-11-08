import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { requirementService } from '../services/requirementService';
import { useAuthStore } from '../store/authStore';
import { z } from 'zod';

const requirementSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  security_controls: z.array(z.object({
    name: z.string().min(1, 'Control name is required'),
    description: z.string().optional(),
    owasp_asvs_level: z.string().optional(),
  })).min(1, 'At least one security control is required'),
  status: z.enum(['Draft', 'Review', 'Approved', 'Implemented']).optional(),
  owasp_asvs_level: z.string().optional(),
});

const Requirements = () => {
  const { user } = useAuthStore();
  const [requirements, setRequirements] = useState([]);
  const [compliance, setCompliance] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    security_controls: [{ name: '', description: '', owasp_asvs_level: '' }],
    status: 'Draft',
    owasp_asvs_level: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadRequirements();
    if (user?.role === 'Admin') {
      loadCompliance();
    }
  }, [user]);

  const loadRequirements = async () => {
    try {
      const data = await requirementService.getRequirements();
      setRequirements(data.requirements || []);
    } catch (error) {
      console.error('Failed to load requirements:', error);
    }
  };

  const loadCompliance = async () => {
    try {
      const data = await requirementService.getCompliance();
      setCompliance(data);
    } catch (error) {
      console.error('Failed to load compliance:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    try {
      const validated = requirementSchema.parse(formData);
      await requirementService.createRequirement(validated);
      await loadRequirements();
      setShowForm(false);
      setFormData({
        title: '',
        description: '',
        security_controls: [{ name: '', description: '', owasp_asvs_level: '' }],
        status: 'Draft',
        owasp_asvs_level: '',
      });
    } catch (error) {
      if (error.errors) {
        const zodErrors = {};
        error.errors.forEach((err) => {
          zodErrors[err.path[0]] = err.message;
        });
        setErrors(zodErrors);
      } else {
        setErrors({ submit: 'Failed to create requirement' });
      }
    } finally {
      setLoading(false);
    }
  };

  const addSecurityControl = () => {
    setFormData((prev) => ({
      ...prev,
      security_controls: [...prev.security_controls, { name: '', description: '', owasp_asvs_level: '' }],
    }));
  };

  const removeSecurityControl = (index) => {
    setFormData((prev) => ({
      ...prev,
      security_controls: prev.security_controls.filter((_, i) => i !== index),
    }));
  };

  const updateSecurityControl = (index, field, value) => {
    setFormData((prev) => {
      const controls = [...prev.security_controls];
      controls[index] = { ...controls[index], [field]: value };
      return { ...prev, security_controls: controls };
    });
  };

  const handleExport = async (format) => {
    try {
      const data = await requirementService.exportRequirements(format);
      if (format === 'csv') {
        const blob = new Blob([data.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'requirements.csv';
        a.click();
      } else {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'requirements.json';
        a.click();
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Requirements Management</h1>
          <p className="text-gray-400">Manage requirements with security controls</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleExport('json')}
            className="px-4 py-2 bg-cyber-dark border border-cyber-blue/20 rounded-lg hover:border-cyber-blue transition-colors"
          >
            Export JSON
          </button>
          <button
            onClick={() => handleExport('csv')}
            className="px-4 py-2 bg-cyber-dark border border-cyber-blue/20 rounded-lg hover:border-cyber-blue transition-colors"
          >
            Export CSV
          </button>
          <button onClick={() => setShowForm(!showForm)} className="btn-primary">
            {showForm ? 'Cancel' : 'New Requirement'}
          </button>
        </div>
      </motion.div>

      {/* Compliance Dashboard (Admin only) */}
      {compliance && user?.role === 'Admin' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Compliance Dashboard</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-400">Total Requirements</p>
              <p className="text-2xl font-bold text-white">{compliance.total_requirements}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">With Controls</p>
              <p className="text-2xl font-bold text-white">{compliance.requirements_with_controls}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Compliance Rate</p>
              <p className="text-2xl font-bold text-cyber-green">{compliance.compliance_rate}%</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Create Form */}
      {showForm && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <h2 className="text-xl font-bold text-white mb-4">Create Requirement</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                className="input-field w-full"
              />
              {errors.title && <p className="text-red-400 text-sm mt-1">{errors.title}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                className="input-field w-full h-24"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">OWASP ASVS Level</label>
              <select
                value={formData.owasp_asvs_level}
                onChange={(e) => setFormData((prev) => ({ ...prev, owasp_asvs_level: e.target.value }))}
                className="input-field w-full"
              >
                <option value="">Select Level</option>
                <option value="Level 1">Level 1</option>
                <option value="Level 2">Level 2</option>
                <option value="Level 3">Level 3</option>
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium">Security Controls</label>
                <button
                  type="button"
                  onClick={addSecurityControl}
                  className="text-sm text-cyber-blue hover:text-cyber-blue/80"
                >
                  + Add Control
                </button>
              </div>
              {formData.security_controls.map((control, index) => (
                <div key={index} className="mb-4 p-4 bg-cyber-dark rounded-lg">
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-400">Control {index + 1}</span>
                    {formData.security_controls.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeSecurityControl(index)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <input
                    type="text"
                    value={control.name}
                    onChange={(e) => updateSecurityControl(index, 'name', e.target.value)}
                    placeholder="Control name"
                    className="input-field w-full mb-2"
                  />
                  <textarea
                    value={control.description}
                    onChange={(e) => updateSecurityControl(index, 'description', e.target.value)}
                    placeholder="Description"
                    className="input-field w-full mb-2"
                  />
                  <select
                    value={control.owasp_asvs_level}
                    onChange={(e) => updateSecurityControl(index, 'owasp_asvs_level', e.target.value)}
                    className="input-field w-full"
                  >
                    <option value="">Select ASVS Level</option>
                    <option value="Level 1">Level 1</option>
                    <option value="Level 2">Level 2</option>
                    <option value="Level 3">Level 3</option>
                  </select>
                </div>
              ))}
              {errors.security_controls && (
                <p className="text-red-400 text-sm mt-1">{errors.security_controls}</p>
              )}
            </div>

            {errors.submit && (
              <div className="bg-red-500/20 border border-red-500 text-red-400 px-4 py-2 rounded">
                {errors.submit}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Creating...' : 'Create Requirement'}
            </button>
          </form>
        </motion.div>
      )}

      {/* Requirements List */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <h2 className="text-xl font-bold text-white mb-4">Requirements</h2>
        <div className="space-y-2">
          {requirements.length === 0 ? (
            <p className="text-gray-400 text-center py-8">No requirements yet</p>
          ) : (
            requirements.map((req) => (
              <div
                key={req.id}
                className="p-4 bg-cyber-dark rounded-lg hover:bg-cyber-dark/80 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-white mb-1">{req.title}</h3>
                    <p className="text-sm text-gray-400 mb-2">{req.description}</p>
                    <div className="flex gap-2 flex-wrap">
                      <span className="px-2 py-1 bg-cyber-blue/20 text-cyber-blue rounded text-xs">
                        {req.status}
                      </span>
                      {req.owasp_asvs_level && (
                        <span className="px-2 py-1 bg-cyber-green/20 text-cyber-green rounded text-xs">
                          {req.owasp_asvs_level}
                        </span>
                      )}
                      <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded text-xs">
                        {req.controls?.length || 0} Controls
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default Requirements;

