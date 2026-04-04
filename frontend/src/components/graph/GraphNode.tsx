"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { getResourceColor, CHANGE_ACTION_COLORS } from "@/lib/constants";
import Badge from "@/components/ui/Badge";

export interface GraphNodeData {
  label: string;
  resourceType: string;
  isRoot: boolean;
  changeAction: string | null;
  [key: string]: unknown;
}

export default function GraphNode({ data }: NodeProps) {
  const nodeData = data as unknown as GraphNodeData;
  const color = getResourceColor(nodeData.resourceType);

  return (
    <div
      className={`rounded-lg border-2 bg-white px-3 py-2 shadow-sm ${
        nodeData.isRoot ? "ring-2 ring-offset-1" : ""
      }`}
      style={{
        borderColor: color,
        ...(nodeData.isRoot ? { ringColor: color } : {}),
      }}
    >
      <Handle type="target" position={Position.Top} className="!bg-gray-400" />
      <div className="flex flex-col gap-1">
        <span className="text-xs font-medium text-gray-500">{nodeData.resourceType}</span>
        <span className="max-w-[180px] truncate text-sm font-semibold text-gray-900">
          {nodeData.label}
        </span>
        {nodeData.changeAction && nodeData.changeAction !== "no-op" && (
          <Badge
            label={nodeData.changeAction}
            className={CHANGE_ACTION_COLORS[nodeData.changeAction] || "bg-gray-100 text-gray-700"}
          />
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-gray-400" />
    </div>
  );
}
