"""Command-line interface for KnowledgeLM.

This module provides CLI commands for batch downloading NSE company announcements.
The CLI is designed to be used both directly by users and by AI agents via the
knowledgelm-nse agent skill.

Usage:
    knowledgelm --help
    knowledgelm download SYMBOL --from DATE --to DATE
    knowledgelm list-categories
    knowledgelm list-files DIRECTORY --json
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from knowledgelm.config import DOWNLOAD_CATEGORIES_CONFIG
from knowledgelm.core.service import KnowledgeService

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> datetime:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise click.BadParameter(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")


@click.group()
@click.version_option(version="3.0.0", prog_name="knowledgelm")
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
    "--output", "-o", default=None, help="Output directory. Defaults to ./{SYMBOL}_knowledgeLM/"
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
    folder_name = output if output else f"{symbol.upper()}_knowledgeLM"

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
        knowledgelm list-files ./HDFCBANK_knowledgeLM --json
    """
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


if __name__ == "__main__":
    main()
