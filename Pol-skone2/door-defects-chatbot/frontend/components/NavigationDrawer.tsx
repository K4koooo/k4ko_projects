'use client'

import { useEffect, useRef } from 'react'
import { triggerIngest } from '@/lib/api'

interface NavigationDrawerProps {
  open: boolean
  onClose: () => void
  onNewChat: () => void
  onShowSnackbar: (text: string, type?: 'error' | 'success') => void
}

export function NavigationDrawer({ open, onClose, onNewChat, onShowSnackbar }: NavigationDrawerProps) {
  const drawerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [open, onClose])

  const handleIngest = async () => {
    onClose()
    onShowSnackbar('Indeksowanie plików Excel...', 'success')
    try {
      const result = await triggerIngest()
      if (result.errors.length > 0) {
        onShowSnackbar(`Częściowy błąd: ${result.errors[0]}`, 'error')
      } else {
        onShowSnackbar(
          `Zaindeksowano ${result.documents_added} nowych wierszy z ${result.files_processed} pliku(-ów)`,
          'success'
        )
      }
    } catch (err) {
      onShowSnackbar('Błąd indeksowania danych', 'error')
    }
  }

  return (
    <>
      {/* Scrim */}
      <div
        onClick={onClose}
        className="fixed inset-0 z-20 transition-opacity duration-300"
        style={{
          background: 'rgba(0,0,0,0.5)',
          opacity: open ? 1 : 0,
          pointerEvents: open ? 'auto' : 'none',
        }}
        aria-hidden
      />

      {/* Drawer */}
      <nav
        ref={drawerRef}
        className="fixed left-0 top-0 h-full z-30 flex flex-col"
        style={{
          width: 320,
          background: 'var(--md-sys-color-surface-container-low)',
          transform: open ? 'translateX(0)' : 'translateX(-100%)',
          transition: 'transform 300ms cubic-bezier(0.2, 0, 0, 1)',
          borderRadius: '0 28px 28px 0',
          boxShadow: open ? '4px 0 16px rgba(0,0,0,0.2)' : 'none',
        }}
        aria-label="Menu nawigacyjne"
      >
        {/* Header */}
        <div
          className="flex items-center gap-3 px-6 pt-6 pb-4"
          style={{ borderBottom: '1px solid var(--md-sys-color-outline-variant)' }}
        >
          <span
            className="material-symbols-rounded filled"
            style={{ fontSize: 32, color: 'var(--md-sys-color-primary)' }}
          >
            door_front
          </span>
          <div>
            <p className="font-medium" style={{ color: 'var(--md-sys-color-on-surface)', fontSize: '0.9rem' }}>
              Wady Produkcyjne
            </p>
            <p style={{ fontSize: '0.75rem', color: 'var(--md-sys-color-on-surface-variant)' }}>
              Lokalny asystent RAG
            </p>
          </div>
          <button className="md3-icon-btn ml-auto" onClick={onClose} aria-label="Zamknij menu">
            <span className="material-symbols-rounded" style={{ fontSize: 22 }}>close</span>
          </button>
        </div>

        {/* Nowy czat */}
        <div className="px-4 pt-4">
          <button
            onClick={onNewChat}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-full font-medium text-sm transition-all"
            style={{
              background: 'var(--md-sys-color-secondary-container)',
              color: 'var(--md-sys-color-on-secondary-container)',
              border: 'none',
              cursor: 'pointer',
            }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLButtonElement).style.opacity = '0.85'
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLButtonElement).style.opacity = '1'
            }}
          >
            <span className="material-symbols-rounded" style={{ fontSize: 20 }}>add</span>
            Nowy czat
            <span style={{ fontSize: '0.7rem', marginLeft: 'auto', opacity: 0.6 }}>Ctrl+K</span>
          </button>
        </div>

        {/* Lista akcji */}
        <div className="flex-1 px-3 py-2 overflow-y-auto">
          <p
            className="px-3 pt-4 pb-1 text-xs font-medium tracking-wide uppercase"
            style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
          >
            Dane
          </p>

          <DrawerItem
            icon="sync"
            label="Przeładuj dane Excel"
            sublabel="Zaindeksuj nowe pliki z data/excel/"
            onClick={handleIngest}
          />

          <p
            className="px-3 pt-5 pb-1 text-xs font-medium tracking-wide uppercase"
            style={{ color: 'var(--md-sys-color-on-surface-variant)' }}
          >
            Informacje
          </p>

          <DrawerItem
            icon="info"
            label="Jak używać?"
            sublabel="Wrzuć pliki .xlsx do data/excel/ i przeładuj"
            onClick={onClose}
          />
        </div>

        {/* Footer */}
        <div
          className="px-6 py-4 text-xs"
          style={{
            color: 'var(--md-sys-color-on-surface-variant)',
            borderTop: '1px solid var(--md-sys-color-outline-variant)',
          }}
        >
          Door Defects Chatbot · v1.0<br />
          <span style={{ opacity: 0.7 }}>Działa w pełni offline</span>
        </div>
      </nav>
    </>
  )
}

function DrawerItem({
  icon,
  label,
  sublabel,
  onClick,
}: {
  icon: string
  label: string
  sublabel?: string
  onClick?: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-3 py-3 rounded-xl text-left transition-colors md3-state-layer"
      style={{
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
        color: 'var(--md-sys-color-on-surface)',
      }}
    >
      <span
        className="material-symbols-rounded"
        style={{ fontSize: 22, color: 'var(--md-sys-color-on-surface-variant)', flexShrink: 0 }}
      >
        {icon}
      </span>
      <div>
        <p style={{ fontSize: '0.875rem', fontWeight: 500 }}>{label}</p>
        {sublabel && (
          <p style={{ fontSize: '0.75rem', color: 'var(--md-sys-color-on-surface-variant)' }}>{sublabel}</p>
        )}
      </div>
    </button>
  )
}
