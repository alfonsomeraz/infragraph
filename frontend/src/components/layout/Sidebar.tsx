"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "◈" },
  { href: "/resources", label: "Resources", icon: "☰" },
  { href: "/graph", label: "Graph Explorer", icon: "◉" },
  { href: "/blast-radius", label: "Blast Radius", icon: "◎" },
  { href: "/findings", label: "Findings", icon: "⚠" },
  { href: "/upload", label: "Upload", icon: "↑" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-56 shrink-0 flex-col border-r border-gray-200 bg-gray-50">
      <div className="flex h-14 items-center gap-2 border-b border-gray-200 px-4">
        <span className="text-lg font-bold text-gray-900">InfraGraph</span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-3">
        {NAV_ITEMS.map(({ href, label, icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? "bg-gray-900 text-white"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              }`}
            >
              <span className="text-base">{icon}</span>
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
