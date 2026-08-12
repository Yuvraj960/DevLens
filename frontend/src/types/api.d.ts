export interface IngestRequest {
  source: 'github' | 'zip' | 'folder';
  url?: string;
  branch?: string;
  subpath?: string;
  file_path?: string;
}

export interface IngestResponse {
  job_id: string;
  repo_id: string;
  status: string;
  message: string;
}

export interface JobProgress {
  stage: string;
  progress: number;
  message: string;
  current_file?: string | null;
  files_processed?: number;
  total_files?: number;
}

export interface JobResponse {
  id: string;
  repo_id: string;
  status: string;
  stage: string;
  progress: number;
  message: string;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface FileTreeNode {
  name: string;
  path: string;
  is_directory: boolean;
  size_bytes?: number;
  children?: FileTreeNode[];
}

export interface RepoResponse {
  id: string;
  name: string;
  source_type: string;
  source_url?: string | null;
  default_branch: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface RepoFilesResponse {
  repo_id: string;
  total_files: number;
  total_loc: number;
  file_tree: FileTreeNode[];
}

export interface SymbolResponse {
  id: string;
  name: string;
  kind: string;
  file_path: string;
  start_line: number;
  end_line: number;
  signature?: string | null;
  docstring?: string | null;
  is_exported: boolean;
  is_async: boolean;
}

export interface SymbolReferenceResponse {
  symbol_name: string;
  references: Array<{
    file_path: string;
    imported_from: string;
    is_external: boolean;
  }>;
}

export interface HybridSearchResultResponse {
  symbol_id?: string | null;
  name: string;
  kind: string;
  file_path: string;
  start_line: number;
  end_line: number;
  signature?: string | null;
  score: number;
  matched_by: string;
}

export interface ProjectSummary {
  overview: string;
  stack: {
    primary: string;
    framework: string;
    language: string;
    database?: string | null;
    auth?: string | null;
    testing?: string | null;
    infra?: string[];
  };
  metrics: {
    total_files: number;
    total_loc: number;
    languages: Record<string, number>;
    complexity_score: number;
    estimated_onboarding_minutes: number;
  };
  key_modules: Array<{
    name: string;
    path: string;
    purpose: string;
    importance: number;
  }>;
  entry_points: Array<{
    type: string;
    name: string;
    file_path: string;
    description: string;
  }>;
  risks: Array<{
    type: string;
    severity: string;
    description: string;
  }>;
}

export interface ArchNode {
  id: string;
  label: string;
  layer: 'presentation' | 'api' | 'business_logic' | 'data_access' | 'external' | 'infrastructure';
  file_paths: string[];
  symbols: SymbolResponse[];
  metadata: {
    file_count: number;
    loc: number;
    complexity: number;
  };
}

export interface ArchEdge {
  source: string;
  target: string;
  type: string;
  weight: number;
}

export interface ArchitectureDiagram {
  nodes: ArchNode[];
  edges: ArchEdge[];
  layers: string[];
}

export interface FolderIntelligence {
  path: string;
  purpose: string;
  key_files: Array<{
    path: string;
    reason: string;
    symbol_count: number;
  }>;
  patterns: string[];
  complexity: number;
  test_coverage: number;
  last_changed?: string | null;
}

export interface Citation {
  file_path: string;
  start_line: number;
  end_line: number;
  symbol_id?: string | null;
  snippet: string;
  relevance_score?: number;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  citations: Citation[];
  suggested_followups: string[];
  metadata?: {
    tokens_used: number;
    model: string;
    retrieval_time_ms: number;
    generation_time_ms: number;
  };
}

export interface SmartSearchResultItem {
  symbol: SymbolResponse;
  file_path: string;
  match_type: string;
  context: string;
}

export interface SmartSearchResponse {
  results: SmartSearchResultItem[];
  total: number;
  query_time_ms: number;
}

export interface ApiEndpoint {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';
  path: string;
  controller: {
    symbol_id: string;
    name: string;
    file_path: string;
    line: number;
  };
  framework: string;
  middleware: Array<{
    name: string;
    type: string;
    file_path: string;
    line: number;
  }>;
  summary: string;
  tags: string[];
  deprecated: boolean;
}

export interface DbColumn {
  name: string;
  type: string;
  nullable: boolean;
  default?: string | null;
  is_primary_key: boolean;
  is_foreign_key: boolean;
  source: string;
}

export interface DbTable {
  name: string;
  schema?: string | null;
  columns: DbColumn[];
  primary_keys: string[];
  source: string;
}

export interface DbRelationship {
  from_table: string;
  to_table: string;
  from_columns: string[];
  to_columns: string[];
  type: string;
  source: string;
}

export interface DatabaseSchema {
  tables: DbTable[];
  relationships: DbRelationship[];
  metadata: {
    orm: string;
    total_tables: number;
    total_columns: number;
  };
}

export interface AuthFlowStep {
  id: string;
  label: string;
  type: string;
  file_path: string;
  line: number;
  description: string;
}

export interface AuthFlow {
  steps: AuthFlowStep[];
  entry_points: Array<{
    type: string;
    path: string;
    controller: string;
  }>;
  protected_routes: Array<{
    path: string;
    middleware_chain: string[];
  }>;
  token_handling: {
    type: string;
    verification_method: string;
    storage: string;
  };
}

export interface CallTraceNode {
  symbol_id: string;
  name: string;
  type: string;
  file_path: string;
  line: number;
  depth: number;
  async: boolean;
  error_handling: string[];
}

export interface TraceNode {
  id: string;
  symbol_id: string;
  label: string;
  kind: string;
  layer: string;
  file_path: string;
  line: number;
  depth: number;
  is_async: boolean;
  signature: string;
  db_operations?: Array<{
    operation: string;
    table: string;
    orm_method: string;
  }>;
  external_calls?: Array<{
    service: string;
    method: string;
    url_pattern: string;
    client: string;
  }>;
  ai_explanation?: string;
}

export interface TraceEdge {
  id: string;
  source: string;
  target: string;
  confidence_score: number;
  is_dashed: boolean;
  call_type: string;
}

export interface TraceEntryPoint {
  id: string;
  label: string;
  target_symbol: string;
  file_path: string;
  line: number;
  type: string;
}

export interface TraceFlowResponse {
  nodes: TraceNode[];
  edges: TraceEdge[];
  entry_points: TraceEntryPoint[];
  metadata: {
    total_nodes: number;
    total_edges: number;
    max_depth: number;
    traversal_time_ms: number;
  };
}

export interface CodeReviewFinding {
  id: string;
  category: string;
  severity: string;
  title: string;
  file_path: string;
  line: number;
  symbol_name: string;
  description: string;
  suggestion: string;
}

export interface RefactoringSuggestion {
  id: string;
  symbol_id: string;
  symbol_name: string;
  file_path: string;
  line: number;
  metrics: {
    cyclomatic_complexity: number;
    cognitive_complexity: number;
    loc: number;
  };
  issue: string;
  impact: string;
  effort: string;
  proposed_diff: string;
}

export interface CommitTimelineEra {
  period: string;
  date: string;
  author: string;
  summary: string;
  files_changed: number;
  insertions: number;
  deletions: number;
}

export interface ArchitectureDiffResponse {
  base_branch: string;
  head_branch: string;
  summary: string;
  added_endpoints: Array<{
    method: string;
    path: string;
    controller: string;
  }>;
  removed_endpoints: Array<{
    method: string;
    path: string;
  }>;
  modified_schemas: Array<{
    table: string;
    change: string;
  }>;
  security_risks: Array<{
    severity: string;
    description: string;
  }>;
  risk_score: number;
}

export interface OnboardingStep {
  step: number;
  title: string;
  estimated_minutes: number;
  description: string;
  key_files: string[];
  checkpoint_question: string;
}

export interface DependencyGraphData {
  nodes: Array<{
    id: string;
    label: string;
    kind: string;
    file_path: string;
    line: number;
    is_exported: boolean;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    relationship: string;
  }>;
  metadata: {
    total_nodes: number;
    total_edges: number;
  };
}
