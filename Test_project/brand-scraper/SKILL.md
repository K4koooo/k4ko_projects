---
name: brand-scraper
description: Scrape any website to extract complete brand identity data using the FireCrawl API. Use this skill whenever the user wants to analyze an existing website's brand, pull colors/fonts/typography/design tokens for use in a new project, extract logos and hero images, understand UI styling patterns (buttons, spacing, animations), or build a brand style guide from a live site. Trigger this skill any time the user mentions: "scrape this site", "pull the brand from", "get the colors/fonts from", "analyze the design of", "I want to clone the look of", "extract branding from", or anything about capturing a website's visual identity to inform new design or development work.
---

# Brand Scraper

Extracts comprehensive brand identity, design tokens, imagery, and UI patterns from any live website using the FireCrawl API. The output is a structured brand report that can be directly used as a design reference when building a new website.

## What you extract

- **Colors**: Primary, secondary, accent, background, text, semantic (success/error/warning), dark/light scheme detection
- **Typography**: Font families (primary, heading, code), sizes (h1–body), weights, line heights
- **Logos & Brand Images**: Logo URL, favicon, OG image, any detected brand marks
- **Hero/Header Images**: Large visual images from above-the-fold sections
- **Interesting Images**: Product images, team photos, illustrations, background images worth referencing
- **UI Components**: Button styles (primary & secondary), input fields, border radii, shadows
- **Spacing & Layout**: Base spacing unit, padding/margin scale, grid configuration
- **Animations**: Transition speeds, easing functions, notable animation patterns
- **Brand Personality**: Tone, energy level, target audience (from FireCrawl's personality detection)

## Prerequisites

- FireCrawl API key stored as `FIRECRAWL_API_KEY` in `.env`
- Python 3.8+ with `firecrawl-py` and `python-dotenv` installed
- `pip install firecrawl-py python-dotenv requests`

---

## Step 1: Confirm the URL and scope

Ask the user:
1. What URL do you want to scrape? (e.g. `https://stripe.com`)
2. Do you want to scrape just the homepage, or also crawl a few additional pages (like `/about`, `/pricing`) to get a richer picture? (Default: homepage only — usually sufficient for brand extraction.)
3. Do you want to download the logo and hero images locally, or just capture their URLs?

If the user is in a hurry, just use the homepage and capture URLs only — that's the fast default.

---

## Step 2: Run the scraper script

Use `scripts/scrape_brand.py`. It calls FireCrawl with `formats=["branding", "images", "screenshot"]` combined, giving you branding data, all image URLs, and a full-page screenshot in one API call.

```bash
python brand-scraper/scripts/scrape_brand.py --url "https://example.com" --output ".tmp/brand_report/"
```

See `scripts/scrape_brand.py` for the full implementation. Key flags:
- `--url` — the target URL (required)
- `--output` — output directory (default: `.tmp/brand_report/`)
- `--download-images` — if passed, downloads logo + hero images locally into `output/images/`
- `--pages` — comma-separated additional paths to scrape (e.g. `--pages "/about,/pricing"`)

---

## Step 3: Interpret the results

After the script runs, read `brand_report.json` and `brand_report.md` from the output directory. Then present the findings to the user in a clear, useful way.

### How to read the branding output

FireCrawl returns a `BrandingProfile` object. Here's what each section means for web development:

**`colors`** — use these as CSS custom properties:
```css
:root {
  --color-primary: #FF6B35;
  --color-secondary: #004E89;
  --color-bg: #1A1A1A;
  --color-text: #FFFFFF;
}
```

**`typography`** — use to set up your font stack and type scale. If a Google Font is detected, it can be imported directly. If a custom/proprietary font appears, flag it to the user — they may need a licensed alternative.

**`components.buttonPrimary` / `buttonSecondary`** — gives you exact CSS to replicate button styles: background, text color, border, border-radius, padding.

**`spacing`** — the `baseUnit` (usually 4px or 8px) tells you the spacing grid. `borderRadius` tells you whether the site feels sharp (0–2px), modern (4–8px), or pill-like (20px+).

**`images`** — the `images` format returns all `<img>` src URLs from the page. Filter these:
- **Logo candidates**: small, square-ish or wide-aspect images near the top; often named `logo`, `brand`, or contain the company name
- **Hero/header images**: large images (look for wide dimensions or filenames like `hero`, `banner`, `header`, `background`)
- **OG image**: always grab `metadata.ogImage` — this is the brand's curated "face" image

**`personality`** — useful for writing copy or setting design tone. Note the energy level and target audience when reporting back.

**`animations`** — if the site uses `transition: all 0.2s ease`, replicate that timing. Subtle = professional; bouncy = playful.

---

## Step 4: Curate and filter images

Not all images returned by FireCrawl are useful. Apply this filter logic (the script does this automatically, but review the output):

1. **Skip**: tracking pixels (1×1), data URIs, icon sprites, ad network URLs
2. **Keep as "logo"**: images with `logo`, `brand`, `mark`, `wordmark` in their URL or alt text
3. **Keep as "hero"**: images with `hero`, `banner`, `header`, `cover`, `bg`, `background` in their URL; or images embedded in `<header>` or `<section>` tags near the top of the page
4. **Keep as "interesting"**: anything that's a JPEG/WebP/PNG and appears likely to be a photograph or illustration (not an icon)
5. **Note expiry**: FireCrawl screenshot URLs expire after **24 hours** — tell the user if they want to preserve them

---

## Step 5: Generate the brand report

The script auto-generates two files:

**`brand_report.json`** — machine-readable, structured output (suitable for piping into other tools or templates)

**`brand_report.md`** — human-readable Markdown report. Structure:

```
# Brand Report: [Site Name]
Scraped: [URL] on [date]

## Color Palette
[Swatches as hex values with CSS variable names]

## Typography
[Font families, sizes, weights]

## Logo & Brand Images
[URLs or local paths]

## Hero / Header Images
[URLs or local paths]

## Other Notable Images
[Curated list]

## UI Components
[Button styles, input styles, border radius, shadow]

## Spacing & Layout
[Base unit, grid, breakpoints if detectable]

## Animations & Transitions
[Timing, easing]

## Brand Personality
[Tone, energy, audience]

## Notes for Development
[Any flags: proprietary fonts, complex animations, things to watch out for]
```

Present this report to the user and walk them through the most important findings. Highlight anything unusual or that will require special attention (licensed fonts, complex CSS effects, etc.).

---

## Step 6: Handle edge cases

**Site blocks scrapers**: Some sites use aggressive bot detection. If FireCrawl returns an error or empty branding data, try:
1. Adding `--enhanced` flag (uses FireCrawl's enhanced mode with proxy rotation)
2. Suggesting the user provides a specific sub-page URL that's less protected
3. Falling back to `formats=["html", "screenshot"]` and doing manual extraction from the HTML

**Branding data is sparse**: If `branding` fields are mostly null (common on very simple or very custom sites), supplement with:
- Parse the raw HTML for `<style>` tags and CSS variables
- Use the `screenshot` format to visually inspect the page and note colors/fonts manually
- Extract `metadata.ogImage`, `metadata.title`, and `metadata.description` as a minimum viable brand package

**Multiple pages**: If the user wants cross-page scraping, run the script once per page with `--output .tmp/brand_report_<pagename>/` and then merge: take the union of images, and use the homepage branding data as canonical (supplemented with anything unique from sub-pages).

**Image URLs behind auth or CDN**: Some image URLs require cookies or auth headers to load. Flag these to the user — they'll need to manually download them from a logged-in browser session.

---

## Reference files

- `scripts/scrape_brand.py` — the main execution script
- `references/firecrawl_branding_schema.md` — full BrandingProfile field reference
