'use client'

interface SnackbarProps {
  text: string
  type?: 'error' | 'success'
}

export function Snackbar({ text, type = 'success' }: SnackbarProps) {
  const isError = type === 'error'

  return (
    <div
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 snackbar-enter"
      role="status"
      aria-live="polite"
    >
      <div
        className="flex items-center gap-3 px-4 py-3 rounded-xl shadow-md3-3 max-w-sm"
        style={{
          background: isError
            ? 'var(--md-sys-color-error-container)'
            : 'var(--md-sys-color-inverse-surface)',
          color: isError
            ? 'var(--md-sys-color-on-error-container)'
            : 'var(--md-sys-color-inverse-on-surface)',
        }}
      >
        <span className="material-symbols-rounded filled" style={{ fontSize: 18 }}>
          {isError ? 'error' : 'check_circle'}
        </span>
        <p className="text-sm font-medium">{text}</p>
      </div>
    </div>
  )
}
