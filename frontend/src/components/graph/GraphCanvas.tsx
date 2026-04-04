"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  MarkerType,
} from "@xyflow/react";
import dagre from "@dagrejs/dagre";
import "@xyflow/react/dist/style.css";

import type { GraphNodeOut, GraphEdgeOut } from "@/lib/types";
import { getResourceColor } from "@/lib/constants";
import GraphNode from "./GraphNode";
import GraphEdge from "./GraphEdge";

const NODE_WIDTH = 220;
const NODE_HEIGHT = 80;

const nodeTypes = { custom: GraphNode };
const edgeTypes = { custom: GraphEdge };

function layoutGraph(nodes: Node[], edges: Edge[]): Node[] {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: "TB", nodesep: 80, ranksep: 100 });

  for (const node of nodes) {
    g.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  }
  for (const edge of edges) {
    g.setEdge(edge.source, edge.target);
  }

  dagre.layout(g);

  return nodes.map((node) => {
    const pos = g.node(node.id);
    return {
      ...node,
      position: {
        x: pos.x - NODE_WIDTH / 2,
        y: pos.y - NODE_HEIGHT / 2,
      },
    };
  });
}

interface GraphCanvasProps {
  apiNodes: GraphNodeOut[];
  apiEdges: GraphEdgeOut[];
  rootResourceId?: string;
}

export default function GraphCanvas({ apiNodes, apiEdges, rootResourceId }: GraphCanvasProps) {
  const { initialNodes, initialEdges } = useMemo(() => {
    const rfNodes: Node[] = apiNodes.map((n) => ({
      id: n.id,
      type: "custom",
      position: { x: 0, y: 0 },
      data: {
        label: n.name || n.external_id,
        resourceType: n.resource_type,
        isRoot: n.id === rootResourceId,
        changeAction: n.change_action,
      },
    }));

    const rfEdges: Edge[] = apiEdges.map((e) => ({
      id: e.id,
      source: e.from_resource_id,
      target: e.to_resource_id,
      type: "custom",
      markerEnd: { type: MarkerType.ArrowClosed, color: "#94a3b8" },
      data: {
        relationshipType: e.relationship_type,
        confidence: e.confidence,
      },
    }));

    const laid = layoutGraph(rfNodes, rfEdges);
    return { initialNodes: laid, initialEdges: rfEdges };
  }, [apiNodes, apiEdges, rootResourceId]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const miniMapColor = useCallback(
    (node: Node) => getResourceColor((node.data as Record<string, string>).resourceType),
    [],
  );

  return (
    <div className="h-[600px] w-full rounded-lg border border-gray-200">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
      >
        <Controls />
        <Background gap={16} size={1} />
        <MiniMap nodeColor={miniMapColor} pannable zoomable />
      </ReactFlow>
    </div>
  );
}
