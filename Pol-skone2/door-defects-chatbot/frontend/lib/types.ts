export interface SourceDocument {
  source_file: string
  sheet_name: string
  row_number: number
  content: string
  metadata: Record<string, string>
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: SourceDocument[]
  isStreaming?: boolean
  isError?: boolean
  timestamp: Date
}

export interface HealthStatus {
  status: 'ok' | 'degraded' | 'error'
  ollama: boolean
  chromadb: boolean
  llm_model_ready: boolean
  embed_model_ready: boolean
}

export interface StatsData {
  total_documents: number
  source_files: string[]
  collection_name: string
}

export interface IngestResult {
  status: string
  files_processed: number
  documents_added: number
  documents_skipped: number
  errors: string[]
}
