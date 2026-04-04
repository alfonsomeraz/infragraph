"use client";

import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  type EdgeProps,
} from "@xyflow/react";

export default function GraphEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  markerEnd,
}: EdgeProps) {
  const confidence = (data?.confidence as number) ?? 1;
  const relationshipType = (data?.relationshipType as string) ?? "";

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          opacity: confidence < 0.8 ? 0.5 : 0.8,
          strokeDasharray: confidence < 0.8 ? "5 5" : undefined,
          stroke: "#94a3b8",
          strokeWidth: 1.5,
        }}
      />
      {relationshipType && (
        <EdgeLabelRenderer>
          <div
            className="pointer-events-none absolute rounded bg-white px-1 py-0.5 text-[10px] text-gray-500"
            style={{
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            }}
          >
            {relationshipType.replace(/_/g, " ")}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
