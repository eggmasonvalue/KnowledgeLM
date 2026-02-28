"""Command-line interface for KnowledgeLM.

This module provides CLI commands for batch downloading NSE company announcements.
The CLI is designed to be used both directly by users and by AI agents via the
knowledgelm-nse agent skill.

Usage:
    knowledgelm --help
    knowledgelm download SYMBOL --from DATE --to DATE
    knowledgelm personnel SYMBOL --from DATE --to DATE
    knowledgelm key-announcements SYMBOL --from DATE --to DATE
    # knowledgelm board-outcome SYMBOL --from DATE --to DATE
    knowledgelm shareholder-meetings SYMBOL --from DATE --to DATE
    knowledgelm list-categories
    knowledgelm forum URL
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from knowledgelm.config import DOWNLOAD_CATEGORIES_CONFIG
from knowledgelm.core.forum import ForumClient, PDFGenerator, ReferenceExtractor
from knowledgelm.core.service import KnowledgeService


# Configure logging for CLI
def configure_logging():
    """Configure logging to send all logs to knowledgelm.log.

    This ensures that the terminal (stdout/stderr) remains completely clean
    for primary command output and error reporting, while background process
    details are captured in the log file.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="knowledgelm.log",
        filemode="w",  # Overwrite on every run
        force=True,
    )


logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> datetime:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise click.BadParameter(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")


@click.group()
@click.version_option(version="4.2.1", prog_name="knowledgelm")
def main():
    r"""KnowledgeLM - Batch download NSE company announcements.

    A CLI tool for downloading company filings from NSE India, designed to work
    with AI agents and NotebookLM integration.

    \b
    Quick Start:
        knowledgelm download HDFCBANK --from 2023-01-01 --to 2025-01-26

    \b
    For AI Agents:
        Run 'knowledgelm --help' to discover available commands.
        Run 'knowledgelm download --help' for download options.
    """
    pass


@main.command()
@click.argument("symbol")
@click.option("--from", "from_date", required=True, help="Start date in YYYY-MM-DD format.")
@click.option("--to", "to_date", required=True, help="End date in YYYY-MM-DD format.")
@click.option(
    "--categories",
    default="all",
    help="Comma-separated categories to download. Use 'all' for all categories. "
    "Run 'knowledgelm list-categories' to see available options.",
)
@click.option(
    "--output", "-o", default=None, help="Output directory. Defaults to ./{SYMBOL}_sources/"
)
@click.option(
    "--annual-reports-all",
    is_flag=True,
    default=False,
    help="Download ALL annual reports regardless of date range.",
)
def download(
    symbol: str,
    from_date: str,
    to_date: str,
    categories: str,
    output: Optional[str],
    annual_reports_all: bool,
):
    r"""Download company filings from NSE India.

    \b
    Examples:
        knowledgelm download HDFCBANK --from 2023-01-01 --to 2025-01-26
        knowledgelm download INFY --from 2020-01-01 --to 2025-01-26 \
            --categories transcripts,credit_rating
        knowledgelm download RELIANCE --from 2020-01-01 --to 2025-01-26 \
            --annual-reports-all

    \b
    Available Categories:
        transcripts, investor_presentations, credit_rating, annual_reports,
        related_party_txns, press_releases, issue_documents
    """
    # Configure logging first
    configure_logging()

    # Parse dates
    try:
        start = parse_date(from_date)
        end = parse_date(to_date)
    except click.BadParameter as e:
        logger.error(f"Invalid date format: {e}")
        click.echo(json.dumps({"error": str(e), "success": False}))
        sys.exit(1)

    # Determine output directory
    folder_name = output if output else f"{symbol.upper()}_sources"

    # Build options dict
    if categories.lower() == "all":
        selected_categories = list(DOWNLOAD_CATEGORIES_CONFIG.keys())
    else:
        selected_categories = [c.strip() for c in categories.split(",")]

    # Validate categories
    valid_cats = set(DOWNLOAD_CATEGORIES_CONFIG.keys())
    invalid = set(selected_categories) - valid_cats
    if invalid:
        msg = f"Invalid categories: {', '.join(invalid)}. Valid: {', '.join(valid_cats)}"
        logger.error(msg)
        click.echo(json.dumps({"error": msg, "success": False}))
        sys.exit(1)

    options = {
        cfg["enabled_arg"]: (cat in selected_categories)
        for cat, cfg in DOWNLOAD_CATEGORIES_CONFIG.items()
    }

    # Run download
    try:
        service = KnowledgeService(str(Path.cwd()))
        announcements, counts = service.process_request(
            symbol=symbol.upper(),
            from_date=start,
            to_date=end,
            folder_name=folder_name,
            options=options,
            annual_reports_all_mode=annual_reports_all,
        )

        result = {
            "success": True,
            "symbol": symbol.upper(),
            "output_directory": str(Path.cwd() / folder_name),
            "date_range": {"from": from_date, "to": to_date},
            "downloads": counts,
            "total_files": sum(counts.values()),
        }

        # Output result as JSON to stdout (always)
        click.echo(json.dumps(result, indent=2))

        # Log process summary (intermediate logs already sent to knowledgelm.log)
        logger.info(f"Producing JSON result for {symbol.upper()}")
        logger.info(f"✓ Downloaded filings for {symbol.upper()}")
        logger.info(f"  Output: {result['output_directory']}")
        logger.info("  Categories:")
        for cat, count in counts.items():
            logger.info(f"    - {cat}: {count} files")
        logger.info(f"  Total: {result['total_files']} files")
        logger.info(f"JSON Result: {json.dumps(result)}")

    except ValueError as e:
        logger.error(f"Value error during download: {e}")
        click.echo(json.dumps({"error": str(e), "success": False}))
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during download")
        click.echo(json.dumps({"error": str(e), "success": False}))
        sys.exit(1)


@main.command("list-categories")
def list_categories():
    """List available download categories.

    Shows all filing types that can be downloaded from NSE.
    """
    configure_logging()

    categories = {
        cat: {
            "label": cfg["label"],
            "config_key": cfg["enabled_arg"],
        }
        for cat, cfg in DOWNLOAD_CATEGORIES_CONFIG.items()
    }

    # Always output JSON to stdout
    click.echo(json.dumps(categories, indent=2))

    # Log results to knowledgelm.log
    logger.info("Available categories:")
    for cat, info in categories.items():
        logger.info(f"  {cat}: {info['label']}")
    logger.info(f"JSON Result: {json.dumps(categories)}")


@main.command("forum")
@click.argument("url")
@click.option("--symbol", "-s", help="Company symbol for the output folder (e.g., HDFCBANK).")
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output directory path. Defaults to ./misc_sources/forum_valuepickr/ if no symbol is provided.",
)
def download_forum(url: str, symbol: Optional[str], output: Optional[str]):
    """Download a ValuePickr forum thread as a clean PDF.

    Args:
        url: The full URL of the ValuePickr thread.
        symbol: Optional company symbol for the filename and folder.
        output: Optional custom output directory.
    """
    configure_logging()

    try:
        client = ForumClient()

        # 1. Fetch data
        logger.info(f"Fetching thread data from {url}...")

        thread_data = client.get_full_thread(url)
        slug = client.parse_topic_url(url)[0]

        # 2. Determine output directory
        if symbol:
            base_folder = f"{symbol.upper()}_sources"
        else:
            base_folder = "misc_sources"

        if not output:
            output_dir = Path.cwd() / base_folder / "forum_valuepickr"
        else:
            output_dir = Path(output) / "forum_valuepickr"

        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "forum_thread.pdf"

        # 3. Generate PDF
        logger.info(f"Generating PDF with {len(thread_data['posts'])} posts...")

        generator = PDFGenerator()
        generator.generate_thread_pdf(thread_data, output_path)

        # 4. Extract references
        logger.info("Extracting external references...")

        ref_extractor = ReferenceExtractor()
        ref_content = ref_extractor.extract_references(thread_data)

        ref_path = output_dir / "forum_links.md"
        with open(ref_path, "w", encoding="utf-8") as f:
            f.write(ref_content)

        result = {
            "success": True,
            "title": thread_data.get("title"),
            "posts_count": len(thread_data["posts"]),
            "output_path": str(output_path.absolute()),
            "references_path": str(ref_path.absolute()),
        }

        # Always output JSON to stdout
        click.echo(json.dumps(result, indent=2))

        # Log process summary
        logger.info(f"✓ Successfully saved thread to {result['output_path']}")
        logger.info(f"✓ References extracted to {result['references_path']}")
        logger.info(f"JSON Result: {json.dumps(result)}")

    except Exception as e:
        logger.exception("Failed to download forum thread")
        click.echo(json.dumps({"error": str(e), "success": False}))
        sys.exit(1)


@main.command()
@click.argument("symbol")
@click.option("--from", "from_date", required=True, help="Start date in YYYY-MM-DD format.")
@click.option("--to", "to_date", required=True, help="End date in YYYY-MM-DD format.")
@click.option(
    "--output", "-o", default=None, help="Output directory. Defaults to ./{SYMBOL}_sources/"
)
def personnel(symbol: str, from_date: str, to_date: str, output: Optional[str]):
    r"""Query board-level personnel changes via XBRL.

    Saves parsed JSON to the output directory and returns a summary.

    \b
    Examples:
        knowledgelm personnel HDFCBANK --from 2023-01-01 --to 2025-01-26
    """
    _query_xbrl(symbol, "personnel", from_date, to_date, output)


@main.command("key-announcements")
@click.argument("symbol")
@click.option("--from", "from_date", required=True, help="Start date in YYYY-MM-DD format.")
@click.option("--to", "to_date", required=True, help="End date in YYYY-MM-DD format.")
@click.option(
    "--output", "-o", default=None, help="Output directory. Defaults to ./{SYMBOL}_sources/"
)
def key_announcements(symbol: str, from_date: str, to_date: str, output: Optional[str]):
    r"""Query key corporate announcements (Reg 30, fund raising, etc.) via XBRL."""
    _query_xbrl(symbol, "key_announcements", from_date, to_date, output)


# @main.command("board-outcome")
# @click.argument("symbol")
# @click.option("--from", "from_date", required=True, help="Start date in YYYY-MM-DD format.")
# @click.option("--to", "to_date", required=True, help="End date in YYYY-MM-DD format.")
# @click.option(
#     "--output", "-o", default=None, help="Output directory. Defaults to ./{SYMBOL}_sources/"
# )
# def board_outcome(symbol: str, from_date: str, to_date: str, output: Optional[str]):
#     r"""Query board meeting outcomes via XBRL."""
#     _query_xbrl(symbol, "board_outcome", from_date, to_date, output)


@main.command("shareholder-meetings")
@click.argument("symbol")
@click.option("--from", "from_date", required=True, help="Start date in YYYY-MM-DD format.")
@click.option("--to", "to_date", required=True, help="End date in YYYY-MM-DD format.")
@click.option(
    "--output", "-o", default=None, help="Output directory. Defaults to ./{SYMBOL}_sources/"
)
def shareholder_meetings(symbol: str, from_date: str, to_date: str, output: Optional[str]):
    r"""Query shareholder meeting announcements via XBRL."""
    _query_xbrl(symbol, "shm", from_date, to_date, output)


def _query_xbrl(symbol: str, category: str, from_date: str, to_date: str, output: str):
    """Helper to run XBRL queries."""
    configure_logging()

    try:
        start = parse_date(from_date)
        end = parse_date(to_date)
    except click.BadParameter as e:
        click.echo(json.dumps({"error": str(e), "success": False}))
        sys.exit(1)

    # Determine output directory (same logic as download)
    folder_name = output if output else f"{symbol.upper()}_sources"
    config = DOWNLOAD_CATEGORIES_CONFIG[category]
    options = {cfg["enabled_arg"]: (c == category) for c, cfg in DOWNLOAD_CATEGORIES_CONFIG.items()}

    try:
        service = KnowledgeService(str(Path.cwd()))
        announcements, counts = service.process_request(
            symbol=symbol.upper(),
            from_date=start,
            to_date=end,
            folder_name=folder_name,
            options=options,
        )

        label = config["label"]
        count = counts.get(label, 0)
        output_dir = Path.cwd() / folder_name
        
        if category == "personnel":
            json_path = output_dir / "personnel_changes.json"
        elif category == "key_announcements":
            json_path = output_dir / "key_announcements.json"
        elif category == "shm":
            json_path = output_dir / "shareholder_meetings" / "shm_details.json"
        else:
            json_path = output_dir / f"{category}_details.json"

        result = {
            "success": True,
            "symbol": symbol.upper(),
            "category": label,
            "date_range": {"from": from_date, "to": to_date},
            "total": count,
            "output_path": str(json_path.absolute()) if count > 0 else None,
        }

        # Always output JSON to stdout
        click.echo(json.dumps(result, indent=2))

        # Log process summary
        if count > 0:
            logger.info(f"✓ Found {count} {label} record(s).")
            logger.info(f"  Parsed details saved to: {result['output_path']}")
        else:
            logger.info(f"No {label} records found for the given date range.")
        logger.info(f"JSON Result: {json.dumps(result)}")

    except Exception as e:
        logger.exception(f"Failed to query {category}")
        click.echo(json.dumps({"error": str(e), "success": False}))
        sys.exit(1)


if __name__ == "__main__":
    main()
