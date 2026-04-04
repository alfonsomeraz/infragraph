"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { listFindings, scanFindings } from "@/lib/api";
import type { FindingOut, FindingType, Severity } from "@/lib/types";
import { SEVERITY_BG, FINDING_TYPE_LABELS } from "@/lib/constants";
import Badge from "@/components/ui/Badge";
import Spinner from "@/components/ui/Spinner";
import EmptyState from "@/components/ui/EmptyState";
import Pagination from "@/components/ui/Pagination";

const LIMIT = 25;

const FINDING_TYPES: FindingType[] = [
  "orphan",
  "drift",
  "exposure",
  "circular_dep",
  "critical_node",
];
const SEVERITIES: Severity[] = ["info", "low", "medium", "high", "critical"];

export default function FindingsPage() {
  const [findings, setFindings] = useState<FindingOut[]>([]);
  const [count, setCount] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [scanning, setScanning] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listFindings({
        limit: LIMIT,
        offset,
        finding_type: typeFilter || undefined,
        severity: severityFilter || undefined,
      });
      setFindings(data.findings);
      setCount(data.count);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load findings");
    } finally {
      setLoading(false);
    }
  }, [offset, typeFilter, severityFilter]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleScan() {
    setScanning(true);
    try {
      await scanFindings();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scan failed");
    } finally {
      setScanning(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Findings</h1>
          <p className="mt-1 text-sm text-gray-500">Detected issues and recommendations</p>
        </div>
        <button
          onClick={handleScan}
          disabled={scanning}
          className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
        >
          {scanning ? "Scanning..." : "Run Scan"}
        </button>
      </div>

      <div className="mt-4 flex gap-3">
        <select
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setOffset(0);
          }}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
        >
          <option value="">All types</option>
          {FINDING_TYPES.map((t) => (
            <option key={t} value={t}>
              {FINDING_TYPE_LABELS[t]}
            </option>
          ))}
        </select>
        <select
          value={severityFilter}
          onChange={(e) => {
            setSeverityFilter(e.target.value);
            setOffset(0);
          }}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
        >
          <option value="">All severities</option>
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <Spinner />
      ) : error ? (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      ) : findings.length === 0 ? (
        <div className="mt-6">
          <EmptyState
            title="No findings"
            message="Run a scan to detect issues in your infrastructure."
            showUploadLink={false}
          />
        </div>
      ) : (
        <>
          <div className="mt-4 overflow-hidden rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Severity
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Message
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Resource
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {findings.map((f) => (
                  <tr key={f.id}>
                    <td className="whitespace-nowrap px-4 py-3">
                      <Badge label={f.severity} className={SEVERITY_BG[f.severity]} />
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">
                      {FINDING_TYPE_LABELS[f.finding_type] || f.finding_type}
                    </td>
                    <td className="max-w-md truncate px-4 py-3 text-sm text-gray-600">
                      {f.message}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <Link
                        href={`/graph?resource_id=${f.resource_id}`}
                        className="font-mono text-xs text-blue-600 hover:underline"
                      >
                        {f.resource_id.slice(0, 8)}...
                      </Link>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-xs text-gray-500">
                      {new Date(f.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4">
            <Pagination
              offset={offset}
              limit={LIMIT}
              count={count}
              onPageChange={setOffset}
            />
          </div>
        </>
      )}
    </div>
  );
}
