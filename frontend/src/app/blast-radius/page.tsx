"use client";

import { Suspense, useState, useCallback, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { getBlastRadius } from "@/lib/api";
import type { BlastRadiusOut } from "@/lib/types";
import ResourcePicker from "@/components/graph/ResourcePicker";
import GraphCanvas from "@/components/graph/GraphCanvas";
import Spinner from "@/components/ui/Spinner";
import EmptyState from "@/components/ui/EmptyState";

function BlastRadiusContent() {
  const searchParams = useSearchParams();
  const initialId = searchParams.get("resource_id") || "";

  const [resourceId, setResourceId] = useState(initialId);
  const [depth, setDepth] = useState(3);
  const [data, setData] = useState<BlastRadiusOut | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadBlastRadius = useCallback(async (id: string, d: number) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const result = await getBlastRadius(id, d);
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load blast radius");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBlastRadius(resourceId, depth);
  }, [resourceId, depth, loadBlastRadius]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Blast Radius</h1>
      <p className="mt-1 text-sm text-gray-500">
        See what resources are affected by changes
      </p>

      <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-end">
        <ResourcePicker onSelect={setResourceId} selectedId={resourceId} />
        <div className="flex items-center gap-3">
          <label htmlFor="depth" className="text-sm font-medium text-gray-700">
            Depth: {depth}
          </label>
          <input
            id="depth"
            type="range"
            min={1}
            max={10}
            value={depth}
            onChange={(e) => setDepth(Number(e.target.value))}
            className="w-32"
          />
        </div>
      </div>

      <div className="mt-6">
        {loading ? (
          <Spinner />
        ) : error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        ) : data && data.nodes.length > 0 ? (
          <>
            <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
              <strong>{data.impact_count}</strong> resource(s) affected within depth{" "}
              <strong>{data.depth}</strong>
            </div>
            <GraphCanvas
              apiNodes={data.nodes}
              apiEdges={data.edges}
              rootResourceId={data.root_resource_id}
            />
          </>
        ) : resourceId ? (
          <EmptyState
            title="No blast radius data"
            message="This resource has no downstream dependencies."
            showUploadLink={false}
          />
        ) : (
          <EmptyState
            title="Select a resource"
            message="Search and select a resource to see its blast radius."
            showUploadLink={false}
          />
        )}
      </div>
    </div>
  );
}

export default function BlastRadiusPage() {
  return (
    <Suspense fallback={<Spinner />}>
      <BlastRadiusContent />
    </Suspense>
  );
}
