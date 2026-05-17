'use client'

// MD3 kolor tonalny wygenerowany z seed #0B57D0 (Google Blue)
// Wartości zgodne z Material Color Utilities

const lightTokens: Record<string, string> = {
  '--md-sys-color-primary': '#0B57D0',
  '--md-sys-color-on-primary': '#FFFFFF',
  '--md-sys-color-primary-container': '#D3E3FD',
  '--md-sys-color-on-primary-container': '#041E49',
  '--md-sys-color-secondary': '#595F72',
  '--md-sys-color-on-secondary': '#FFFFFF',
  '--md-sys-color-secondary-container': '#DDE2F9',
  '--md-sys-color-on-secondary-container': '#161C2C',
  '--md-sys-color-tertiary': '#735472',
  '--md-sys-color-on-tertiary': '#FFFFFF',
  '--md-sys-color-tertiary-container': '#FFD6FA',
  '--md-sys-color-on-tertiary-container': '#2A112A',
  '--md-sys-color-error': '#B3261E',
  '--md-sys-color-on-error': '#FFFFFF',
  '--md-sys-color-error-container': '#F9DEDC',
  '--md-sys-color-on-error-container': '#410E0B',
  '--md-sys-color-background': '#FAFBFF',
  '--md-sys-color-on-background': '#1A1B1F',
  '--md-sys-color-surface': '#FAFBFF',
  '--md-sys-color-on-surface': '#1A1B1F',
  '--md-sys-color-surface-variant': '#E1E2EC',
  '--md-sys-color-on-surface-variant': '#44464F',
  '--md-sys-color-outline': '#74777F',
  '--md-sys-color-outline-variant': '#C4C6D0',
  '--md-sys-color-shadow': '#000000',
  '--md-sys-color-scrim': '#000000',
  '--md-sys-color-inverse-surface': '#2F3038',
  '--md-sys-color-inverse-on-surface': '#F2F0F4',
  '--md-sys-color-inverse-primary': '#A8C7FA',
  '--md-sys-color-surface-dim': '#DAD9E0',
  '--md-sys-color-surface-bright': '#FAFBFF',
  '--md-sys-color-surface-container-lowest': '#FFFFFF',
  '--md-sys-color-surface-container-low': '#F4F3FA',
  '--md-sys-color-surface-container': '#EEEFF6',
  '--md-sys-color-surface-container-high': '#E8E8EF',
  '--md-sys-color-surface-container-highest': '#E3E3EA',
}

const darkTokens: Record<string, string> = {
  '--md-sys-color-primary': '#A8C7FA',
  '--md-sys-color-on-primary': '#002F6C',
  '--md-sys-color-primary-container': '#0844A4',
  '--md-sys-color-on-primary-container': '#D3E3FD',
  '--md-sys-color-secondary': '#BBC3DB',
  '--md-sys-color-on-secondary': '#253042',
  '--md-sys-color-secondary-container': '#3C4759',
  '--md-sys-color-on-secondary-container': '#DDE2F9',
  '--md-sys-color-tertiary': '#E9B9E7',
  '--md-sys-color-on-tertiary': '#422741',
  '--md-sys-color-tertiary-container': '#5A3D59',
  '--md-sys-color-on-tertiary-container': '#FFD6FA',
  '--md-sys-color-error': '#F2B8B5',
  '--md-sys-color-on-error': '#601410',
  '--md-sys-color-error-container': '#8C1D18',
  '--md-sys-color-on-error-container': '#F9DEDC',
  '--md-sys-color-background': '#111318',
  '--md-sys-color-on-background': '#E3E2E6',
  '--md-sys-color-surface': '#111318',
  '--md-sys-color-on-surface': '#E3E2E6',
  '--md-sys-color-surface-variant': '#44464F',
  '--md-sys-color-on-surface-variant': '#C4C6D0',
  '--md-sys-color-outline': '#8E9099',
  '--md-sys-color-outline-variant': '#44464F',
  '--md-sys-color-shadow': '#000000',
  '--md-sys-color-scrim': '#000000',
  '--md-sys-color-inverse-surface': '#E3E3EA',
  '--md-sys-color-inverse-on-surface': '#2F3038',
  '--md-sys-color-inverse-primary': '#0B57D0',
  '--md-sys-color-surface-dim': '#111318',
  '--md-sys-color-surface-bright': '#37393E',
  '--md-sys-color-surface-container-lowest': '#0C0E13',
  '--md-sys-color-surface-container-low': '#1A1B20',
  '--md-sys-color-surface-container': '#1E1F25',
  '--md-sys-color-surface-container-high': '#282A2F',
  '--md-sys-color-surface-container-highest': '#33353B',
}

export function applyTheme(dark: boolean) {
  const tokens = dark ? darkTokens : lightTokens
  const root = document.documentElement
  root.setAttribute('data-theme', dark ? 'dark' : 'light')
  Object.entries(tokens).forEach(([key, value]) => {
    root.style.setProperty(key, value)
  })
}

export function getSystemPrefersDark(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

export { lightTokens, darkTokens }
