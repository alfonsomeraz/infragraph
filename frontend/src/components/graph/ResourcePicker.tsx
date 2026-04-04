"use client";

import { useState, useEffect, useRef } from "react";
import { listResources } from "@/lib/api";
import type { ResourceOut } from "@/lib/types";

interface ResourcePickerProps {
  onSelect: (resourceId: string) => void;
  selectedId?: string;
}

export default function ResourcePicker({ onSelect, selectedId }: ResourcePickerProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ResourceOut[]>([]);
  const [allResources, setAllResources] = useState<ResourceOut[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Load all resources on mount for initial dropdown
  useEffect(() => {
    const loadAllResources = async () => {
      try {
        const data = await listResources({ limit: 100 });
        setAllResources(data.resources);
      } catch {
        setAllResources([]);
      }
    };
    loadAllResources();
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      // Show all resources when empty
      setResults(allResources);
      return;
    }

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await listResources({ limit: 50 });
        const filtered = data.resources.filter(
          (r) =>
            r.name?.toLowerCase().includes(query.toLowerCase()) ||
            r.external_id.toLowerCase().includes(query.toLowerCase()) ||
            r.resource_type.toLowerCase().includes(query.toLowerCase()),
        );
        setResults(filtered);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
  }, [query, allResources]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as HTMLElement)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className="relative w-full max-w-md">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 100)}
        placeholder="Search resources by name, ID, or type..."
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
      />
      {loading && (
        <div className="absolute right-3 top-2.5">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600" />
        </div>
      )}
      {selectedId && (
        <p className="mt-1 text-xs text-gray-500">
          Selected: <span className="font-mono">{selectedId.slice(0, 8)}...</span>
        </p>
      )}
      {open && (
        <div className="absolute z-10 mt-1 w-full max-h-60 overflow-auto rounded-md border border-gray-200 bg-white shadow-lg">
          {results.length > 0 ? (
            <ul>
              {results.map((r) => (
                <li key={r.id}>
                  <button
                    type="button"
                    className="flex w-full flex-col gap-0.5 px-3 py-2 text-left hover:bg-gray-50"
                    onClick={() => {
                      onSelect(r.id);
                      setQuery(r.name || r.external_id);
                      setOpen(false);
                    }}
                  >
                    <span className="text-sm font-medium text-gray-900">
                      {r.name || r.external_id}
                    </span>
                    <span className="text-xs text-gray-500">
                      {r.resource_type} &middot; {r.external_id}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-3 py-4 text-center text-sm text-gray-500">
              {allResources.length === 0 ? (
                <>No resources found. Upload a Terraform file first.</>
              ) : (
                <>No matches for "{query}"</>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
