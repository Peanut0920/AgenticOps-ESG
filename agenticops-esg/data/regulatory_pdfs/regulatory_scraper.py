#!/usr/bin/env python3
"""
Regulatory PDF Scraper v2 – AgenticOps-ESG
- Uses modern browser headers to bypass 403
- Discovers PDFs dynamically from current portals
- Prints manual download commands when automation fails
"""

import os
import re
import argparse
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# ============================================================
# Configuration
# ============================================================

DATA_DIR = Path("data/regulatory_pdfs")
METADATA_FILE = DATA_DIR / "scraper_metadata.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

REQUEST_TIMEOUT = 30

# Modern browser headers to bypass 403
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# ============================================================
# Base Scraper with Better Fetch
# ============================================================

class RegulatoryScraper:
    def __init__(self, name: str, source_url: str):
        self.name = name
        self.source_url = source_url
        self.session = requests.Session()
        self.session.headers.update(BROWSER_HEADERS)
        self.session.max_redirects = 5

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch with retries and better error handling."""
        try:
            resp = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if resp.status_code == 403:
                # Try with extra "Referer" to bypass some CDN blocks
                self.session.headers.update({"Referer": "https://www.google.com/"})
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            print(f"   ⚠️ Fetch error: {e}")
            return None

    def download_pdf(self, url: str, filename: str) -> Optional[Path]:
        try:
            self.session.headers.update({"Referer": urlparse(url).netloc})
            resp = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            resp.raise_for_status()
            if not resp.content[:4].startswith(b"%PDF"):
                print(f"   ⚠️ Skipped (not a PDF): {filename}")
                return None
            filepath = DATA_DIR / filename
            with open(filepath, "wb") as f:
                f.write(resp.content)
            print(f"   ✅ Downloaded: {filename} ({len(resp.content) // 1024} KB)")
            return filepath
        except Exception as e:
            print(f"   ❌ Download failed: {e}")
            return None

    def scrape(self) -> List[Dict]:
        raise NotImplementedError

    def manual_guide(self, url: str, hint: str):
        """Print a manual download guide for hard-to-scrape sources."""
        print(f"   ℹ️  Auto-scrape blocked. Please manually download from:")
        print(f"      🔗 {url}")
        print(f"      💡 {hint}")
        print(f"      📁 Place the PDF in: {DATA_DIR}/")


# ============================================================
# 1. BURSA – Fix: Dynamic page discovery with referer
# ============================================================

class BursaScraper(RegulatoryScraper):
    def __init__(self):
        super().__init__(
            name="bursa",
            source_url="https://www.bursamalaysia.com/sustainability/sustainability-reporting-guide"
        )

    def scrape(self) -> List[Dict]:
        results = []
        html = self.fetch_page(self.source_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            # Find all PDF links on the page
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.lower().endswith(".pdf"):
                    full_url = urljoin(self.source_url, href)
                    # Look for sustainability or guide keywords
                    if "sustainability" in href.lower() or "guide" in href.lower():
                        filename = f"bursa_{Path(urlparse(full_url).path).name}"
                        filepath = self.download_pdf(full_url, filename)
                        if filepath:
                            results.append({
                                "source": self.name,
                                "url": full_url,
                                "filename": filename,
                                "filepath": str(filepath),
                                "description": link.get_text(strip=True) or "Bursa Guide",
                                "scraped_at": datetime.now().isoformat()
                            })
        if not results:
            self.manual_guide(
                "https://www.bursamalaysia.com/sustainability/sustainability-reporting-guide",
                "Look for the 'Download' button or PDF icon on the page."
            )
        return results


# ============================================================
# 2. MCMC – Keep working G004, discover others
# ============================================================

class MCMCScraper(RegulatoryScraper):
    def __init__(self):
        super().__init__(
            name="mcmc",
            source_url="https://www.mcmc.gov.my/en/documents/technical-codes"
        )

    def scrape(self) -> List[Dict]:
        results = []
        # Known good link (was 404 for G002, but G004 works)
        known_good = {
            "url": "https://www.mcmc.gov.my/skmmgovmy/media/General/registers/MCMC-MTSFB-G0042024-Specification-for-Green-Data-Centres-First-Revision.pdf",
            "filename": "mcmc_green_data_centres_g004_2024.pdf",
            "description": "MCMC G004:2024 - Green Data Centres"
        }
        fp = self.download_pdf(known_good["url"], known_good["filename"])
        if fp:
            results.append({**known_good, "filepath": str(fp), "scraped_at": datetime.now().isoformat()})

        # Try dynamic discovery for others
        html = self.fetch_page(self.source_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.lower().endswith(".pdf") and "technical" in href.lower():
                    full_url = urljoin(self.source_url, href)
                    filename = f"mcmc_{Path(urlparse(full_url).path).name}"
                    filepath = self.download_pdf(full_url, filename)
                    if filepath:
                        results.append({
                            "source": self.name,
                            "url": full_url,
                            "filename": filename,
                            "filepath": str(filepath),
                            "description": link.get_text(strip=True) or "MCMC Tech Code",
                            "scraped_at": datetime.now().isoformat()
                        })
        return results


# ============================================================
# 3. TENAGA – Fix: Point to the Acts page
# ============================================================

class TenagaScraper(RegulatoryScraper):
    def __init__(self):
        super().__init__(
            name="tenaga",
            source_url="https://www.st.gov.my/en/contents/policies_acts/acts"
        )

    def scrape(self) -> List[Dict]:
        results = []
        html = self.fetch_page(self.source_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.lower().endswith(".pdf"):
                    full_url = urljoin(self.source_url, href)
                    if "energy" in href.lower() or "efficiency" in href.lower() or "act" in href.lower():
                        filename = f"tenaga_{Path(urlparse(full_url).path).name}"
                        filepath = self.download_pdf(full_url, filename)
                        if filepath:
                            results.append({
                                "source": self.name,
                                "url": full_url,
                                "filename": filename,
                                "filepath": str(filepath),
                                "description": link.get_text(strip=True) or "Tenaga Document",
                                "scraped_at": datetime.now().isoformat()
                            })
        if not results:
            self.manual_guide(
                "https://www.st.gov.my/en/contents/policies_acts/acts",
                "Look for the Energy Efficiency and Conservation Act 2024 PDF."
            )
        return results


# ============================================================
# 4. DOE – Fix: Point to guidelines search
# ============================================================

class Doescraper(RegulatoryScraper):
    def __init__(self):
        super().__init__(
            name="doe",
            source_url="https://www.doe.gov.my/en/regulations-guidelines"
        )

    def scrape(self) -> List[Dict]:
        results = []
        html = self.fetch_page(self.source_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.lower().endswith(".pdf"):
                    full_url = urljoin(self.source_url, href)
                    if any(k in href.lower() for k in ["eia", "environment", "quality", "emission"]):
                        filename = f"doe_{Path(urlparse(full_url).path).name}"
                        filepath = self.download_pdf(full_url, filename)
                        if filepath:
                            results.append({
                                "source": self.name,
                                "url": full_url,
                                "filename": filename,
                                "filepath": str(filepath),
                                "description": link.get_text(strip=True) or "DOE PDF",
                                "scraped_at": datetime.now().isoformat()
                            })
        if not results:
            self.manual_guide(
                "https://www.doe.gov.my/en/regulations-guidelines",
                "Search for 'EIA Guidelines' or 'Environmental Quality' reports."
            )
        return results


# ============================================================
# 5. MITI – Fix: Search within the main policies page
# ============================================================

class MITIScraper(RegulatoryScraper):
    def __init__(self):
        super().__init__(
            name="miti",
            source_url="https://www.miti.gov.my/index.php/policies/guidelines"
        )

    def scrape(self) -> List[Dict]:
        results = []
        html = self.fetch_page(self.source_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.lower().endswith(".pdf"):
                    full_url = urljoin(self.source_url, href)
                    if "data centre" in href.lower() or "sustainability" in href.lower():
                        filename = f"miti_{Path(urlparse(full_url).path).name}"
                        filepath = self.download_pdf(full_url, filename)
                        if filepath:
                            results.append({
                                "source": self.name,
                                "url": full_url,
                                "filename": filename,
                                "filepath": str(filepath),
                                "description": link.get_text(strip=True) or "MITI PDF",
                                "scraped_at": datetime.now().isoformat()
                            })
        if not results:
            self.manual_guide(
                "https://www.miti.gov.my/index.php/policies/guidelines",
                "Search for 'Data Centre Sustainability Guidelines'."
            )
        return results


# ============================================================
# 6. SC (Securities Commission) – real link structure
# ============================================================

class SCSraper(RegulatoryScraper):
    def __init__(self):
        super().__init__(
            name="sc",
            source_url="https://www.sc.com.my/sustainability/national-sustainability-reporting-framework"
        )

    def scrape(self) -> List[Dict]:
        results = []
        html = self.fetch_page(self.source_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.lower().endswith(".pdf"):
                    full_url = urljoin(self.source_url, href)
                    if "nsrf" in href.lower() or "sustainability" in href.lower():
                        filename = f"sc_{Path(urlparse(full_url).path).name}"
                        filepath = self.download_pdf(full_url, filename)
                        if filepath:
                            results.append({
                                "source": self.name,
                                "url": full_url,
                                "filename": filename,
                                "filepath": str(filepath),
                                "description": link.get_text(strip=True) or "SC PDF",
                                "scraped_at": datetime.now().isoformat()
                            })
        if not results:
            self.manual_guide(
                "https://www.sc.com.my/sustainability/national-sustainability-reporting-framework",
                "Look for the 'Implementation Guide' download button."
            )
        return results


# ============================================================
# 7. MGTC – keep working ones, fix GHG URL
# ============================================================

class MGTScraper(RegulatoryScraper):
    def __init__(self):
        super().__init__(
            name="mgtc",
            source_url="https://www.mgtc.gov.my/resources/publications"
        )

    def scrape(self) -> List[Dict]:
        results = []
        html = self.fetch_page(self.source_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.lower().endswith(".pdf"):
                    full_url = urljoin(self.source_url, href)
                    filename = f"mgtc_{Path(urlparse(full_url).path).name}"
                    filepath = self.download_pdf(full_url, filename)
                    if filepath:
                        results.append({
                            "source": self.name,
                            "url": full_url,
                            "filename": filename,
                            "filepath": str(filepath),
                            "description": link.get_text(strip=True) or "MGTC PDF",
                            "scraped_at": datetime.now().isoformat()
                        })
        if not results:
            # Fallback: try generic search
            self.manual_guide(
                "https://www.mgtc.gov.my/resources/publications",
                "Search for 'GHG Accounting Guidelines' or 'Green Technology Master Plan'."
            )
        return results


# ============================================================
# GRI – keep working (they are publicly available)
# ============================================================

class GRIScraper(RegulatoryScraper):
    def __init__(self):
        super().__init__(
            name="gri",
            source_url="https://www.globalreporting.org/how-to-use-the-gri-standards/gri-standards-english-language/"
        )

    def scrape(self) -> List[Dict]:
        results = []
        # Known working mockup
        known = {
            "url": "https://www.globalreporting.org/media/wavkg5lw/item-07-mock-up-of-a-gri-topic-standard.pdf",
            "filename": "gri_305_emissions_2016_mockup.pdf",
            "description": "GRI 305: Emissions 2016 (Mock-up)"
        }
        fp = self.download_pdf(known["url"], known["filename"])
        if fp:
            results.append({**known, "filepath": str(fp), "scraped_at": datetime.now().isoformat()})

        # Try to find more GRI PDFs via discovery
        html = self.fetch_page(self.source_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.lower().endswith(".pdf") and "gri" in href.lower():
                    full_url = urljoin(self.source_url, href)
                    filename = f"gri_{Path(urlparse(full_url).path).name}"
                    filepath = self.download_pdf(full_url, filename)
                    if filepath:
                        results.append({
                            "source": self.name,
                            "url": full_url,
                            "filename": filename,
                            "filepath": str(filepath),
                            "description": link.get_text(strip=True) or "GRI Standard",
                            "scraped_at": datetime.now().isoformat()
                        })
        return results


# ============================================================
# SASB – remains manual (requires registration)
# ============================================================

class SASBScraper(RegulatoryScraper):
    def __init__(self):
        super().__init__(name="sasb", source_url="https://sasb.ifrs.org/standards/")

    def scrape(self) -> List[Dict]:
        self.manual_guide(
            "https://sasb.ifrs.org/standards/",
            "Free registration required. Download the Hardware (TC-HW) standard."
        )
        return []


# ============================================================
# ORCHESTRATOR (updated)
# ============================================================

class RegulatoryScraperOrchestrator:
    def __init__(self):
        self.scrapers = {
            "bursa": BursaScraper(),
            "mcmc": MCMCScraper(),
            "tenaga": TenagaScraper(),
            "doe": Doescraper(),
            "miti": MITIScraper(),
            "sc": SCSraper(),
            "mgtc": MGTScraper(),
            "gri": GRIScraper(),
            "sasb": SASBScraper(),
            # Add others (mdec, nsrf, kpkt) as needed – they redirect or are web-only
        }
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        if METADATA_FILE.exists():
            try:
                with open(METADATA_FILE, "r") as f:
                    return json.load(f)
            except:
                return {"downloaded_files": [], "last_run": None}
        return {"downloaded_files": [], "last_run": None}

    def _save_metadata(self):
        self.metadata["last_run"] = datetime.now().isoformat()
        with open(METADATA_FILE, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def scrape_source(self, source: str) -> List[Dict]:
        if source not in self.scrapers:
            print(f"❌ Unknown: {source}")
            return []
        print(f"\n📡 Scraping {source.upper()}...")
        results = self.scrapers[source].scrape()
        for r in results:
            if r["filepath"] not in self.metadata["downloaded_files"]:
                self.metadata["downloaded_files"].append(r["filepath"])
        self._save_metadata()
        return results

    def scrape_all(self):
        all_results = {}
        for s in self.scrapers:
            all_results[s] = self.scrape_source(s)
        return all_results

    def list_downloaded(self):
        files = []
        for f in self.metadata.get("downloaded_files", []):
            if Path(f).exists():
                files.append({"filename": Path(f).name, "size_kb": Path(f).stat().st_size // 1024})
        return files


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["bursa","mcmc","tenaga","doe","miti","sc","mgtc","gri","sasb"])
    parser.add_argument("--download-all", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    orch = RegulatoryScraperOrchestrator()

    if args.list:
        files = orch.list_downloaded()
        print("\n📁 Downloaded PDFs:")
        for f in files:
            print(f"   📄 {f['filename']} ({f['size_kb']} KB)")
        return

    if args.source:
        orch.scrape_source(args.source)
    elif args.download_all:
        orch.scrape_all()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()