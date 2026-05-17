'use client'

import { useEffect, useState } from 'react'
import { StatusIndicator } from './StatusIndicator'

interface AppBarProps {
  onMenuClick: () => void
  darkMode: boolean
  onToggleDark: () => void
}

export function AppBar({ onMenuClick, darkMode, onToggleDark }: AppBarProps) {
  return (
    <header
      className="flex items-center px-2 h-16 shrink-0 z-10"
      style={{
        background: 'var(--md-sys-color-surface-container)',
        borderBottom: '1px solid var(--md-sys-color-outline-variant)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
      }}
    >
      {/* Hamburger */}
      <button
        className="md3-icon-btn"
        onClick={onMenuClick}
        aria-label="Menu"
      >
        <span className="material-symbols-rounded" style={{ fontSize: 24 }}>menu</span>
      </button>

      {/* Ikona + tytuł */}
      <div className="flex items-center gap-2 ml-1 mr-auto">
        <span
          className="material-symbols-rounded filled"
          style={{ fontSize: 28, color: 'var(--md-sys-color-primary)' }}
        >
          door_front
        </span>
        <div>
          <p
            className="font-medium leading-tight"
            style={{
              fontSize: '1rem',
              color: 'var(--md-sys-color-on-surface)',
              letterSpacing: '0.01em',
            }}
          >
            Asystent Wad Produkcyjnych
          </p>
          <p style={{ fontSize: '0.7rem', color: 'var(--md-sys-color-on-surface-variant)' }}>
            RAG · Ollama · ChromaDB
          </p>
        </div>
      </div>

      {/* Status + licznik dokumentów */}
      <StatusIndicator />

      {/* Toggle motywu */}
      <button
        className="md3-icon-btn ml-1"
        onClick={onToggleDark}
        aria-label={darkMode ? 'Przełącz na jasny motyw' : 'Przełącz na ciemny motyw'}
        title={darkMode ? 'Motyw jasny' : 'Motyw ciemny'}
      >
        <span className="material-symbols-rounded" style={{ fontSize: 22 }}>
          {darkMode ? 'light_mode' : 'dark_mode'}
        </span>
      </button>
    </header>
  )
}
