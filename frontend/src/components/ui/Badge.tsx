interface BadgeProps {
  label: string;
  className?: string;
}

export default function Badge({ label, className = "bg-gray-100 text-gray-700" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${className}`}
    >
      {label}
    </span>
  );
}
