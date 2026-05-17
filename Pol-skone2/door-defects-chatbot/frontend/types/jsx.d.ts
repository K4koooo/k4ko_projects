import React from 'react'

type MDBase = React.HTMLAttributes<HTMLElement> & {
  class?: string
}

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'md-filled-button': MDBase & { disabled?: boolean; 'trailing-icon'?: boolean }
      'md-outlined-button': MDBase & { disabled?: boolean }
      'md-text-button': MDBase & { disabled?: boolean }
      'md-tonal-button': MDBase & { disabled?: boolean }
      'md-elevated-button': MDBase & { disabled?: boolean }
      'md-icon-button': MDBase & { disabled?: boolean; selected?: boolean; toggle?: boolean }
      'md-filled-icon-button': MDBase & { disabled?: boolean }
      'md-tonal-icon-button': MDBase & { disabled?: boolean }
      'md-outlined-icon-button': MDBase & { disabled?: boolean; selected?: boolean; toggle?: boolean }
      'md-outlined-text-field': MDBase & {
        label?: string
        value?: string
        disabled?: boolean
        type?: string
        placeholder?: string
        rows?: number
        cols?: number
        maxlength?: number
        'supporting-text'?: string
        error?: boolean
        'error-text'?: string
        autocomplete?: string
      }
      'md-filled-text-field': MDBase & {
        label?: string
        value?: string
        disabled?: boolean
        type?: string
        rows?: number
        maxlength?: number
      }
      'md-assist-chip': MDBase & {
        label?: string
        disabled?: boolean
        elevated?: boolean
      }
      'md-filter-chip': MDBase & {
        label?: string
        selected?: boolean
        disabled?: boolean
      }
      'md-chip-set': MDBase
      'md-circular-progress': MDBase & {
        indeterminate?: boolean
        value?: number
        max?: number
      }
      'md-linear-progress': MDBase & {
        indeterminate?: boolean
        value?: number
        max?: number
        buffer?: number
      }
      'md-switch': MDBase & { selected?: boolean; disabled?: boolean }
      'md-divider': MDBase & { inset?: boolean; 'inset-start'?: boolean; 'inset-end'?: boolean }
      'md-list': MDBase
      'md-list-item': MDBase & {
        headline?: string
        'supporting-text'?: string
        disabled?: boolean
        type?: string
        href?: string
      }
      'md-icon': MDBase
      'md-ripple': MDBase
      'md-focus-ring': MDBase
      'md-elevation': MDBase
      'md-badge': MDBase & { value?: string | number }
    }
  }
}

export {}
