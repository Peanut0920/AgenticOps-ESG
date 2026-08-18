#!/usr/bin/env python3
"""
AgenticOps-ESG Initialization Script

This script bootstraps the entire environment:
    - Creates required directories (data/, logs/)
    - Seeds the mock RAG vector database with regulatory clauses
    - Validates connectivity to external systems (Prometheus, TNB, GitHub)
    - Prints a summary for the user

Usage:
    python initialization.py --setup-db
    python initialization.py --dry-run
    python initialization.py --help
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("AgenticOps-Init")

# ============================================================
# 1. Directory Creation
# ============================================================
def create_directories():
    """Create all required folders for data persistence and logs."""
    dirs = [
        "data/rag_db",
        "data/telemetry_cache",
        "data/regulatory_pdfs",
        "logs"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        logger.info("📁 Created/verified directory: %s", d)

# ============================================================
# 2. RAG Database Seeding (Mock)
# ============================================================
def seed_rag_database():
    """
    Seed the vector database with mock regulatory clauses.
    In production, this would parse and embed real PDFs from data/regulatory_pdfs/.
    """
    try:
        from src.utils.db_connectors import VectorDatabase
    except ImportError:
        logger.error("❌ Could not import VectorDatabase. Ensure src/ is in PYTHONPATH.")
        return False

    db_path = Path("data/rag_db")
    db_path.mkdir(parents=True, exist_ok=True)

    logger.info("🧠 Seeding mock RAG database at %s...", db_path)
    vdb = VectorDatabase(persist_directory=str(db_path))

    # The mock database already has embedded knowledge, but we simulate ingestion
    # of PDFs for completeness.
    pdf_folder = Path("data/regulatory_pdfs")
    if pdf_folder.exists():
        pdf_files = list(pdf_folder.glob("*.pdf"))
        if pdf_files:
            logger.info("📄 Found %d PDFs in regulatory_pdfs/. Ingesting...", len(pdf_files))
            for pdf_file in pdf_files:
                vdb.ingest_pdf(
                    file_path=str(pdf_file),
                    metadata={"source": pdf_file.stem, "jurisdiction": "Malaysia"}
                )
        else:
            logger.warning("⚠️ No PDFs found in data/regulatory_pdfs/. Using built‑in mock knowledge.")
    else:
        logger.info("ℹ️ data/regulatory_pdfs/ does not exist. Using built‑in mock knowledge base.")

    logger.info("✅ RAG database ready.")
    return True

# ============================================================
# 3. Connectivity Checks (Optional)
# ============================================================
def test_connectivity(dry_run=False):
    """Test external API connectivity (Prometheus, TNB, GitHub)."""
    if dry_run:
        logger.info("🔍 Dry‑run mode: skipping external connectivity tests.")
        return True

    # Try importing settings (falls back to defaults if .env missing)
    try:
        from src.config.settings import AppSettings
        settings = AppSettings()
    except ImportError:
        logger.warning("⚠️ Could not import AppSettings. Using fallback defaults.")
        settings = None

    all_ok = True

    # 1. Prometheus (mock if no URL)
    prom_url = getattr(settings, "prometheus_url", "http://localhost:9090") if settings else "http://localhost:9090"
    if "localhost" in prom_url or "example" in prom_url:
        logger.info("ℹ️ Prometheus URL is set to a placeholder. Mock mode will be used.")
    else:
        # Attempt a simple ping (optional)
        try:
            import httpx
            resp = httpx.get(f"{prom_url}/-/healthy", timeout=2.0)
            if resp.status_code == 200:
                logger.info("✅ Prometheus reachable at %s", prom_url)
            else:
                logger.warning("⚠️ Prometheus returned status %d", resp.status_code)
        except Exception:
            logger.warning("⚠️ Could not reach Prometheus at %s (will use mock).", prom_url)

    # 2. TNB API
    tnb_key = getattr(settings, "tnb_api_key", None) if settings else None
    if not tnb_key or tnb_key == "dummy_tnb_key":
        logger.info("ℹ️ No TNB API key provided. Using mock grid intensity.")
    else:
        logger.info("✅ TNB API key found (not validating).")

    # 3. GitHub
    gh_token = getattr(settings, "github_token", None) if settings else None
    if not gh_token or gh_token == "dummy_gh_token":
        logger.info("ℹ️ No GitHub token provided. GitOps PRs will be simulated.")
    else:
        logger.info("✅ GitHub token found (not validating).")

    return all_ok

# ============================================================
# 4. Main Entry Point
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="AgenticOps-ESG Bootstrapper",
        epilog="Run without arguments to perform a basic setup."
    )
    parser.add_argument(
        "--setup-db",
        action="store_true",
        help="Seed the RAG vector database with regulatory clauses."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip external connectivity tests."
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output (not used in this version)."
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("🚀 AgenticOps-ESG Initialization")
    logger.info("=" * 60)

    # Step 1: Create directories
    create_directories()

    # Step 2: Seed RAG DB (if requested)
    if args.setup_db:
        success = seed_rag_database()
        if not success:
            logger.error("❌ RAG seeding failed. Please check your installation.")
            sys.exit(1)

    # Step 3: Connectivity tests
    test_connectivity(dry_run=args.dry_run)

    # Step 4: Final summary
    print("\n" + "=" * 60)
    print(" ✅ INITIALIZATION COMPLETE")
    print("=" * 60)
    print(f" 📁 Data directory:    {Path('data').absolute()}")
    print(f" 📁 Log directory:     {Path('logs').absolute()}")
    print(f" 🧠 RAG DB seeded:     {'Yes' if args.setup_db else 'Existing/Not requested'}")
    print(f" 🔌 Connectivity:      {'Skipped (dry-run)' if args.dry_run else 'Checked (mock fallbacks)'}")
    print("\n Next steps:")
    print("   1. Start the backend:   uvicorn backend_api.main:app --reload")
    print("   2. Serve the frontend:  cd frontend && python3 -m http.server 5500")
    print("   3. Open the dashboard:  http://localhost:5500")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()