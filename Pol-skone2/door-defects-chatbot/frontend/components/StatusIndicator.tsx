'use client'

import { useEffect, useState, useCallback } from 'react'
import { fetchHealth, fetchStats } from '@/lib/api'
import type { HealthStatus, StatsData } from '@/lib/types'

export function StatusIndicator() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [stats, setStats] = useState<StatsData | null>(null)

  const refresh = useCallback(async () => {
    try {
      const [h, s] = await Promise.all([fetchHealth(), fetchStats()])
      setHealth(h)
      setStats(s)
    } catch {
      setHealth(null)
    }
  }, [])

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 30_000)
    return () => clearInterval(interval)
  }, [refresh])

  const isOk = health?.status === 'ok'
  const dot = isOk ? '#34A853' : health ? '#FBBC04' : '#EA4335'
  const label = isOk ? 'Online' : health ? 'Degraded' : 'Offline'

  return (
    <div className="flex items-center gap-2 mr-1">
      {/* Status Ollama */}
      <div
        className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium"
        style={{
          background: 'var(--md-sys-color-surface-container-highest)',
          color: 'var(--md-sys-color-on-surface-variant)',
          border: '1px solid var(--md-sys-color-outline-variant)',
        }}
        title={`Ollama: ${health?.ollama ? 'ok' : 'offline'} | ChromaDB: ${health?.chromadb ? 'ok' : 'offline'}`}
      >
        <span
          style={{
            width: 7, height: 7, borderRadius: '50%',
            background: dot, flexShrink: 0,
            boxShadow: `0 0 0 2px ${dot}33`,
          }}
        />
        <span style={{ color: 'var(--md-sys-color-on-surface)' }}>{label}</span>
      </div>

      {/* Licznik dokumentów */}
      {stats && stats.total_documents > 0 && (
        <div
          className="flex items-center gap-1 px-2 py-1 rounded-full text-xs"
          style={{
            background: 'var(--md-sys-color-primary-container)',
            color: 'var(--md-sys-color-on-primary-container)',
          }}
          title={`Pliki: ${stats.source_files.join(', ')}`}
        >
          <span className="material-symbols-rounded" style={{ fontSize: 14 }}>database</span>
          <span>{stats.total_documents}</span>
        </div>
      )}
    </div>
  )
}
