# InfraGraph — Frontend

Next.js 16 web application for InfraGraph. Provides an interactive graph canvas, resource browser, blast radius analysis, and findings dashboard.

## Stack

- **Next.js 16** (App Router, TypeScript strict)
- **React Flow v12** (`@xyflow/react`) — graph visualization
- **dagre** — automatic graph layout
- **Tailwind CSS v4** — styling

## Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard — summary stats + recent findings |
| `/upload` | Drag-and-drop Terraform JSON upload |
| `/resources` | Filterable, paginated resource browser |
| `/graph` | Interactive dependency graph for any resource |
| `/blast-radius` | BFS impact visualization with configurable depth |
| `/findings` | Findings list filtered by type and severity |

## Development

Requires the backend API running on `:8000` (see root README).

```bash
# Install deps
npm install

# Start dev server on :3000
npm run dev

# Production build
npm run build

# Lint
npm run lint
```

Or use the root Makefile targets:

```bash
make fe-install
make fe-dev
make fe-build
make fe-lint
```

## API integration

All API calls go through Next.js rewrites (`next.config.ts`):

```
/api/* → http://api:8000    (inside Docker)
/api/* → http://localhost:8000  (local dev)
```

This avoids CORS issues in development. The fetch wrapper lives in `src/lib/api.ts`.

## Project layout

```
src/
├── app/                  # Pages (Next.js App Router)
│   ├── page.tsx          # Dashboard
│   ├── upload/
│   ├── resources/
│   ├── graph/
│   ├── blast-radius/
│   └── findings/
├── components/
│   ├── AppShell.tsx      # Layout + sidebar navigation
│   ├── graph/            # React Flow canvas, nodes, edges
│   └── ui/               # Badge, Spinner, EmptyState, Pagination, DropZone, ResourcePicker
└── lib/
    ├── api.ts            # Typed fetch wrappers for every API endpoint
    ├── types.ts          # TypeScript types matching backend Pydantic schemas
    └── constants.ts      # Severity colors, labels, default limits
```
