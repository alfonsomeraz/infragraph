"use client";

interface PaginationProps {
  offset: number;
  limit: number;
  count: number;
  onPageChange: (newOffset: number) => void;
}

export default function Pagination({ offset, limit, count, onPageChange }: PaginationProps) {
  const page = Math.floor(offset / limit) + 1;
  const hasPrev = offset > 0;
  const hasNext = count === limit;

  return (
    <div className="flex items-center justify-between border-t border-gray-200 pt-4">
      <span className="text-sm text-gray-500">
        Showing {offset + 1}–{offset + count} results
      </span>
      <div className="flex gap-2">
        <button
          disabled={!hasPrev}
          onClick={() => onPageChange(Math.max(0, offset - limit))}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Previous
        </button>
        <span className="flex items-center px-2 text-sm text-gray-600">Page {page}</span>
        <button
          disabled={!hasNext}
          onClick={() => onPageChange(offset + limit)}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Next
        </button>
      </div>
    </div>
  );
}
