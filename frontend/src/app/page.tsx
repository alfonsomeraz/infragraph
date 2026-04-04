"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listResources, listFindings } from "@/lib/api";
import type { FindingOut } from "@/lib/types";
import { SEVERITY_BG, FINDING_TYPE_LABELS } from "@/lib/constants";
import Badge from "@/components/ui/Badge";
import Spinner from "@/components/ui/Spinner";

export default function DashboardPage() {
  const [resourceCount, setResourceCount] = useState<number | null>(null);
  const [findingsCount, setFindingsCount] = useState<number | null>(null);
  const [recentFindings, setRecentFindings] = useState<FindingOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [resources, findings] = await Promise.all([
          listResources({ limit: 1 }),
          listFindings({ limit: 5 }),
        ]);
        setResourceCount(resources.count);
        setFindingsCount(findings.count);
        setRecentFindings(findings.findings);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Spinner />;

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p className="mt-1 text-sm text-gray-500">Overview of your infrastructure</p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Total Resources" value={resourceCount ?? 0} href="/resources" />
        <StatCard label="Total Findings" value={findingsCount ?? 0} href="/findings" />
        <StatCard label="Recent Findings" value={recentFindings.length} href="/findings" />
      </div>

      {recentFindings.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900">Recent Findings</h2>
          <div className="mt-3 overflow-hidden rounded-lg border border-gray-200">
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
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {recentFindings.map((f) => (
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
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({
  label,
  value,
  href,
}: {
  label: string;
  value: number;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="rounded-lg border border-gray-200 p-5 transition-shadow hover:shadow-md"
    >
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="mt-1 text-3xl font-bold text-gray-900">{value}</p>
    </Link>
  );
}
