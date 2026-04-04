import Link from "next/link";

interface EmptyStateProps {
  title: string;
  message?: string;
  showUploadLink?: boolean;
}

export default function EmptyState({
  title,
  message = "No data available yet.",
  showUploadLink = true,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 py-16 text-center">
      <p className="text-lg font-medium text-gray-900">{title}</p>
      <p className="mt-1 text-sm text-gray-500">{message}</p>
      {showUploadLink && (
        <Link
          href="/upload"
          className="mt-4 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          Upload Terraform Files
        </Link>
      )}
    </div>
  );
}
