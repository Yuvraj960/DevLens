# Frontend Application Architecture (docs/frontend.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

The DevLens frontend is built with **Next.js 14 (React 18)** using the **App Router**, **Tailwind CSS**, **Zustand**, and **TanStack Query**.

```
frontend/
├── src/
│   ├── app/             # App Router pages and layouts
│   │   ├── layout.tsx   # Root Layout & Global Theme Providers
│   │   ├── page.tsx     # Landing Page & Ingestion Form
│   │   └── repos/[id]/  # Repository Dashboard
│   ├── components/      # Reusable React UI Components
│   │   ├── ui/          # Core primitives (Button, Card, Badge, Progress)
│   │   ├── ingestion/   # Form, Progress Tracker, Uploaders
│   │   └── repository/  # File Tree Browser, Code Viewer
│   ├── hooks/           # Custom React Hooks
│   ├── lib/             # API Client & Utility Functions
│   └── types/           # TypeScript Types (Generated from OpenAPI)
├── biome.json           # Biome Linter & Formatter Config
└── tsconfig.json        # TypeScript Strict Configuration
```

---

## Key Features & Components

### 1. Ingestion Flow Component (`src/components/ingestion/`)
- Accepts GitHub URL, ZIP file upload, or local folder path.
- Connects to backend `/ws/jobs/{job_id}` WebSocket to display real-time stage progress (`QUEUED` -> `CLONING` -> `WALKING` -> `COMPLETE`).

### 2. Repo Dashboard (`src/app/repos/[id]/page.tsx`)
- Tabbed interface navigation (Summary, Architecture, File Tree, Chat, Search, API, DB).
- Interactive File Tree component for browsing repository directories and inspecting individual file details.

---

## Quick Node Connections
- Backend Endpoints: [Backend Architecture](backend.md)
- API Integration Specs: [API Contracts](api.md)
