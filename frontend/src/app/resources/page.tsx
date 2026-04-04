"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { listResources } from "@/lib/api";
import type { ResourceOut } from "@/lib/types";
import Spinner from "@/components/ui/Spinner";
import EmptyState from "@/components/ui/EmptyState";
import Pagination from "@/components/ui/Pagination";
import Badge from "@/components/ui/Badge";
import { CHANGE_ACTION_COLORS } from "@/lib/constants";

const LIMIT = 25;

export default function ResourcesPage() {
  const router = useRouter();
  const [resources, setResources] = useState<ResourceOut[]>([]);
  const [count, setCount] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState("");
  const [providerFilter, setProviderFilter] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listResources({
        limit: LIMIT,
        offset,
        resource_type: typeFilter || undefined,
        provider: providerFilter || undefined,
      });
      setResources(data.resources);
      setCount(data.count);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load resources");
    } finally {
      setLoading(false);
    }
  }, [offset, typeFilter, providerFilter]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Resources</h1>
      <p className="mt-1 text-sm text-gray-500">All parsed cloud resources</p>

      <div className="mt-4 flex gap-3">
        <input
          type="text"
          placeholder="Filter by type (e.g. aws_instance)"
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setOffset(0);
          }}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
        />
        <input
          type="text"
          placeholder="Filter by provider"
          value={providerFilter}
          onChange={(e) => {
            setProviderFilter(e.target.value);
            setOffset(0);
          }}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
        />
      </div>

      {loading ? (
        <Spinner />
      ) : error ? (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      ) : resources.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="No resources found" />
        </div>
      ) : (
        <>
          <div className="mt-4 overflow-hidden rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Name
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    External ID
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Provider
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Source
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {resources.map((r) => (
                  <tr
                    key={r.id}
                    onClick={() => router.push(`/graph?resource_id=${r.id}`)}
                    className="cursor-pointer hover:bg-gray-50"
                  >
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">
                      {r.name || "-"}
                    </td>
                    <td className="max-w-[200px] truncate px-4 py-3 font-mono text-xs text-gray-600">
                      {r.external_id}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">
                      {r.resource_type}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">
                      {r.provider || "-"}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
                      {r.source}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      {r.change_action ? (
                        <Badge
                          label={r.change_action}
                          className={
                            CHANGE_ACTION_COLORS[r.change_action] || "bg-gray-100 text-gray-700"
                          }
                        />
                      ) : (
                        "-"
                      )}
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
