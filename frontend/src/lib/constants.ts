import type { FindingType, Severity } from "./types";

// Resource type → node color (Tailwind classes)
export const RESOURCE_COLORS: Record<string, string> = {
  aws_instance: "#3b82f6",       // blue
  aws_vpc: "#8b5cf6",            // violet
  aws_subnet: "#a78bfa",         // violet-light
  aws_security_group: "#ef4444", // red
  aws_iam_role: "#f59e0b",       // amber
  aws_iam_policy: "#fbbf24",     // amber-light
  aws_s3_bucket: "#10b981",      // emerald
  aws_rds_instance: "#06b6d4",   // cyan
  aws_lambda_function: "#f97316",// orange
  aws_lb: "#14b8a6",             // teal
  aws_route_table: "#6366f1",    // indigo
  aws_eip: "#ec4899",            // pink
  aws_nat_gateway: "#84cc16",    // lime
  aws_kms_key: "#eab308",        // yellow
};

export const DEFAULT_RESOURCE_COLOR = "#6b7280"; // gray

export function getResourceColor(resourceType: string): string {
  return RESOURCE_COLORS[resourceType] || DEFAULT_RESOURCE_COLOR;
}

// Severity → color
export const SEVERITY_COLORS: Record<Severity, string> = {
  info: "#6b7280",
  low: "#3b82f6",
  medium: "#f59e0b",
  high: "#ef4444",
  critical: "#dc2626",
};

export const SEVERITY_BG: Record<Severity, string> = {
  info: "bg-gray-100 text-gray-700",
  low: "bg-blue-100 text-blue-700",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-red-100 text-red-700",
  critical: "bg-red-200 text-red-900",
};

// Finding type → display label
export const FINDING_TYPE_LABELS: Record<FindingType, string> = {
  orphan: "Orphaned Resource",
  drift: "Configuration Drift",
  exposure: "Security Exposure",
  circular_dep: "Circular Dependency",
  critical_node: "Critical Node",
};

// Change action → badge color
export const CHANGE_ACTION_COLORS: Record<string, string> = {
  create: "bg-green-100 text-green-700",
  update: "bg-amber-100 text-amber-700",
  delete: "bg-red-100 text-red-700",
  "no-op": "bg-gray-100 text-gray-600",
  read: "bg-blue-100 text-blue-700",
};
