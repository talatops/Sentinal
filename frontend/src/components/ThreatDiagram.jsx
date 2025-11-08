import { useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';

const ThreatDiagram = ({ threat, onNodeClick }) => {
  const { nodes, edges } = useMemo(() => {
    if (!threat) return { nodes: [], edges: [] };

    const nodes = [];
    const edges = [];
    let nodeId = 1;

    // Parse flow description to extract components
    const flow = threat.flow.toLowerCase();
    const asset = threat.asset;

    // Extract components from flow
    const components = [];
    
    // Common component patterns
    if (flow.includes('user') || flow.includes('client')) {
      components.push({ type: 'user', name: 'User', icon: '👤' });
    }
    if (flow.includes('api') || flow.includes('endpoint')) {
      components.push({ type: 'api', name: 'API', icon: '🔌' });
    }
    if (flow.includes('database') || flow.includes('db') || flow.includes('postgres') || flow.includes('mysql')) {
      components.push({ type: 'database', name: 'Database', icon: '🗄️' });
    }
    if (flow.includes('auth') || flow.includes('login') || flow.includes('authentication')) {
      components.push({ type: 'auth', name: 'Auth Service', icon: '🔐' });
    }
    if (flow.includes('frontend') || flow.includes('ui') || flow.includes('web')) {
      components.push({ type: 'frontend', name: 'Frontend', icon: '💻' });
    }
    if (flow.includes('backend') || flow.includes('server')) {
      components.push({ type: 'backend', name: 'Backend', icon: '⚙️' });
    }

    // If no components detected, create default ones
    if (components.length === 0) {
      components.push(
        { type: 'user', name: 'User', icon: '👤' },
        { type: 'api', name: 'API Service', icon: '🔌' },
        { type: 'database', name: 'Data Store', icon: '🗄️' }
      );
    }

    // Create nodes
    const nodePositions = {
      user: { x: 100, y: 200 },
      frontend: { x: 300, y: 200 },
      api: { x: 500, y: 200 },
      backend: { x: 500, y: 100 },
      auth: { x: 500, y: 300 },
      database: { x: 700, y: 200 },
    };

    components.forEach((comp, index) => {
      const position = nodePositions[comp.type] || { x: 300 + index * 200, y: 200 };
      
      // Determine node style based on risk level
      const riskColor = threat.risk_level === 'High' ? '#ef4444' : 
                       threat.risk_level === 'Medium' ? '#f59e0b' : '#10b981';
      
      nodes.push({
        id: `node-${nodeId++}`,
        type: 'default',
        position,
        data: {
          label: (
            <div className="text-center">
              <div className="text-2xl mb-1">{comp.icon}</div>
              <div className="text-sm font-medium">{comp.name}</div>
            </div>
          ),
        },
        style: {
          background: '#1f2937',
          border: `2px solid ${riskColor}`,
          borderRadius: '8px',
          color: '#fff',
          width: 120,
          height: 100,
          padding: '10px',
        },
      });
    });

    // Create edges (connections between components)
    for (let i = 0; i < nodes.length - 1; i++) {
      const strideCategories = threat.stride_categories || [];
      const edgeColor = threat.risk_level === 'High' ? '#ef4444' : 
                       threat.risk_level === 'Medium' ? '#f59e0b' : '#10b981';
      
      edges.push({
        id: `edge-${i}`,
        source: nodes[i].id,
        target: nodes[i + 1].id,
        label: (
          <div className="px-2 py-1 bg-gray-800 rounded text-xs">
            {strideCategories.slice(0, 2).join(', ')}
          </div>
        ),
        style: { stroke: edgeColor, strokeWidth: 2 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: edgeColor,
        },
        labelStyle: { fill: '#fff', fontWeight: 600 },
        labelBgStyle: { fill: '#1f2937', fillOpacity: 0.8 },
      });
    }

    // Add trust boundary if specified
    if (threat.trust_boundary) {
      nodes.push({
        id: 'trust-boundary',
        type: 'default',
        position: { x: 250, y: 150 },
        data: {
          label: (
            <div className="text-center">
              <div className="text-xs text-yellow-400">Trust Boundary</div>
              <div className="text-xs">{threat.trust_boundary}</div>
            </div>
          ),
        },
        style: {
          background: 'transparent',
          border: '2px dashed #f59e0b',
          borderRadius: '8px',
          width: 400,
          height: 200,
          position: 'absolute',
        },
        draggable: false,
        selectable: false,
      });
    }

    return { nodes, edges };
  }, [threat]);

  if (!threat) {
    return (
      <div className="flex items-center justify-center h-96 bg-cyber-dark rounded-lg border border-gray-700">
        <p className="text-gray-400">Select a threat to view its data flow diagram</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full h-96 bg-cyber-dark rounded-lg border border-gray-700"
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        attributionPosition="bottom-left"
        onNodeClick={onNodeClick}
      >
        <Background color="#374151" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.id === 'trust-boundary') return '#f59e0b';
            return threat.risk_level === 'High' ? '#ef4444' : 
                   threat.risk_level === 'Medium' ? '#f59e0b' : '#10b981';
          }}
          maskColor="rgba(0, 0, 0, 0.6)"
        />
      </ReactFlow>
    </motion.div>
  );
};

export default ThreatDiagram;

