'use client'

import { useState, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { SourceChips } from './SourceChips'
import { LoadingDots } from './LoadingDots'
import type { Message } from '@/lib/types'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false)
  const isDark = typeof document !== 'undefined'
    && document.documentElement.getAttribute('data-theme') === 'dark'

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [message.content])

  if (message.role === 'user') {
    return (
      <div className="flex justify-end animate-slide-in-bottom">
        <div
          className="bubble-user max-w-[75%] px-4 py-3 text-sm leading-relaxed"
          style={{ wordBreak: 'break-word' }}
        >
          {message.content}
        </div>
      </div>
    )
  }

  // Asystent
  return (
    <div className="flex gap-3 animate-slide-in-bottom">
      {/* Avatar */}
      <div
        className="flex items-center justify-center w-9 h-9 rounded-full shrink-0 mt-0.5"
        style={{ background: 'var(--md-sys-color-primary-container)' }}
      >
        <span
          className="material-symbols-rounded filled"
          style={{ fontSize: 18, color: 'var(--md-sys-color-on-primary-container)' }}
        >
          smart_toy
        </span>
      </div>

      {/* Treść */}
      <div className="flex-1 min-w-0">
        {/* Wiadomość lub loading */}
        {message.isStreaming && !message.content ? (
          <div
            className="inline-block px-4 py-3 rounded-xl"
            style={{ background: 'var(--md-sys-color-surface-container-high)' }}
          >
            <LoadingDots />
          </div>
        ) : (
          <div>
            <div
              className="bubble-assistant px-4 py-3 text-sm"
              style={{
                ...(message.isError ? {
                  background: 'var(--md-sys-color-error-container)',
                  color: 'var(--md-sys-color-on-error-container)',
                  borderRadius: '4px 20px 20px 20px',
                } : {}),
              }}
            >
              <div className="prose-md3">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, className, children, ...props }: any) {
                      const match = /language-(\w+)/.exec(className || '')
                      const isBlock = !!(node?.position?.start.line !== node?.position?.end.line || match)
                      return isBlock ? (
                        <SyntaxHighlighter
                          style={isDark ? oneDark : oneLight}
                          language={match ? match[1] : 'text'}
                          PreTag="div"
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>{children}</code>
                      )
                    },
                  }}
                >
                  {message.content || ''}
                </ReactMarkdown>
              </div>
              {/* Migający kursor podczas streamowania */}
              {message.isStreaming && message.content && (
                <span
                  className="inline-block w-0.5 h-4 ml-0.5 align-middle animate-shimmer"
                  style={{ background: 'var(--md-sys-color-primary)' }}
                />
              )}
            </div>

            {/* Akcje pod wiadomością */}
            {!message.isStreaming && message.content && !message.isError && (
              <div className="flex items-center gap-1 mt-1">
                <button
                  className="md3-icon-btn"
                  onClick={handleCopy}
                  title="Kopiuj odpowiedź"
                  aria-label="Kopiuj"
                  style={{ width: 32, height: 32 }}
                >
                  <span className="material-symbols-rounded" style={{ fontSize: 16 }}>
                    {copied ? 'check' : 'content_copy'}
                  </span>
                </button>
              </div>
            )}

            {/* Chipy źródeł */}
            {!message.isStreaming && message.sources && message.sources.length > 0 && (
              <SourceChips sources={message.sources} />
            )}
          </div>
        )}
      </div>
    </div>
  )
}
