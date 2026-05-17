'use client'

import '@material/web/chips/assist-chip.js'
import '@material/web/chips/chip-set.js'

import { useState } from 'react'
import type { SourceDocument } from '@/lib/types'

interface SourceChipsProps {
  sources: SourceDocument[]
}

export function SourceChips({ sources }: SourceChipsProps) {
  const [expanded, setExpanded] = useState<number | null>(null)

  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-3">
      <p className="text-xs mb-2" style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
        Źródła ({sources.length}):
      </p>

      {/* Chipy MD3 */}
      <div className="flex flex-wrap gap-2">
        {sources.map((src, i) => (
          <button
            key={i}
            onClick={() => setExpanded(expanded === i ? null : i)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all"
            style={{
              border: `1px solid ${expanded === i
                ? 'var(--md-sys-color-primary)'
                : 'var(--md-sys-color-outline)'}`,
              background: expanded === i
                ? 'var(--md-sys-color-primary-container)'
                : 'transparent',
              color: expanded === i
                ? 'var(--md-sys-color-on-primary-container)'
                : 'var(--md-sys-color-on-surface-variant)',
              cursor: 'pointer',
            }}
          >
            <span className="material-symbols-rounded" style={{ fontSize: 14 }}>description</span>
            {src.source_file} · ark. {src.sheet_name} · w. {src.row_number}
            <span className="material-symbols-rounded" style={{ fontSize: 14 }}>
              {expanded === i ? 'expand_less' : 'expand_more'}
            </span>
          </button>
        ))}
      </div>

      {/* Rozwinięta karta ze szczegółami */}
      {expanded !== null && sources[expanded] && (
        <div
          className="mt-2 p-3 rounded-xl text-sm animate-slide-in-bottom"
          style={{
            background: 'var(--md-sys-color-surface-container-high)',
            border: '1px solid var(--md-sys-color-outline-variant)',
          }}
        >
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-rounded" style={{ fontSize: 16, color: 'var(--md-sys-color-primary)' }}>
              table_rows
            </span>
            <p className="font-medium text-xs" style={{ color: 'var(--md-sys-color-on-surface-variant)' }}>
              {sources[expanded].source_file} · {sources[expanded].sheet_name} · wiersz {sources[expanded].row_number}
            </p>
          </div>
          <p
            className="font-mono text-xs leading-relaxed break-words"
            style={{ color: 'var(--md-sys-color-on-surface)' }}
          >
            {sources[expanded].content}
          </p>
        </div>
      )}
    </div>
  )
}
