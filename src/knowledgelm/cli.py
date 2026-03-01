"""Command-line interface for KnowledgeLM.

This module provides CLI commands for batch downloading NSE company announcements
and ValuePickr forum threads. Designed explicitly for LLM Agent consumption.
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


def configure_logging():
    """Configure logging to send all logs to knowledgelm.log.

    Ensures stdout/stderr are clean for JSON output.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="knowledgelm.log",
        filemode="w",
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
    """KnowledgeLM CLI: Data Extraction Interface for LLM Agents.

    Core Abstraction:
      This tool provides programmatic access to external data sources.
      It always outputs strictly formatted JSON to stdout. All standard logging,
      warnings, and progress bars are routed to `knowledgelm.log` to preserve
      your context window.

    Response Schema:
      Success: {"success": true, ...data...}
      Failure: {"success": false, "error": "<reason>"}

    Command Groups:
      fetch          : Universal data retrieval command.
                       - `fetch nse` : Retrieve corporate filings/XBRL.
                       - `fetch vp`  : Retrieve ValuePickr forum threads.
      convert        : Offline PDF-to-Markdown conversion tool.
                       - `convert file`: Safely convert a single PDF.
                       - `convert dir` : Bulk convert a directory of PDFs.
      list-datasets  : Enumerates valid values for `fetch nse --datasets`.
    """
    pass


@main.group()
def fetch():
    """Universal data retrieval command group.

    Execute `fetch nse --help` or `fetch vp --help` for specific schemas.
    """
    pass


@fetch.command("nse")
@click.argument("symbol")
@click.option("--start", "from_date", required=True, help="Date string YYYY-MM-DD.")
@click.option("--end", "to_date", required=True, help="Date string YYYY-MM-DD.")
@click.option(
    "--datasets",
    default="all",
    help="Comma-separated keys (e.g. 'transcripts,personnel'). Use 'all' for standard collection.",
)
@click.option(
    "--output", "-o", default=None, help="Output directory path. Defaults to ./{SYMBOL}_sources/"
)
@click.option(
    "--annual-reports-all",
    is_flag=True,
    default=False,
    help="Download ALL annual reports regardless of date range.",
)
def nse(
    symbol: str,
    from_date: str,
    to_date: str,
    datasets: str,
    output: Optional[str],
    annual_reports_all: bool,
):
    """Fetch Corporate Filings and XBRL structured data from NSE India.

    Inputs:
      symbol     : The National Stock Exchange of India ticker (e.g., HDFCBANK).
      --start    : YYYY-MM-DD filtering bound.
      --end      : YYYY-MM-DD filtering bound.
      --datasets : Specific data types to fetch. Run `list-datasets` to see options.

    Output Schema (JSON):
      {
        "success": true,
        "symbol": "HDFCBANK",
        "output_directory": "/absolute/path/to/HDFCBANK_sources",
        "date_range": {"from": "2024-01-01", "to": "2024-01-31"},
        "downloads": {"transcript": 2, "personnel change": 1},
        "total_files": 3
      }
    """
    configure_logging()

    try:
        start = parse_date(from_date)
        end = parse_date(to_date)
    except click.BadParameter as e:
        logger.error(f"Invalid date format: {e}")
        click.echo(json.dumps({"error": str(e), "success": False}))
        sys.exit(1)

    folder_name = output if output else f"{symbol.upper()}_sources"

    if datasets.lower() == "all":
        selected_categories = list(DOWNLOAD_CATEGORIES_CONFIG.keys())
    else:
        selected_categories = [c.strip() for c in datasets.split(",")]

    valid_cats = set(DOWNLOAD_CATEGORIES_CONFIG.keys())
    invalid = set(selected_categories) - valid_cats
    if invalid:
        msg = f"Invalid datasets: {', '.join(invalid)}. Valid: {', '.join(valid_cats)}"
        logger.error(msg)
        click.echo(json.dumps({"error": msg, "success": False}))
        sys.exit(1)

    options = {
        cfg["enabled_arg"]: (cat in selected_categories)
        for cat, cfg in DOWNLOAD_CATEGORIES_CONFIG.items()
    }

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

        click.echo(json.dumps(result, indent=2))

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


@fetch.command("vp")
@click.argument("url")
@click.option("--symbol", "-s", help="Stock symbol context (influences output directory).")
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output directory path. Defaults to ./misc_sources/forum_valuepickr/ if no symbol is provided.",
)
def vp(url: str, symbol: Optional[str], output: Optional[str]):
    """Fetch a ValuePickr forum thread as a clean, multimodal PDF and top links from the thread into a .md file.

    Inputs:
      url     : The fully qualified URL of the target thread.
      --symbol: If provided, correlates the export into the matching `{SYMBOL}_sources` folder.

    Output Schema (JSON):
      {
        "success": true,
        "title": "Thread Title",
        "posts_count": 150,
        "output_path": "/absolute/path/to/forum_thread.pdf",
        "references_path": "/absolute/path/to/forum_links.md"
      }
    """
    configure_logging()

    try:
        client = ForumClient()
        logger.info(f"Fetching thread data from {url}...")
        thread_data = client.get_full_thread(url)
        slug = client.parse_topic_url(url)[0]

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

        logger.info(f"Generating PDF with {len(thread_data['posts'])} posts...")
        generator = PDFGenerator()
        generator.generate_thread_pdf(thread_data, output_path)

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

        click.echo(json.dumps(result, indent=2))

        logger.info(f"✓ Successfully saved thread to {result['output_path']}")
        logger.info(f"✓ References extracted to {result['references_path']}")
        logger.info(f"JSON Result: {json.dumps(result)}")

    except Exception as e:
        logger.exception("Failed to download forum thread")
        click.echo(json.dumps({"error": str(e), "success": False}))
        sys.exit(1)


@main.command("list-datasets")
def list_datasets():
    """List valid values for the `fetch nse --datasets` parameter.
    
    Output Schema (JSON):
      {
        "datasets": {
          "transcripts": "Analyst call transcripts",
          "annual_reports": "Annual reports",
          "personnel": "Personnel changes (XBRL)",
          "shm": "Shareholder meetings (XBRL)"
        }
      }
    """
    configure_logging()
    
    datasets = {}
    for cat, cfg in DOWNLOAD_CATEGORIES_CONFIG.items():
        datasets[cat] = cfg["label"].title()
        if cfg.get("is_xbrl"):
            datasets[cat] += " (XBRL/JSON)"
            
    result = {"datasets": datasets}

    click.echo(json.dumps(result, indent=2))

    logger.info("Available datasets list fetched.")
    logger.info(f"JSON Result: {json.dumps(result)}")


@main.group()
def convert():
    """Offline PDF-to-Markdown conversion command group."""
    pass


def _convert_single_pdf(pdf_path: Path) -> dict:
    """Helper to convert a single PDF using MarkItDown and return stat dict."""
    import time
    from markitdown import MarkItDown
    
    start_time = time.time()
    try:
        md_converter = MarkItDown()
        result = md_converter.convert(str(pdf_path))
        
        md_path = pdf_path.with_suffix(".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result.text_content)
            
        return {
            "success": True,
            "file": pdf_path.name,
            "output": str(md_path.absolute()),
            "time_seconds": round(time.time() - start_time, 2),
            "characters": len(result.text_content)
        }
    except Exception as e:
        return {
            "success": False,
            "file": pdf_path.name,
            "error": str(e),
            "time_seconds": round(time.time() - start_time, 2)
        }


@convert.command("file")
@click.argument("filepath")
def convert_file(filepath: str):
    """Convert a single PDF file to Markdown.
    
    Inputs:
      filepath : Absolute or relative path to the .pdf file.
      
    Output Schema (JSON):
      {
        "success": true,
        "file": "AR_2024.pdf",
        "output": "/absolute/path/to/AR_2024.md",
        "time_seconds": 125.4,
        "characters": 1850230
      }
    """
    configure_logging()
    target_path = Path(filepath)
    
    if dict(target_path.absolute().parts).get(0) == "":
        pass # Handle root correctly on various OS if needed, but Path handles standard cases.
        
    if not target_path.exists():
        msg = f"File not found: {filepath}"
        logger.error(msg)
        click.echo(json.dumps({"error": msg, "success": False}))
        sys.exit(1)
        
    if not target_path.is_file() or target_path.suffix.lower() != ".pdf":
        msg = f"Target must be a valid .pdf file. Received: {filepath}"
        logger.error(msg)
        click.echo(json.dumps({"error": msg, "success": False}))
        sys.exit(1)
        
    logger.info(f"Converting PDF to Markdown: {target_path.name}")
    result = _convert_single_pdf(target_path)
    
    click.echo(json.dumps(result, indent=2))
    
    if result["success"]:
        logger.info(f"✓ Converted {result['file']} in {result['time_seconds']}s")
    else:
        logger.error(f"❌ Failed to convert {result['file']}: {result.get('error')}")


@convert.command("dir")
@click.argument("directory")
def convert_dir(directory: str):
    """Convert all PDF files in a directory to Markdown.
    
    Inputs:
      directory : Absolute or relative path to the directory containing PDFs.
      
    Output Schema (JSON):
      {
        "success": true,
        "directory": "/absolute/path/to/transcripts",
        "converted": 5,
        "failed": 0,
        "total_time_seconds": 34.2,
        "results": [
           {"file": "file1.pdf", "success": true, "time_seconds": 5.1, ...}
        ]
      }
    """
    import time
    configure_logging()
    target_dir = Path(directory)
    
    if not target_dir.exists() or not target_dir.is_dir():
        msg = f"Directory not found or invalid: {directory}"
        logger.error(msg)
        click.echo(json.dumps({"error": msg, "success": False}))
        sys.exit(1)
        
    pdf_files = list(target_dir.glob("*.pdf"))
    if not pdf_files:
        msg = f"No .pdf files found in directory: {directory}"
        logger.warning(msg)
        click.echo(json.dumps({"error": msg, "success": False}))
        sys.exit(1)
        
    logger.info(f"Found {len(pdf_files)} PDFs in {target_dir.name}. Starting conversion...")
    
    start_time = time.time()
    results = []
    success_count = 0
    
    for pdf in pdf_files:
        logger.info(f"Processing: {pdf.name}")
        res = _convert_single_pdf(pdf)
        results.append(res)
        if res["success"]:
            success_count += 1
            
    final_output = {
        "success": success_count > 0,
        "directory": str(target_dir.absolute()),
        "converted": success_count,
        "failed": len(pdf_files) - success_count,
        "total_time_seconds": round(time.time() - start_time, 2),
        "results": results
    }
    
    click.echo(json.dumps(final_output, indent=2))
    logger.info(f"Finished directory conversion. {success_count}/{len(pdf_files)} successful.")


if __name__ == "__main__":
    main()
