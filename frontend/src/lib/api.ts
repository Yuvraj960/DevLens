import type {
  IngestRequest,
  IngestResponse,
  JobResponse,
  RepoFilesResponse,
  RepoResponse,
  SymbolResponse,
  SymbolReferenceResponse,
  HybridSearchResultResponse,
  ProjectSummary,
  ArchitectureDiagram,
  FolderIntelligence,
  ChatResponse,
  SmartSearchResponse,
  ApiEndpoint,
  DatabaseSchema,
  AuthFlow,
  CallTraceNode,
  TraceFlowResponse,
  TraceEntryPoint,
  CodeReviewFinding,
  RefactoringSuggestion,
  CommitTimelineEra,
  ArchitectureDiffResponse,
  OnboardingStep,
  DependencyGraphData,
} from '@/types/api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const { headers: optHeaders, ...restOptions } = options ?? {};
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...restOptions,
    headers: {
      'Content-Type': 'application/json',
      ...(optHeaders instanceof Headers
        ? Object.fromEntries(optHeaders.entries())
        : Array.isArray(optHeaders)
          ? Object.fromEntries(optHeaders)
          : optHeaders),
    },
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error (${res.status}): ${errorText}`);
  }

  return res.json();
}

export const api = {
  ingestRepo: (data: IngestRequest) =>
    fetchJSON<IngestResponse>('/api/v1/ingest', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getJobStatus: (jobId: string) => fetchJSON<JobResponse>(`/api/v1/jobs/${jobId}`),

  getRepos: () => fetchJSON<RepoResponse[]>('/api/v1/repos'),

  getRepo: (id: string) => fetchJSON<RepoResponse>(`/api/v1/repos/${id}`),

  getRepoFiles: (id: string) => fetchJSON<RepoFilesResponse>(`/api/v1/repos/${id}/files`),

  getSymbols: (repoId: string, q?: string, kind?: string) => {
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (kind) params.set('kind', kind);
    return fetchJSON<SymbolResponse[]>(`/api/v1/repos/${repoId}/symbols?${params.toString()}`);
  },

  getSymbolReferences: (repoId: string, symbolId: string) =>
    fetchJSON<SymbolReferenceResponse>(`/api/v1/repos/${repoId}/symbols/${symbolId}/references`),

  hybridSearch: (repoId: string, query: string, kind?: string) =>
    fetchJSON<HybridSearchResultResponse[]>(`/api/v1/repos/${repoId}/search/hybrid`, {
      method: 'POST',
      body: JSON.stringify({ query, kind, limit: 20 }),
    }),

  getSummary: (repoId: string) => fetchJSON<ProjectSummary>(`/api/v1/repos/${repoId}/summary`),

  getArchitecture: (repoId: string) => fetchJSON<ArchitectureDiagram>(`/api/v1/repos/${repoId}/architecture`),

  getFolders: (repoId: string) => fetchJSON<FolderIntelligence[]>(`/api/v1/repos/${repoId}/folders`),

  postChat: (repoId: string, message: string, conversationId?: string) =>
    fetchJSON<ChatResponse>(`/api/v1/repos/${repoId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    }),

  postSmartSearch: (repoId: string, query: string, limit: number = 50) =>
    fetchJSON<SmartSearchResponse>(`/api/v1/repos/${repoId}/search/smart`, {
      method: 'POST',
      body: JSON.stringify({ query, limit }),
    }),

  getApiEndpoints: (repoId: string) => fetchJSON<ApiEndpoint[]>(`/api/v1/repos/${repoId}/endpoints`),

  getDatabaseSchema: (repoId: string) => fetchJSON<DatabaseSchema>(`/api/v1/repos/${repoId}/database`),

  getAuthFlow: (repoId: string) => fetchJSON<AuthFlow>(`/api/v1/repos/${repoId}/auth-flow`),

  getExecutionTrace: (repoId: string) => fetchJSON<CallTraceNode[]>(`/api/v1/repos/${repoId}/trace`),

  postTraceFlow: (repoId: string, entryPointSymbol?: string) =>
    fetchJSON<TraceFlowResponse>(`/api/v1/repos/${repoId}/trace/flow`, {
      method: 'POST',
      body: JSON.stringify({ entry_point_symbol: entryPointSymbol }),
    }),

  getTraceEntryPoints: (repoId: string) => fetchJSON<TraceEntryPoint[]>(`/api/v1/repos/${repoId}/trace/entry-points`),

  postCodeReview: (repoId: string, scope: string = 'all') =>
    fetchJSON<CodeReviewFinding[]>(`/api/v1/repos/${repoId}/code-review`, {
      method: 'POST',
      body: JSON.stringify({ scope }),
    }),

  postRefactor: (repoId: string) =>
    fetchJSON<RefactoringSuggestion[]>(`/api/v1/repos/${repoId}/refactor`, {
      method: 'POST',
    }),

  getTimeline: (repoId: string) => fetchJSON<CommitTimelineEra[]>(`/api/v1/repos/${repoId}/timeline`),

  postDiff: (repoId: string, baseBranch: string = 'main', headBranch: string = 'feature/v2') =>
    fetchJSON<ArchitectureDiffResponse>(`/api/v1/repos/${repoId}/diff`, {
      method: 'POST',
      body: JSON.stringify({ base_branch: baseBranch, head_branch: headBranch }),
    }),

  getOnboarding: (repoId: string) => fetchJSON<OnboardingStep[]>(`/api/v1/repos/${repoId}/onboarding`),

  getDependencyGraph: (repoId: string) => fetchJSON<DependencyGraphData>(`/api/v1/repos/${repoId}/dependency-graph`),
};
