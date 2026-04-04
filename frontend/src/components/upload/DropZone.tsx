"use client";

import { useState, useRef, type DragEvent } from "react";

interface DropZoneProps {
  onFileDrop: (file: File) => void;
  disabled?: boolean;
}

export default function DropZone({ onFileDrop, disabled }: DropZoneProps) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    setDragging(true);
  }

  function handleDragLeave() {
    setDragging(false);
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith(".json")) {
      onFileDrop(file);
    }
  }

  function handleFileSelect() {
    const file = inputRef.current?.files?.[0];
    if (file) onFileDrop(file);
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-16 transition-colors ${
        disabled
          ? "cursor-not-allowed border-gray-200 bg-gray-50"
          : dragging
            ? "border-gray-900 bg-gray-50"
            : "border-gray-300 hover:border-gray-400"
      }`}
    >
      <span className="text-3xl text-gray-400">↑</span>
      <p className="mt-2 text-sm font-medium text-gray-700">
        Drop a Terraform JSON file here, or click to browse
      </p>
      <p className="mt-1 text-xs text-gray-500">Supports plan and state JSON files</p>
      <input
        ref={inputRef}
        type="file"
        accept=".json"
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled}
      />
    </div>
  );
}
