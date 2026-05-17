'use client'

export function LoadingDots() {
  return (
    <div className="flex items-center gap-1 px-1" aria-label="Generowanie odpowiedzi...">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="block rounded-full animate-dot-bounce"
          style={{
            width: 8,
            height: 8,
            background: 'var(--md-sys-color-on-surface-variant)',
            animationDelay: `${i * 0.16}s`,
          }}
        />
      ))}
    </div>
  )
}
