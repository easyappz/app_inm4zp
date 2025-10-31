import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT_SECONDS = 10


def _extract_meta_content(html: str, key: str) -> Optional[str]:
    """
    Extract content from meta tags by property or name.
    Looks for both: property="key" and name="key".
    """
    patterns = [
        rf"<meta[^>]+property=[\"']{re.escape(key)}[\"'][^>]*content=[\"'](.*?)[\"']",
        rf"<meta[^>]+name=[\"']{re.escape(key)}[\"'][^>]*content=[\"'](.*?)[\"']",
    ]
    for pat in patterns:
        m = re.search(pat, html, flags=re.IGNORECASE | re.DOTALL)
        if m:
            return _clean_html_text(m.group(1))
    return None


def _extract_tag_text(html: str, tag: str) -> Optional[str]:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    return _clean_html_text(m.group(1))


def _clean_html_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    # Remove tags and compress whitespace
    text = re.sub(r"<[^>]+>", " ", value)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _extract_description(html: str) -> Optional[str]:
    # Try common meta tags
    desc = _extract_meta_content(html, "og:description")
    if desc:
        return desc
    desc = _extract_meta_content(html, "description")
    if desc:
        return desc
    # Heuristic: itemprop="description" blocks
    m = re.search(r"<[^>]+itemprop=\"description\"[^>]*>(.*?)</", html, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return _clean_html_text(m.group(1))
    return None


def _extract_price(html: str) -> Optional[Decimal]:
    """
    Extract price as Decimal from typical patterns.
    Heuristics:
    - Look near currency symbols like ₽, RUB
    - Fallback to prominent number blocks (with spaces)
    """
    # Try meta price
    meta_price = _extract_meta_content(html, "product:price:amount") or _extract_meta_content(html, "price")
    if meta_price:
        parsed = _parse_decimal(meta_price)
        if parsed is not None:
            return parsed

    # Search for number followed by ₽ or RUB
    patterns = [
        r"([\d\s\u00A0]+)\s*[₽\u20BD]",
        r"([\d\s\u00A0]+)\s*(?:RUB|rub)",
    ]
    for pat in patterns:
        m = re.search(pat, html, flags=re.IGNORECASE)
        if m:
            parsed = _parse_decimal(m.group(1))
            if parsed is not None:
                return parsed

    # Fallback: first long-ish number
    m = re.search(r"([\d\s\u00A0]{4,})", html)
    if m:
        parsed = _parse_decimal(m.group(1))
        if parsed is not None:
            return parsed

    return None


def _parse_decimal(text: str) -> Optional[Decimal]:
    # Keep digits only for integers; Avito prices are usually integers
    digits = re.sub(r"[^0-9]", "", text or "")
    if not digits:
        return None
    try:
        return Decimal(digits)
    except (InvalidOperation, ValueError):
        return None


def _extract_image(html: str) -> Optional[str]:
    # Prefer Open Graph image
    og = _extract_meta_content(html, "og:image")
    if og:
        return og
    # Heuristic: data- attributes or img with main in class
    m = re.search(r"<img[^>]+(?:data-image|data-url|src)=\"(.*?)\"[^>]*>", html, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def fetch_avito_data(url: str) -> Dict[str, Optional[object]]:
    """
    Fetch listing data from a URL and extract basic fields.
    Notes:
    - URL must start with http/https. Domain does not have to be avito.ru (kept flexible for future sources).
    - Uses urllib (no external deps). Timeout is 10 seconds.
    - Extraction uses simple heuristics (OG meta tags, <title>, regex patterns).
    - Returns None/empty values when specific fields are not found.

    Returns dict with keys: title, image_url, price (Decimal|None), description.
    Raises URLError/HTTPError for network issues which caller should handle.
    """
    if not isinstance(url, str) or not re.match(r"^https?://", url.strip(), flags=re.IGNORECASE):
        raise ValueError("Invalid URL: must start with http or https")

    # Domain check intentionally permissive: allow non-avito domains for future extensibility.

    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})

    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            # Determine encoding
            try:
                encoding = resp.headers.get_content_charset() or "utf-8"
            except Exception:
                encoding = "utf-8"
            raw = resp.read()
            html = raw.decode(encoding, errors="ignore")
    except (HTTPError, URLError) as e:
        # Propagate to caller to decide status code mapping
        raise e

    title = _extract_meta_content(html, "og:title") or _extract_tag_text(html, "title")
    image_url = _extract_image(html)
    price = _extract_price(html)
    description = _extract_description(html)

    return {
        "title": title,
        "image_url": image_url,
        "price": price,
        "description": description,
    }
