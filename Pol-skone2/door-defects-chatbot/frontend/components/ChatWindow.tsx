'use client'

import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import type { Message } from '@/lib/types'

const SUGGESTION_QUESTIONS = [
  'Jakie wady najczęściej występują w marcu 2026?',
  'Który wydział generuje najwięcej wad?',
  'Jakie są główne problemy z powierzchnią drzwi?',
  'Ile wadliwych sztuk futryn odnotowano?',
  'Jakie wady okuć wystąpiły najczęściej?',
]

interface ChatWindowProps {
  messages: Message[]
  isStreaming: boolean
}

export function ChatWindow({ messages, isStreaming }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto flex flex-col items-center justify-center px-4 py-8">
        <EmptyState />
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-3xl mx-auto px-4 py-6 flex flex-col gap-4">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="w-full max-w-2xl flex flex-col items-center text-center">
      {/* Duża ikona */}
      <div
        className="flex items-center justify-center w-20 h-20 rounded-full mb-6"
        style={{ background: 'var(--md-sys-color-primary-container)' }}
      >
        <span
          className="material-symbols-rounded filled"
          style={{ fontSize: 44, color: 'var(--md-sys-color-on-primary-container)' }}
        >
          door_front
        </span>
      </div>

      <h1
        className="font-medium mb-2"
        style={{ fontSize: '1.5rem', color: 'var(--md-sys-color-on-surface)' }}
      >
        Asystent Wad Produkcyjnych
      </h1>
      <p className="mb-8 max-w-md" style={{ color: 'var(--md-sys-color-on-surface-variant)', fontSize: '0.9rem' }}>
        Zadaj pytanie o dane z zaindeksowanych plików Excel.
        Odpowiedzi są generowane lokalnie — żadne dane nie opuszczają Twojego komputera.
      </p>

      {/* Sugestie pytań */}
      <div className="w-full">
        <p
          className="text-xs font-medium mb-3 tracking-wide uppercase"
          style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
        >
          Przykładowe pytania
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {SUGGESTION_QUESTIONS.map((q, i) => (
            <SuggestionChip key={i} text={q} />
          ))}
        </div>
      </div>

      <p className="mt-10 text-xs" style={{ color: 'var(--md-sys-color-outline)' }}>
        Ctrl+K · Nowy czat &nbsp;|&nbsp; Shift+Enter · Nowa linia
      </p>
    </div>
  )
}

function SuggestionChip({ text }: { text: string }) {
  // Kliknięcie wstrzykuje pytanie do ComposerBar przez CustomEvent
  const handleClick = () => {
    window.dispatchEvent(new CustomEvent('suggestion-click', { detail: text }))
  }

  return (
    <button
      onClick={handleClick}
      className="flex items-start gap-2 px-4 py-3 rounded-xl text-left text-sm transition-all md3-state-layer"
      style={{
        background: 'var(--md-sys-color-surface-container)',
        border: '1px solid var(--md-sys-color-outline-variant)',
        color: 'var(--md-sys-color-on-surface)',
        cursor: 'pointer',
        borderRadius: 12,
      }}
    >
      <span className="material-symbols-rounded" style={{ fontSize: 16, color: 'var(--md-sys-color-primary)', flexShrink: 0, marginTop: 1 }}>
        chat_bubble
      </span>
      {text}
    </button>
  )
}
