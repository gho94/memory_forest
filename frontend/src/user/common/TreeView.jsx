import React, { useState } from 'react';

const TreeView = ({ data, onNodeClick }) => {
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  const toggleNode = (nodeId) => {
    const newExpandedNodes = new Set(expandedNodes);
    if (newExpandedNodes.has(nodeId)) {
      newExpandedNodes.delete(nodeId);
    } else {
      newExpandedNodes.add(nodeId);
    }
    setExpandedNodes(newExpandedNodes);
  };

  const renderNode = (node, level = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.id);
    const indent = level * 20;

    return (
      <div key={node.id} className="tree-node">
        <div 
          className="tree-node-content"
          style={{ paddingLeft: `${indent}px` }}
          onClick={() => {
            if (hasChildren) {
              toggleNode(node.id);
            }
            if (onNodeClick) {
              onNodeClick(node);
            }
          }}
        >
          <div className="tree-node-toggle">
            {hasChildren && (
              <span className={`toggle-icon ${isExpanded ? 'expanded' : ''}`}>
                ▼
              </span>
            )}
            {!hasChildren && <span className="leaf-icon">●</span>}
          </div>
          <div className="tree-node-label">
            <span className="node-text">{node.label}</span>
          </div>
        </div>
        {hasChildren && isExpanded && (
          <div className="tree-children">
            {node.children.map(child => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="tree-view">
      {data.map(node => renderNode(node))}
    </div>
  );
};

export default TreeView; 