# FireCrawl BrandingProfile Field Reference

Full schema for the `branding` object returned by FireCrawl's `/v1/scrape` endpoint with `formats: ["branding"]`.

Source: https://docs.firecrawl.dev/features/scrape#branding-profile-structure

---

## Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `colorScheme` | `"light"` \| `"dark"` | Detected color scheme of the site |
| `logo` | string (URL) | Primary logo URL |
| `colors` | object | Brand color palette |
| `fonts` | array | All font families detected on the page |
| `typography` | object | Detailed type system |
| `spacing` | object | Spacing and layout scale |
| `components` | object | UI component styles |
| `icons` | object | Icon style information |
| `images` | object | Brand images (logo, favicon, OG image) |
| `animations` | object | Animation and transition settings |
| `layout` | object | Layout configuration |
| `personality` | object | Brand personality traits |

---

## `colors` object

| Field | Description |
|-------|-------------|
| `primary` | Primary brand color (hex) |
| `secondary` | Secondary brand color (hex) |
| `accent` | Accent/highlight color (hex) |
| `background` | Page background color (hex) |
| `textPrimary` | Primary text color (hex) |
| `textSecondary` | Secondary/muted text color (hex) |
| `link` | Link color (hex) |
| `success` | Success state color (hex) |
| `warning` | Warning state color (hex) |
| `error` | Error state color (hex) |

---

## `typography` object

```json
{
  "fontFamilies": {
    "primary": "Inter",
    "heading": "Inter",
    "code": "Roboto Mono"
  },
  "fontSizes": {
    "h1": "48px",
    "h2": "36px",
    "h3": "24px",
    "h4": "20px",
    "body": "16px",
    "small": "14px"
  },
  "fontWeights": {
    "light": 300,
    "regular": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700
  },
  "lineHeights": {
    "heading": "1.2",
    "body": "1.6"
  }
}
```

---

## `spacing` object

```json
{
  "baseUnit": 8,
  "borderRadius": "8px",
  "padding": {
    "small": "8px",
    "medium": "16px",
    "large": "32px"
  },
  "margins": {
    "section": "64px",
    "element": "24px"
  }
}
```

---

## `components` object

```json
{
  "buttonPrimary": {
    "background": "#FF6B35",
    "textColor": "#FFFFFF",
    "borderRadius": "8px",
    "padding": "12px 24px",
    "fontSize": "16px",
    "fontWeight": 600
  },
  "buttonSecondary": {
    "background": "transparent",
    "textColor": "#FF6B35",
    "borderColor": "#FF6B35",
    "borderWidth": "1px",
    "borderRadius": "8px",
    "padding": "12px 24px"
  },
  "input": {
    "background": "#FFFFFF",
    "borderColor": "#D1D5DB",
    "borderRadius": "6px",
    "textColor": "#111827",
    "placeholderColor": "#9CA3AF"
  }
}
```

---

## `images` object

```json
{
  "logo": "https://example.com/logo.svg",
  "favicon": "https://example.com/favicon.ico",
  "ogImage": "https://example.com/og-image.png"
}
```

---

## `animations` object

```json
{
  "transitionDuration": "0.2s",
  "transitionEasing": "ease-in-out",
  "hoverScale": "1.02"
}
```

---

## `layout` object

```json
{
  "maxWidth": "1200px",
  "grid": "12-column",
  "headerHeight": "64px",
  "footerHeight": "200px"
}
```

---

## `personality` object

```json
{
  "tone": "professional",
  "energy": "calm",
  "targetAudience": "enterprise developers",
  "styleKeywords": ["minimal", "clean", "modern"]
}
```

---

## Note on null/missing fields

Not all fields will be populated for every site. Common gaps:
- Simple static sites may have sparse `typography` and no `components`
- Sites with CSS-in-JS may not expose readable custom properties
- `personality` is an AI inference and may be absent or generic

When `branding` data is sparse, supplement by using `formats: ["html"]` and parsing the raw `<style>` tags or CSS variables manually.
