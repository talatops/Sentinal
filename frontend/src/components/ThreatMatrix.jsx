import { useMemo } from 'react';
// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion';

const ThreatMatrix = ({ threats }) => {
  const matrixData = useMemo(() => {
    if (!threats || threats.length === 0) return { assets: [], strideCategories: [], data: {} };

    // Extract unique assets and STRIDE categories
    const assets = [...new Set(threats.map(t => t.asset))];
    const strideCategories = ['Spoofing', 'Tampering', 'Repudiation', 'Information Disclosure', 'Denial of Service', 'Elevation of Privilege'];

    // Build matrix data
    const data = {};
    assets.forEach(asset => {
      data[asset] = {};
      strideCategories.forEach(category => {
        data[asset][category] = 0;
      });
    });

    // Count threats per asset-stride combination
    threats.forEach(threat => {
      const asset = threat.asset;
      const categories = threat.stride_categories || [];
      categories.forEach(category => {
        if (data[asset] && data[asset][category] !== undefined) {
          data[asset][category]++;
        }
      });
    });

    return { assets, strideCategories, data };
  }, [threats]);

  const getHeatColor = (count, maxCount) => {
    if (count === 0) return 'bg-gray-800';
    const intensity = maxCount > 0 ? count / maxCount : 0;
    if (intensity > 0.7) return 'bg-red-600';
    if (intensity > 0.4) return 'bg-orange-500';
    if (intensity > 0.2) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const maxCount = useMemo(() => {
    let max = 0;
    Object.values(matrixData.data).forEach(assetData => {
      Object.values(assetData).forEach(count => {
        if (count > max) max = count;
      });
    });
    return max;
  }, [matrixData.data]);

  if (!threats || threats.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-cyber-dark rounded-lg border border-gray-700">
        <p className="text-gray-400">No threats available for matrix</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="card overflow-x-auto"
    >
      <h3 className="text-lg font-bold text-white mb-4">STRIDE vs Asset Heatmap</h3>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="sticky left-0 bg-cyber-dark border border-gray-700 px-4 py-2 text-left text-sm font-medium text-gray-300 z-10">
                Asset
              </th>
              {matrixData.strideCategories.map(category => (
                <th
                  key={category}
                  className="border border-gray-700 px-4 py-2 text-center text-xs font-medium text-gray-300 min-w-[120px]"
                >
                  {category}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrixData.assets.map((asset, assetIndex) => (
              <motion.tr
                key={asset}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: assetIndex * 0.05 }}
                className="hover:bg-gray-800/50"
              >
                <td className="sticky left-0 bg-cyber-dark border border-gray-700 px-4 py-2 text-sm text-white font-medium z-10">
                  {asset}
                </td>
                {matrixData.strideCategories.map(category => {
                  const count = matrixData.data[asset]?.[category] || 0;
                  return (
                    <td
                      key={category}
                      className={`border border-gray-700 px-4 py-2 text-center ${getHeatColor(count, maxCount)} text-white font-bold`}
                      title={`${count} threat(s) for ${asset} - ${category}`}
                    >
                      {count > 0 ? count : '-'}
                    </td>
                  );
                })}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-4 flex items-center gap-4 text-xs text-gray-400">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-800 border border-gray-700"></div>
          <span>0 threats</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500"></div>
          <span>Low (1-2)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-500"></div>
          <span>Medium (3-5)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-orange-500"></div>
          <span>High (6-8)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-600"></div>
          <span>Critical (9+)</span>
        </div>
      </div>
    </motion.div>
  );
};

export default ThreatMatrix;

