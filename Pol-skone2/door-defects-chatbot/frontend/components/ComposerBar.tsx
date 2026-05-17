'use client'

import '@material/web/progress/circular-progress.js'

import { useState, useRef, useCallback, useEffect } from 'react'

interface ComposerBarProps {
  onSend: (text: string) => void
  onStop: () => void
  isStreaming: boolean
  disabled: boolean
}

export function ComposerBar({ onSend, onStop, isStreaming, disabled }: ComposerBarProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Autoresize textarea
  const resize = useCallback(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    const maxH = 5 * 24 + 16 // 5 linii + padding
    el.style.height = `${Math.min(el.scrollHeight, maxH)}px`
  }, [])

  useEffect(() => { resize() }, [value, resize])

  // Odbierz sugestię z ChatWindow
  useEffect(() => {
    const handler = (e: Event) => {
      const text = (e as CustomEvent<string>).detail
      setValue(text)
      setTimeout(() => textareaRef.current?.focus(), 50)
    }
    window.addEventListener('suggestion-click', handler)
    return () => window.removeEventListener('suggestion-click', handler)
  }, [])

  const handleSend = useCallback(() => {
    const text = value.trim()
    if (!text || isStreaming) return
    onSend(text)
    setValue('')
  }, [value, isStreaming, onSend])

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])

  const canSend = value.trim().length > 0 && !isStreaming && !disabled

  return (
    <div className="px-4 pb-4 pt-2 shrink-0">
      <div className="max-w-3xl mx-auto">
        <div
          className="flex items-end gap-2 px-3 py-2 rounded-3xl"
          style={{
            background: 'var(--md-sys-color-surface-container-highest)',
            border: '1px solid var(--md-sys-color-outline-variant)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.10)',
            transition: 'border-color 150ms',
          }}
          onFocusCapture={e => {
            (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--md-sys-color-primary)'
          }}
          onBlurCapture={e => {
            (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--md-sys-color-outline-variant)'
          }}
        >
          {/* Placeholder ikona */}
          <button
            className="md3-icon-btn shrink-0"
            style={{ width: 36, height: 36, cursor: 'default', opacity: 0.4 }}
            disabled
            aria-label="Załącz plik (wkrótce)"
            title="Załącz plik (wkrótce)"
          >
            <span className="material-symbols-rounded" style={{ fontSize: 20 }}>attach_file</span>
          </button>

          {/* Textarea */}
          <textarea
            ref={textareaRef}
            className="md3-composer-field flex-1"
            rows={1}
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Zapytaj o wady produkcyjne..."
            disabled={disabled}
            style={{ maxHeight: '7rem', overflowY: 'auto' }}
            aria-label="Wiadomość"
          />

          {/* Stop / Wyślij */}
          {isStreaming ? (
            <button
              className="md3-icon-btn shrink-0"
              onClick={onStop}
              aria-label="Zatrzymaj generowanie"
              title="Zatrzymaj"
              style={{
                width: 36, height: 36,
                background: 'var(--md-sys-color-error-container)',
                color: 'var(--md-sys-color-on-error-container)',
              }}
            >
              <span className="material-symbols-rounded filled" style={{ fontSize: 18 }}>stop</span>
            </button>
          ) : (
            <button
              className="md3-icon-btn primary shrink-0"
              onClick={handleSend}
              disabled={!canSend}
              aria-label="Wyślij"
              title="Wyślij (Enter)"
              style={{ width: 36, height: 36 }}
            >
              <span className="material-symbols-rounded filled" style={{ fontSize: 20 }}>arrow_upward</span>
            </button>
          )}
        </div>

        <p
          className="text-center mt-1.5 text-xs"
          style={{ color: 'var(--md-sys-color-on-surface-variant)', opacity: 0.6 }}
        >
          Enter — wyślij &nbsp;·&nbsp; Shift+Enter — nowa linia
          {isStreaming && (
            <span> &nbsp;·&nbsp;
              <md-circular-progress indeterminate
                style={{ '--md-circular-progress-size': '12px', '--md-circular-progress-active-indicator-width': '2' } as React.CSSProperties}
              />
              &nbsp; Generowanie...
            </span>
          )}
        </p>
      </div>
    </div>
  )
}
