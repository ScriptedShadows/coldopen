"""Fetch a prospect's website and distill it into a compact research packet.

Homepage only (plus /about when discoverable) — enough signal for positioning,
terminology, and tone without a full crawl. Degrades gracefully: any page that
fails just contributes nothing.
"""

import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 ColdOpen/0.1"
)

MAX_TEXT_CHARS = 6000


class ScrapeError(Exception):
    pass


@dataclass
class ScrapedSite:
    url: str
    domain: str
    title: str = ""
    description: str = ""
    site_name: str = ""
    theme_color: str = ""
    headings: list[str] = field(default_factory=list)
    nav_links: list[str] = field(default_factory=list)
    text: str = ""

    def as_prompt_block(self) -> str:
        parts = [
            f"URL: {self.url}",
            f"Domain: {self.domain}",
            f"<title>: {self.title}",
            f"Meta description: {self.description or '(none)'}",
            f"Site name: {self.site_name or '(none)'}",
            f"Declared theme color: {self.theme_color or '(none)'}",
            "Headings: " + " | ".join(self.headings[:25]),
            "Nav links: " + " | ".join(self.nav_links[:20]),
            "Visible text (truncated):",
            self.text[:MAX_TEXT_CHARS],
        ]
        return "\n".join(parts)


def _normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not re.match(r"^https?://", raw):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if not parsed.netloc or "." not in parsed.netloc:
        raise ScrapeError(f"'{raw}' does not look like a company URL.")
    return raw


def _visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()


def scrape_site(raw_url: str) -> ScrapedSite:
    url = _normalize_url(raw_url)
    with httpx.Client(
        follow_redirects=True, timeout=20, headers={"User-Agent": UA}
    ) as client:
        try:
            resp = client.get(url)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise ScrapeError(f"Could not reach {url}: {exc}") from exc

        soup = BeautifulSoup(resp.text, "html.parser")
        final_url = str(resp.url)
        site = ScrapedSite(url=final_url, domain=urlparse(final_url).netloc.removeprefix("www."))

        site.title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""

        def meta(**attrs) -> str:
            tag = soup.find("meta", attrs=attrs)
            return (tag.get("content") or "").strip() if tag else ""

        site.description = meta(name="description") or meta(property="og:description")
        site.site_name = meta(property="og:site_name")
        site.theme_color = meta(name="theme-color")

        site.headings = [
            h.get_text(" ", strip=True)
            for h in soup.find_all(["h1", "h2", "h3"], limit=30)
            if h.get_text(strip=True)
        ]
        nav = soup.find("nav") or soup.find("header")
        if nav:
            site.nav_links = [
                a.get_text(" ", strip=True) for a in nav.find_all("a") if a.get_text(strip=True)
            ][:20]

        site.text = _visible_text(soup)

        # One optional extra page: an /about-ish link, for tone and history.
        about_href = None
        for a in soup.find_all("a", href=True):
            label = (a.get_text(" ", strip=True) or "").lower()
            if re.search(r"\babout\b|\bcompany\b|\bwho we are\b", label):
                about_href = urljoin(final_url, a["href"])
                break
        if about_href and urlparse(about_href).netloc == urlparse(final_url).netloc:
            try:
                about = client.get(about_href)
                about.raise_for_status()
                about_soup = BeautifulSoup(about.text, "html.parser")
                site.text = (site.text + " \n[ABOUT PAGE] " + _visible_text(about_soup))[
                    : MAX_TEXT_CHARS * 2
                ]
            except httpx.HTTPError:
                pass

        if len(site.text) < 200 and not site.headings:
            raise ScrapeError(
                f"{site.domain} returned almost no readable content (likely fully JS-rendered "
                "or bot-blocked). Try another company URL."
            )
        return site
