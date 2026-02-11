"""Command-line interface for KnowledgeLM.

This module provides CLI commands for batch downloading NSE company announcements.
The CLI is designed to be used both directly by users and by AI agents via the
knowledgelm-nse agent skill.

Usage:
    knowledgelm --help
    knowledgelm download SYMBOL --from DATE --to DATE
    knowledgelm list-categories
    knowledgelm list-files DIRECTORY --json
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
@click.version_option(version="4.2.0", prog_name="knowledgelm")
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
    "--output", "-o", default=None, help="Output directory. Defaults to ./{SYMBOL}_filings/"
)
@click.option(
    "--annual-reports-all",
    is_flag=True,
    default=False,
    help="Download ALL annual reports regardless of date range.",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    default=False,
    help="Output results as JSON for agent parsing.",
)
def download(
    symbol: str,
    from_date: str,
    to_date: str,
    categories: str,
    output: Optional[str],
    annual_reports_all: bool,
    output_json: bool,
):
    r"""Download company filings from NSE India.

    \b
    Examples:
        knowledgelm download HDFCBANK --from 2023-01-01 --to 2025-01-26
        knowledgelm download INFY --from 2020-01-01 --to 2025-01-26 \
            --categories transcripts,credit_rating
        knowledgelm download RELIANCE --from 2020-01-01 --to 2025-01-26 \
            --annual-reports-all --json

    \b
    Available Categories:
        transcripts, investor_presentations, credit_rating, annual_reports,
        related_party_txns, press_releases
    """
    # Configure logging first
    configure_logging()

    # Parse dates
    try:
        start = parse_date(from_date)
        end = parse_date(to_date)
    except click.BadParameter as e:
        if output_json:
            click.echo(json.dumps({"error": str(e), "success": False}))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Determine output directory
    folder_name = output if output else f"{symbol.upper()}_filings"

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
        if output_json:
            click.echo(json.dumps({"error": msg, "success": False}))
        else:
            click.echo(f"Error: {msg}", err=True)
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

        if output_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"✓ Downloaded filings for {symbol.upper()}")
            click.echo(f"  Output: {result['output_directory']}")
            click.echo("  Categories:")
            for cat, count in counts.items():
                click.echo(f"    - {cat}: {count} files")
            click.echo(f"  Total: {result['total_files']} files")

    except ValueError as e:
        if output_json:
            click.echo(json.dumps({"error": str(e), "success": False}))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during download")
        if output_json:
            click.echo(json.dumps({"error": str(e), "success": False}))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command("list-categories")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON.")
def list_categories(output_json: bool):
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

    if output_json:
        click.echo(json.dumps(categories, indent=2))
    else:
        click.echo("Available categories:")
        for cat, info in categories.items():
            click.echo(f"  {cat}: {info['label']}")


@main.command("list-files")
@click.argument("directory", type=click.Path(exists=True))
@click.option("--json", "output_json", is_flag=True, help="Output as JSON.")
@click.option(
    "--exclude",
    multiple=True,
    default=[".pkl"],
    help="File extensions to exclude. Defaults to .pkl",
)
def list_files(directory: str, output_json: bool, exclude: tuple):
    r"""List downloaded files in a directory.

    Useful for NotebookLM integration - outputs file paths that can be
    added as sources to a notebook.

    \b
    Example:
        knowledgelm list-files ./HDFCBANK_filings --json
    """
    configure_logging()

    dir_path = Path(directory)
    files = []

    for file_path in dir_path.rglob("*"):
        if file_path.is_file():
            # Check exclusions
            if any(file_path.suffix.lower() == ext.lower() for ext in exclude):
                continue
            files.append(
                {
                    "path": str(file_path.absolute()),
                    "name": file_path.name,
                    "category": file_path.parent.name if file_path.parent != dir_path else "root",
                    "size_bytes": file_path.stat().st_size,
                }
            )

    result = {
        "directory": str(dir_path.absolute()),
        "file_count": len(files),
        "files": files,
    }

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"Files in {directory}:")
        for f in files:
            click.echo(f"  [{f['category']}] {f['name']}")
        click.echo(f"\nTotal: {len(files)} files")


@main.command("forum")
@click.argument("url")
@click.option("--symbol", "-s", help="Company symbol for the output folder (e.g., HDFCBANK).")
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output directory path. Defaults to ./<SYMBOL>_valuepickr/",
)
@click.option("--json", "output_json", is_flag=True, help="Output result as JSON.")
def download_forum(url: str, symbol: Optional[str], output: Optional[str], output_json: bool):
    """Download a ValuePickr forum thread as a clean PDF.

    Arguments:
        URL: The full URL of the ValuePickr thread.
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
            folder_name = f"{symbol.upper()}_valuepickr"
        else:
            folder_name = f"{slug}_valuepickr"

        if not output:
            output_dir = Path.cwd() / folder_name
        else:
            output_dir = Path(output)

        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{slug}_valuepickr_forum.pdf"

        # 3. Generate PDF
        logger.info(f"Generating PDF with {len(thread_data['posts'])} posts...")

        generator = PDFGenerator()
        generator.generate_thread_pdf(thread_data, output_path)

        # 4. Extract references
        logger.info("Extracting external references...")

        ref_extractor = ReferenceExtractor()
        ref_content = ref_extractor.extract_references(thread_data)

        ref_path = output_dir / f"{slug}_ValuePickr_references.md"
        with open(ref_path, "w", encoding="utf-8") as f:
            f.write(ref_content)

        result = {
            "success": True,
            "title": thread_data.get("title"),
            "posts_count": len(thread_data["posts"]),
            "output_path": str(output_path.absolute()),
            "references_path": str(ref_path.absolute()),
        }

        if output_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"✓ Successfully saved thread to {result['output_path']}")
            click.echo(f"✓ References extracted to {result['references_path']}")

    except Exception as e:
        logger.exception("Failed to download forum thread")
        if output_json:
            click.echo(json.dumps({"error": str(e), "success": False}))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
