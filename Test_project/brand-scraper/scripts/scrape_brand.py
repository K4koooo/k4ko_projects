"""
scrape_brand.py
---------------
Calls the FireCrawl API to extract comprehensive brand identity data from a website.
Outputs brand_report.json and brand_report.md to the specified output directory.

Usage:
    python brand-scraper/scripts/scrape_brand.py --url "https://example.com" --output ".tmp/brand_report/"
    python brand-scraper/scripts/scrape_brand.py --url "https://stripe.com" --output ".tmp/stripe/" --download-images
    python brand-scraper/scripts/scrape_brand.py --url "https://airbnb.com" --output ".tmp/airbnb/" --pages "/about,/help"
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# ---------------------------------------------------------------------------
# FireCrawl API helpers
# ---------------------------------------------------------------------------

FIRECRAWL_API_BASE = "https://api.firecrawl.dev/v1"


def get_api_key() -> str:
    """Read FIRECRAWL_API_KEY from environment."""
    key = os.getenv("FIRECRAWL_API_KEY")
    if not key:
        print(
            "ERROR: FIRECRAWL_API_KEY not set. Add it to your .env file:\n"
            "  FIRECRAWL_API_KEY=fc-YOUR-KEY-HERE",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def scrape_url(url: str, api_key: str, enhanced: bool = False) -> dict:
    """
    Call the /v1/scrape endpoint with branding + images + screenshot formats.
    Returns the parsed JSON response data dict.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "url": url,
        "formats": ["branding", "images", "screenshot", "markdown"],
        "onlyMainContent": False,
        "timeout": 60000,  # 60 seconds
    }

    if enhanced:
        payload["enhancedMode"] = True

    print(f"  → Scraping {url} ...", flush=True)
    response = requests.post(
        f"{FIRECRAWL_API_BASE}/scrape",
        headers=headers,
        json=payload,
        timeout=90,
    )

    if response.status_code != 200:
        print(
            f"  ERROR: FireCrawl returned HTTP {response.status_code}\n"
            f"  Response: {response.text[:500]}",
            file=sys.stderr,
        )
        return {}

    data = response.json()
    if not data.get("success"):
        print(
            f"  ERROR: FireCrawl reported failure: {data.get('error', 'unknown')}",
            file=sys.stderr,
        )
        return {}

    return data.get("data", {})


# ---------------------------------------------------------------------------
# Image classification helpers
# ---------------------------------------------------------------------------

LOGO_KEYWORDS = re.compile(
    r"logo|brand|mark|wordmark|icon|emblem|symbol", re.IGNORECASE
)
HERO_KEYWORDS = re.compile(
    r"hero|banner|header|cover|bg|background|splash|jumbotron|keyvisual",
    re.IGNORECASE,
)
SKIP_PATTERNS = re.compile(
    r"tracking|pixel|beacon|analytics|ad\.|ads\.|\.gif$|data:image|1x1|spacer",
    re.IGNORECASE,
)
IMAGE_EXTENSIONS = re.compile(
    r"\.(jpg|jpeg|png|webp|svg|avif)(\?|$)", re.IGNORECASE
)


def classify_image(url: str) -> str | None:
    """
    Returns one of: 'logo', 'hero', 'interesting', or None (skip).
    """
    if SKIP_PATTERNS.search(url):
        return None
    if not IMAGE_EXTENSIONS.search(url):
        return None  # not a recognizable image format

    path = urlparse(url).path.lower()
    filename = Path(path).name

    if LOGO_KEYWORDS.search(filename) or LOGO_KEYWORDS.search(path):
        return "logo"
    if HERO_KEYWORDS.search(filename) or HERO_KEYWORDS.search(path):
        return "hero"
    # Rough heuristic: SVGs are often icons/logos, PNGs/JPEGs/WebPs are content
    if path.endswith(".svg"):
        return "logo"  # SVGs at unclassified paths are likely icons or logos
    return "interesting"


def classify_all_images(raw_images: list[str], branding: dict) -> dict:
    """
    Categorize all images into logos, heroes, and interesting.
    Also injects known brand images from the branding profile.
    """
    logos = []
    heroes = []
    interesting = []
    seen = set()

    # First: inject branding-detected images (highest confidence)
    brand_imgs = branding.get("images", {}) or {}
    for key in ("logo", "favicon", "ogImage"):
        img_url = brand_imgs.get(key)
        if img_url and img_url not in seen:
            seen.add(img_url)
            if key == "logo":
                logos.append({"url": img_url, "source": "branding.images.logo"})
            elif key == "favicon":
                logos.append({"url": img_url, "source": "branding.images.favicon"})
            else:
                interesting.append({"url": img_url, "source": "branding.images.ogImage"})

    # Also check branding.logo top-level field
    top_logo = branding.get("logo")
    if top_logo and top_logo not in seen:
        seen.add(top_logo)
        logos.append({"url": top_logo, "source": "branding.logo"})

    # Process all page images
    for url in raw_images or []:
        if url in seen:
            continue
        seen.add(url)
        category = classify_image(url)
        if category == "logo":
            logos.append({"url": url, "source": "page"})
        elif category == "hero":
            heroes.append({"url": url, "source": "page"})
        elif category == "interesting":
            interesting.append({"url": url, "source": "page"})

    return {"logos": logos, "heroes": heroes, "interesting": interesting}


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(url: str, pages_data: list[dict]) -> dict:
    """
    Merge data from one or more scraped pages into a unified brand report.
    The first page (homepage) is authoritative for branding data.
    """
    primary = pages_data[0] if pages_data else {}
    branding = primary.get("branding") or {}
    metadata = primary.get("metadata") or {}

    # Aggregate images from all pages
    all_raw_images = []
    for page in pages_data:
        all_raw_images.extend(page.get("images") or [])

    classified = classify_all_images(all_raw_images, branding)

    # Pull screenshot from primary page
    screenshot_url = primary.get("screenshot")

    return {
        "url": url,
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "site_name": metadata.get("ogSiteName") or metadata.get("title", "Unknown"),
        "site_description": metadata.get("description") or metadata.get("ogDescription", ""),
        "branding": branding,
        "images": classified,
        "screenshot": screenshot_url,
        "metadata": metadata,
    }


def render_markdown_report(report: dict) -> str:
    """
    Render the brand report as a human-readable Markdown document.
    """
    b = report.get("branding", {}) or {}
    colors = b.get("colors", {}) or {}
    fonts = b.get("fonts", []) or []
    typography = b.get("typography", {}) or {}
    spacing = b.get("spacing", {}) or {}
    components = b.get("components", {}) or {}
    animations = b.get("animations", {}) or {}
    personality = b.get("personality", {}) or {}
    images = report.get("images", {})

    font_families = typography.get("fontFamilies", {}) or {}
    font_sizes = typography.get("fontSizes", {}) or {}
    font_weights = typography.get("fontWeights", {}) or {}
    line_heights = typography.get("lineHeights", {}) or {}

    lines = []
    lines.append(f"# Brand Report: {report.get('site_name', 'Unknown')}")
    lines.append(f"\n**URL:** {report.get('url')}  ")
    lines.append(f"**Scraped:** {report.get('scraped_at')}  ")
    lines.append(f"**Color Scheme:** {b.get('colorScheme', 'unknown')}  ")
    if report.get("site_description"):
        lines.append(f"**Description:** {report['site_description']}")

    # --- Color Palette ---
    lines.append("\n---\n\n## 🎨 Color Palette\n")
    if colors:
        lines.append("| Role | Hex Value | CSS Variable |")
        lines.append("|------|-----------|--------------|")
        for role, hex_val in colors.items():
            if hex_val:
                css_var = f"--color-{re.sub(r'([A-Z])', r'-\\1', role).lower().strip('-')}"
                lines.append(f"| {role} | `{hex_val}` | `{css_var}` |")
        lines.append("\n**Suggested CSS Custom Properties:**")
        lines.append("```css\n:root {")
        for role, hex_val in colors.items():
            if hex_val:
                css_var = f"--color-{re.sub(r'([A-Z])', r'-\\1', role).lower().strip('-')}"
                lines.append(f"  {css_var}: {hex_val};")
        lines.append("}\n```")
    else:
        lines.append("_No color data extracted._")

    # --- Typography ---
    lines.append("\n---\n\n## 🔤 Typography\n")
    if font_families:
        lines.append(f"- **Primary font:** `{font_families.get('primary', 'N/A')}`")
        lines.append(f"- **Heading font:** `{font_families.get('heading', 'N/A')}`")
        lines.append(f"- **Code/mono font:** `{font_families.get('code', 'N/A')}`")
    if fonts:
        all_families = ", ".join(f"`{f.get('family', f)}`" if isinstance(f, dict) else f"`{f}`" for f in fonts)
        lines.append(f"- **All detected fonts:** {all_families}")
    if font_sizes:
        lines.append("\n**Font Sizes:**")
        for name, size in font_sizes.items():
            lines.append(f"  - `{name}`: {size}")
    if font_weights:
        lines.append("\n**Font Weights:**")
        for name, weight in font_weights.items():
            lines.append(f"  - `{name}`: {weight}")
    if line_heights:
        lines.append("\n**Line Heights:**")
        for name, lh in line_heights.items():
            lines.append(f"  - `{name}`: {lh}")
    if not (font_families or fonts):
        lines.append("_No typography data extracted._")

    # --- Logos & Brand Images ---
    lines.append("\n---\n\n## 🖼️ Logos & Brand Images\n")
    logos = images.get("logos", [])
    if logos:
        for img in logos:
            lines.append(f"- [{img['url']}]({img['url']}) _(source: {img['source']})_")
    else:
        lines.append("_No logos detected._")

    # --- Hero / Header Images ---
    lines.append("\n---\n\n## 🦸 Hero / Header Images\n")
    heroes = images.get("heroes", [])
    if heroes:
        for img in heroes:
            lines.append(f"- [{img['url']}]({img['url']})")
    else:
        lines.append("_No hero images detected._")

    # --- Other Notable Images ---
    lines.append("\n---\n\n## 📸 Other Notable Images\n")
    interesting = images.get("interesting", [])
    if interesting:
        for img in interesting[:20]:  # Cap at 20 to keep report readable
            lines.append(f"- [{img['url']}]({img['url']})")
        if len(interesting) > 20:
            lines.append(f"\n_(+ {len(interesting) - 20} more — see brand_report.json for full list)_")
    else:
        lines.append("_No additional images found._")

    # --- UI Components ---
    lines.append("\n---\n\n## 🧩 UI Components\n")
    if components:
        btn_primary = components.get("buttonPrimary", {}) or {}
        btn_secondary = components.get("buttonSecondary", {}) or {}
        inp = components.get("input", {}) or {}

        if btn_primary:
            lines.append("**Primary Button:**")
            lines.append("```css\n.btn-primary {")
            for k, v in btn_primary.items():
                css_prop = re.sub(r'([A-Z])', r'-\1', k).lower()
                lines.append(f"  {css_prop}: {v};")
            lines.append("}\n```")

        if btn_secondary:
            lines.append("**Secondary Button:**")
            lines.append("```css\n.btn-secondary {")
            for k, v in btn_secondary.items():
                css_prop = re.sub(r'([A-Z])', r'-\1', k).lower()
                lines.append(f"  {css_prop}: {v};")
            lines.append("}\n```")

        if inp:
            lines.append("**Input Field:**")
            lines.append("```css\ninput {")
            for k, v in inp.items():
                css_prop = re.sub(r'([A-Z])', r'-\1', k).lower()
                lines.append(f"  {css_prop}: {v};")
            lines.append("}\n```")
    else:
        lines.append("_No component data extracted._")

    # --- Spacing & Layout ---
    lines.append("\n---\n\n## 📐 Spacing & Layout\n")
    if spacing:
        for k, v in spacing.items():
            lines.append(f"- **{k}:** `{v}`")
    else:
        lines.append("_No spacing data extracted._")

    # --- Animations & Transitions ---
    lines.append("\n---\n\n## ✨ Animations & Transitions\n")
    if animations:
        for k, v in animations.items():
            lines.append(f"- **{k}:** `{v}`")
    else:
        lines.append("_No animation data extracted._")

    # --- Brand Personality ---
    lines.append("\n---\n\n## 🧠 Brand Personality\n")
    if personality:
        for k, v in personality.items():
            lines.append(f"- **{k}:** {v}")
    else:
        lines.append("_No personality data extracted._")

    # --- Screenshot ---
    lines.append("\n---\n\n## 📷 Screenshot\n")
    screenshot = report.get("screenshot")
    if screenshot:
        lines.append(f"[View full-page screenshot]({screenshot})")
        lines.append("\n> ⚠️ FireCrawl screenshot URLs expire after 24 hours.")
    else:
        lines.append("_No screenshot captured._")

    # --- Dev Notes ---
    lines.append("\n---\n\n## 🛠️ Notes for Development\n")
    notes = []

    # Flag proprietary/non-Google fonts
    all_font_names = []
    for f in fonts:
        if isinstance(f, dict):
            all_font_names.append(f.get("family", ""))
        else:
            all_font_names.append(str(f))
    for name in [font_families.get("primary"), font_families.get("heading"), font_families.get("code")]:
        if name and name not in all_font_names:
            all_font_names.append(name)

    google_fonts_common = {
        "inter", "roboto", "open sans", "lato", "montserrat", "poppins",
        "raleway", "nunito", "ubuntu", "source sans", "playfair display",
        "merriweather", "pt sans", "josefin sans", "outfit", "dm sans",
        "manrope", "figtree", "geist", "roboto mono", "fira code", "space mono",
    }
    for fname in all_font_names:
        if fname and fname.lower() not in google_fonts_common:
            notes.append(f"⚠️ **`{fname}`** may be a custom/proprietary font — verify license before using. Consider a Google Fonts alternative if needed.")

    if not notes:
        notes.append("✅ No major issues detected. All fonts appear to be standard web fonts.")

    lines.extend(notes)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Image downloader
# ---------------------------------------------------------------------------

def download_images(images: dict, output_dir: Path, api_key: str):
    """Download logo and hero images to output_dir/images/."""
    img_dir = output_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    to_download = []
    for img in images.get("logos", []):
        to_download.append(("logo", img["url"]))
    for img in images.get("heroes", []):
        to_download.append(("hero", img["url"]))

    if not to_download:
        print("  No logo/hero images to download.")
        return

    for category, url in to_download:
        try:
            ext = Path(urlparse(url).path).suffix or ".png"
            filename = f"{category}_{abs(hash(url)) % 10000:04d}{ext}"
            dest = img_dir / filename
            print(f"  Downloading {category}: {url[:80]}...")
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            print(f"    → Saved to {dest}")
        except Exception as e:
            print(f"  WARNING: Could not download {url}: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scrape brand identity from a website using FireCrawl API."
    )
    parser.add_argument("--url", required=True, help="Target URL to scrape")
    parser.add_argument(
        "--output",
        default=".tmp/brand_report/",
        help="Output directory for report files (default: .tmp/brand_report/)",
    )
    parser.add_argument(
        "--download-images",
        action="store_true",
        help="Download logo and hero images locally",
    )
    parser.add_argument(
        "--pages",
        default="",
        help="Comma-separated additional paths to scrape (e.g. /about,/pricing)",
    )
    parser.add_argument(
        "--enhanced",
        action="store_true",
        help="Use FireCrawl enhanced mode (proxy rotation, better JS rendering)",
    )
    args = parser.parse_args()

    api_key = get_api_key()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine all URLs to scrape
    base_url = args.url.rstrip("/")
    urls_to_scrape = [base_url]
    if args.pages:
        for path in args.pages.split(","):
            path = path.strip()
            if path:
                full_url = urljoin(base_url + "/", path.lstrip("/"))
                urls_to_scrape.append(full_url)

    print(f"\n🔍 Scraping {len(urls_to_scrape)} page(s) for brand data...\n")

    pages_data = []
    for url in urls_to_scrape:
        data = scrape_url(url, api_key, enhanced=args.enhanced)
        if data:
            pages_data.append(data)
        else:
            print(f"  WARNING: Got no data from {url}", file=sys.stderr)

    if not pages_data:
        print("ERROR: No data was retrieved. Check your API key and URL.", file=sys.stderr)
        sys.exit(1)

    print(f"\n✅ Successfully scraped {len(pages_data)} page(s).\n")

    # Build unified report
    report = build_report(args.url, pages_data)

    # Save JSON report
    json_path = output_dir / "brand_report.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"📄 JSON report saved to: {json_path}")

    # Save Markdown report
    md_content = render_markdown_report(report)
    md_path = output_dir / "brand_report.md"
    md_path.write_text(md_content, encoding="utf-8")
    print(f"📝 Markdown report saved to: {md_path}")

    # Optionally download images
    if args.download_images:
        print("\n📥 Downloading logo and hero images...")
        download_images(report["images"], output_dir, api_key)

    # Print summary
    b = report.get("branding", {}) or {}
    colors = b.get("colors", {}) or {}
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Brand Extraction Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Site:         {report.get('site_name')}
Color scheme: {b.get('colorScheme', 'unknown')}
Colors found: {len([v for v in colors.values() if v])}
Logos found:  {len(report['images']['logos'])}
Hero images:  {len(report['images']['heroes'])}
Other images: {len(report['images']['interesting'])}
Screenshot:   {'Yes (expires in 24h)' if report.get('screenshot') else 'No'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reports:
  {json_path}
  {md_path}
""")


if __name__ == "__main__":
    main()
