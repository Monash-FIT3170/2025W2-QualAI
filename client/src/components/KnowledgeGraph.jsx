import React, { useEffect, useRef } from "react";
import { DataSet, Network } from "vis-network/standalone";

export default function KnowledgeGraph() {
  const containerRef = useRef(null);

  useEffect(() => {
    // Dummy graph data
    const nodes = new DataSet([
      { id: 1, label: "Cats", value: 5 },
      { id: 2, label: "Dogs", value: 5 },
      { id: 3, label: "Animals", value: 10 },
    ]);

    const edges = new DataSet([
      { from: 1, to: 3 },
      { from: 2, to: 3 },
    ]);

    // Creating the network
    new Network(containerRef.current, { nodes, edges }, {
      physics: { enabled: true },
      nodes: { 
        shape: "circle", 
        size: 20,        
        font : {
            color: "#e2e8f0",
            strokeWidth: 0,
        },
        color: {
            border: "#4338ca",
            background: "#4f46e5",
            highlight: {
                background: "#5d87f0",
                border: "#4338ca" 
            }
        }
      },
      edges: { arrows: "to" },
      
    
    });
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        width: "100%",
        height: "400px",
        border: "1px solid #1e293b",
        borderRadius: "0.75rem",
        backgroundColor: "#1e293b"
    

      }}
    />
  );
}
