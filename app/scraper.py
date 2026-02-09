import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag

from app.config import settings


@dataclass
class ScrapeResult:
    
    # Ergebnis des Scrapings - Fokus die Hauptseite der URL von SCHUNK
    name: str
    url: str
    sections: Dict[str, str]


def _clean_text(text: str) -> str:
    # Normalisiert Whitespace und entfernt führende/abschließende Leerzeichen
    return re.sub(r"\s+", " ", text or "").strip()


def _remove_noise(root: Tag) -> None:
    # Entfernt typische Layout-/Skript-Elemente, damit nur Content übrig bleibt
    for selector in [
        "script",
        "style",
        "noscript",
        "header",
        "footer",
        "nav",
        "aside",
        "form",
        "svg",
    ]:
        for el in root.select(selector):
            el.decompose()

    # Cookie-/Consent-Overlays (häufige Klassen/Rollen)
    for el in root.select('[role="dialog"], .cookie, .cookies, .cookie-banner, .consent'):
        try:
            el.decompose()
        except Exception:
            pass


def _pick_main_container(soup: BeautifulSoup) -> Tag:
    # Wählt den Container aus, der am ehesten den Hauptinhalt enthält
    for sel in [
        "main",
        "#content",
        "article",
        "[data-testid='content']",
        "[role='main']",
    ]:
        node = soup.select_one(sel)
        if isinstance(node, Tag) and _clean_text(node.get_text(" ", strip=True)):
            return node
    return soup.body or soup


def _heading_level(tag: Tag) -> int:

    # Gibt die Überschriften-Ebene zurück (h1=1 ... h6=6), sonst 99.
    if not tag.name or not tag.name.startswith("h"):
        return 99
    try:
        return int(tag.name[1:])
    except Exception:
        return 99


def _extract_sections_from_main(main: Tag) -> Tuple[str, Dict[str, str]]:
    
    # Extrahiert Beschreibung, Technik, Vorteile, Versionen anhand von Überschriften
    # Produktname: bevorzugt h1, andernfalls erster sinnvoller Titel
    h1 = main.find(["h1"])  # type: ignore[arg-type]
    name = _clean_text(h1.get_text(" ", strip=True)) if isinstance(h1, Tag) else "PGN-plus-P"

    # Inhalte, die befüllt werden sollen
    sections: Dict[str, List[str]] = {
        "beschreibung": [],
        "technik": [],
        "vorteile": [],
        "versionen": [],
    }

    # Mapping: Schlagworte in Überschriften -> Zielinhalt
    def classify_heading(text: str) -> Optional[str]:
        t = text.lower()
        if any(k in t for k in ["beschreibung", "universeller", "parallelgreifer", "pgn"]):
            return "beschreibung"
        if any(k in t for k in ["technik", "technische", "merkmale", "eigenschaften"]):
            return "technik"
        if any(k in t for k in ["vorteile", "profitieren", "auf einen blick", "nutzen"]):
            return "vorteile"
        if any(k in t for k in ["version", "varianten", "ausführung", "ausfuehrung"]):
            return "versionen"
        return None

    current_key: Optional[str] = None
    current_level: int = 99

    # Nacheinander durch die Elemente gehen, so wie sie im HTML stehen
    for el in main.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol"]):
        if not isinstance(el, Tag):
            continue

        # Neue Überschrift setzt den aktuellen Abschnitt
        if el.name and el.name.startswith("h"):
            title = _clean_text(el.get_text(" ", strip=True))
            key = classify_heading(title)
            if key:
                current_key = key
                current_level = _heading_level(el)
            continue

        # Falls kein Abschnitt gefunden, wird Text als Beschreibung genutzt
        if current_key is None:
            current_key = "beschreibung"
            current_level = 2

        # p als Text übernehmen
        if el.name == "p":
            text = _clean_text(el.get_text(" ", strip=True))
            if text:
                sections[current_key].append(text)
            continue

        # Listen als Stichworte übernehmen
        if el.name in ("ul", "ol"):
            items = []
            for li in el.find_all("li"):
                li_text = _clean_text(li.get_text(" ", strip=True))
                if li_text:
                    items.append(f"- {li_text}")
            if items:
                sections[current_key].extend(items)
            continue

    # In Strings zusammenführen
    joined = {k: _clean_text("\n".join(v)) for k, v in sections.items()}

    return name, joined


def scrape_series_page(url: str) -> ScrapeResult:
    
    # Scraped die Serienseite und liefert nur den Hauptcontent als strukturierte Inhalte
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    }

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    main = _pick_main_container(soup)
    _remove_noise(main)

    name, sections = _extract_sections_from_main(main)

    # Validierung, dass echter Content extrahiert wurde.
    beschreibung = sections.get("beschreibung", "")
    filled = [k for k, v in sections.items() if v]

    if len(beschreibung) < 80:
        raise ValueError(
            "Fehlgeschlagen: 'beschreibung' ist zu kurz. "
            "Wahrscheinlich wurde kein relevanter Content gefunden."
        )

    if not ("beschreibung" in filled and ("technik" in filled or "vorteile" in filled or "versionen" in filled)):
        raise ValueError(
            "Unvollständig: Es wurden nicht genug Inhalte befüllt (beschreibung + mind. eine weitere)."
        )

    return ScrapeResult(name=name, url=url, sections=sections)


def write_product_data_json(result: ScrapeResult, path: str) -> None:
    
    #Speichert das Scraping-Ergebnis als JSON
    payload = {
        "schema_version": 1,
        "name": result.name,
        "url": result.url,
        "sections": result.sections,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main() -> None:
    
    # scraped und schreibt settings.product_data_path
    url = settings.product_url
    out_path = settings.product_data_path

    # Datei wird nur geschrieben, wenn scrape_series_page keinen Fehler wirft
    result = scrape_series_page(url)
    write_product_data_json(result, out_path)


if __name__ == "__main__":
    main()
