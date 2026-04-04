"use client";

import { Suspense, useState, useCallback, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { getGraph } from "@/lib/api";
import type { GraphOut } from "@/lib/types";
import ResourcePicker from "@/components/graph/ResourcePicker";
import GraphCanvas from "@/components/graph/GraphCanvas";
import Spinner from "@/components/ui/Spinner";
import EmptyState from "@/components/ui/EmptyState";

function GraphPageContent() {
  const searchParams = useSearchParams();
  const initialId = searchParams.get("resource_id") || "";

  const [resourceId, setResourceId] = useState(initialId);
  const [graph, setGraph] = useState<GraphOut | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadGraph = useCallback(async (id: string) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getGraph(id);
      setGraph(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load graph");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadGraph(resourceId);
  }, [resourceId, loadGraph]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Graph Explorer</h1>
      <p className="mt-1 text-sm text-gray-500">
        Visualize resource dependencies
      </p>

      <div className="mt-4">
        <ResourcePicker onSelect={setResourceId} selectedId={resourceId} />
      </div>

      <div className="mt-6">
        {loading ? (
          <Spinner />
        ) : error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        ) : graph && graph.nodes.length > 0 ? (
          <GraphCanvas apiNodes={graph.nodes} apiEdges={graph.edges} />
        ) : resourceId ? (
          <EmptyState
            title="No graph data"
            message="This resource has no relationships."
            showUploadLink={false}
          />
        ) : (
          <EmptyState
            title="Select a resource"
            message="Search and select a resource to see its dependency graph."
            showUploadLink={false}
          />
        )}
      </div>
    </div>
  );
}

export default function GraphPage() {
  return (
    <Suspense fallback={<Spinner />}>
      <GraphPageContent />
    </Suspense>
  );
}
