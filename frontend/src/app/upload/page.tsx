"use client";

import { useState } from "react";
import { uploadFile, scanFindings } from "@/lib/api";
import type { IngestionRunOut } from "@/lib/types";
import DropZone from "@/components/upload/DropZone";

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [run, setRun] = useState<IngestionRunOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<string | null>(null);

  async function handleFile(file: File) {
    setUploading(true);
    setError(null);
    setRun(null);
    setScanResult(null);
    try {
      const result = await uploadFile(file);
      setRun(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleScan() {
    setScanning(true);
    setScanResult(null);
    try {
      const result = await scanFindings();
      setScanResult(`Scan complete: ${result.count} finding(s) detected.`);
    } catch (e) {
      setScanResult(e instanceof Error ? e.message : "Scan failed");
    } finally {
      setScanning(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Upload</h1>
      <p className="mt-1 text-sm text-gray-500">
        Upload Terraform plan or state JSON files to parse
      </p>

      <div className="mt-6">
        <DropZone onFileDrop={handleFile} disabled={uploading} />
      </div>

      {uploading && (
        <p className="mt-4 text-sm text-gray-600">Uploading and parsing...</p>
      )}

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {run && (
        <div className="mt-4 rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="font-medium text-green-800">Upload successful</p>
          <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-green-700">
            <dt className="font-medium">File</dt>
            <dd>{run.file_name}</dd>
            <dt className="font-medium">Status</dt>
            <dd>{run.status}</dd>
            <dt className="font-medium">Resources</dt>
            <dd>{run.resource_count}</dd>
            <dt className="font-medium">Relationships</dt>
            <dd>{run.relationship_count}</dd>
            <dt className="font-medium">Source Type</dt>
            <dd>{run.source_type}</dd>
          </dl>
          <button
            onClick={handleScan}
            disabled={scanning}
            className="mt-4 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
          >
            {scanning ? "Scanning..." : "Scan for Findings"}
          </button>
          {scanResult && (
            <p className="mt-2 text-sm text-gray-700">{scanResult}</p>
          )}
        </div>
      )}
    </div>
  );
}
