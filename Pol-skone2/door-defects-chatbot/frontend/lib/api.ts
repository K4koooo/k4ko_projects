import type { HealthStatus, StatsData, IngestResult, SourceDocument } from './types'

export type SSEEvent =
  | { type: 'token'; content: string }
  | { type: 'sources'; content: SourceDocument[] }
  | { type: 'error'; content: string }

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export async function* streamChat(
  question: string,
  history: ChatMessage[],
  topK = 5,
  signal?: AbortSignal
): AsyncGenerator<SSEEvent> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history, top_k: topK }),
    signal,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const raw = line.slice(6).trim()
        if (raw === '[DONE]') return
        try {
          yield JSON.parse(raw) as SSEEvent
        } catch {
          // ignoruj nieprawidłowe JSON linie
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch('/api/health', { next: { revalidate: 0 } })
  if (!res.ok) throw new Error('Health check failed')
  return res.json()
}

export async function fetchStats(): Promise<StatsData> {
  const res = await fetch('/api/stats', { next: { revalidate: 0 } })
  if (!res.ok) throw new Error('Stats fetch failed')
  return res.json()
}

export async function triggerIngest(): Promise<IngestResult> {
  const res = await fetch('/api/ingest', { method: 'POST' })
  if (!res.ok) throw new Error('Ingest failed')
  return res.json()
}
