'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import { AppBar } from '@/components/AppBar'
import { NavigationDrawer } from '@/components/NavigationDrawer'
import { ChatWindow } from '@/components/ChatWindow'
import { ComposerBar } from '@/components/ComposerBar'
import { Snackbar } from '@/components/Snackbar'
import { applyTheme, getSystemPrefersDark } from '@/lib/theme'
import { streamChat } from '@/lib/api'
import type { Message } from '@/lib/types'

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const [snackbar, setSnackbar] = useState<{ text: string; type?: 'error' | 'success' } | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem('theme')
    const prefersDark = stored === 'dark' || (!stored && getSystemPrefersDark())
    setDarkMode(prefersDark)
    applyTheme(prefersDark)

    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        handleNewChat()
      }
      if (e.key === 'Escape') setDrawerOpen(false)
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const toggleDark = useCallback(() => {
    setDarkMode(prev => {
      const next = !prev
      applyTheme(next)
      localStorage.setItem('theme', next ? 'dark' : 'light')
      return next
    })
  }, [])

  const showSnackbar = useCallback((text: string, type: 'error' | 'success' = 'success') => {
    setSnackbar({ text, type })
    setTimeout(() => setSnackbar(null), 4000)
  }, [])

  const handleNewChat = useCallback(() => {
    if (isStreaming) {
      abortRef.current?.abort()
      setIsStreaming(false)
    }
    setMessages([])
    setDrawerOpen(false)
  }, [isStreaming])

  const handleSend = useCallback(async (question: string) => {
    if (isStreaming || !question.trim()) return

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    const assistantId = `assistant-${Date.now()}`
    const assistantMsg: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      isStreaming: true,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMsg, assistantMsg])
    setIsStreaming(true)

    const controller = new AbortController()
    abortRef.current = controller

    const history = messages.map(m => ({ role: m.role, content: m.content }))

    try {
      for await (const event of streamChat(question, history, 5, controller.signal)) {
        if (event.type === 'token') {
          setMessages(prev =>
            prev.map(m => m.id === assistantId ? { ...m, content: m.content + event.content } : m)
          )
        } else if (event.type === 'sources') {
          setMessages(prev =>
            prev.map(m => m.id === assistantId ? { ...m, sources: event.content } : m)
          )
        } else if (event.type === 'error') {
          setMessages(prev =>
            prev.map(m => m.id === assistantId
              ? { ...m, content: `Błąd: ${event.content}`, isError: true }
              : m
            )
          )
          showSnackbar(event.content, 'error')
        }
      }
    } catch (err: unknown) {
      if ((err as Error).name === 'AbortError') return
      const msg = err instanceof Error ? err.message : 'Nieznany błąd'
      setMessages(prev =>
        prev.map(m => m.id === assistantId
          ? { ...m, content: `Nie udało się uzyskać odpowiedzi: ${msg}`, isError: true }
          : m
        )
      )
      showSnackbar(msg, 'error')
    } finally {
      setMessages(prev =>
        prev.map(m => m.id === assistantId ? { ...m, isStreaming: false } : m)
      )
      setIsStreaming(false)
      abortRef.current = null
    }
  }, [isStreaming, messages, showSnackbar])

  const handleStop = useCallback(() => {
    abortRef.current?.abort()
    setIsStreaming(false)
    setMessages(prev =>
      prev.map(m => m.isStreaming ? { ...m, isStreaming: false } : m)
    )
  }, [])

  return (
    <div className="flex flex-col h-dvh" style={{ background: 'var(--md-sys-color-background)' }}>
      <AppBar
        onMenuClick={() => setDrawerOpen(true)}
        darkMode={darkMode}
        onToggleDark={toggleDark}
      />

      <NavigationDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onNewChat={handleNewChat}
        onShowSnackbar={showSnackbar}
      />

      <main className="flex-1 overflow-hidden flex flex-col">
        <ChatWindow messages={messages} isStreaming={isStreaming} />
        <ComposerBar
          onSend={handleSend}
          onStop={handleStop}
          isStreaming={isStreaming}
          disabled={false}
        />
      </main>

      {snackbar && (
        <Snackbar text={snackbar.text} type={snackbar.type} />
      )}
    </div>
  )
}
