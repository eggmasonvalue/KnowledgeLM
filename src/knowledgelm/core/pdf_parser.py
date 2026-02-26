"""Module for extracting resolutions from Shareholder Meeting PDF notices."""

import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pdfplumber

logger = logging.getLogger(__name__)


class PDFResolutionExtractor:
    """Extracts resolutions and explanatory statements from PDF notices."""

    def extract_resolutions(self, pdf_path: Path) -> Tuple[List[Dict[str, str]], str]:
        """Extract resolutions from a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Tuple containing:
            1. List of dictionaries with resolution details.
            2. The full extracted raw text from the PDF.
        """
        text = self._extract_text(pdf_path)
        if not text:
            logger.warning(f"No text extracted from PDF: {pdf_path}")
            return [], ""

        # Split into Notice and Explanatory Statement sections
        # Common headers: "EXPLANATORY STATEMENT", "STATEMENT PURSUANT TO SECTION 102"
        # We look for this header, usually in uppercase, centered or start of line.
        # We use (?:\n|^) to ensure it's a header line, not just a mention in text.
        split_pattern = re.compile(
            r"(?:\n|^)\s*(?:EXPLANATORY\s+STATEMENT|STATEMENT\s+PURSUANT\s+TO\s+SECTION\s+102)",
            re.IGNORECASE,
        )
        match = split_pattern.search(text)

        if match:
            notice_text = text[: match.start()]
            explanation_text = text[match.end() :]
            logger.info(
                f"Found Explanatory Statement section. "
                f"Notice len: {len(notice_text)}, Exp len: {len(explanation_text)}"
            )
        else:
            notice_text = text
            explanation_text = ""
            logger.info("No separate Explanatory Statement section found.")

        # Parse items from both sections
        raw_resolutions = self._parse_items(notice_text)
        logger.info(f"Found {len(raw_resolutions)} items in notice section.")

        raw_explanations = (
            self._parse_items(explanation_text) if explanation_text else []
        )
        logger.info(f"Found {len(raw_explanations)} items in explanation section.")

        # Fallback: If no resolutions found in notice section, but we have items in explanation
        # (meaning maybe the split was wrong or notice is interleaved),
        # use the explanation items as resolutions too.
        if not raw_resolutions and raw_explanations:
            logger.warning(
                "No resolutions in Notice section. Using Explanation items as resolutions."
            )
            raw_resolutions = raw_explanations
        elif not raw_resolutions and not raw_explanations:
            # Try parsing full text if everything failed
             logger.warning("No items found in split sections. Trying full text.")
             raw_resolutions = self._parse_items(text)

        # Deduplicate resolutions (prefer longer text to avoid ToC entries)
        unique_resolutions = {}
        for res in raw_resolutions:
            item_no = res["item_no"]
            if item_no not in unique_resolutions:
                unique_resolutions[item_no] = res
            else:
                if len(res["text"]) > len(unique_resolutions[item_no]["text"]):
                    unique_resolutions[item_no] = res

        # Map explanations by item_no
        unique_explanations = {}
        for exp in raw_explanations:
            item_no = exp["item_no"]
            if item_no not in unique_explanations:
                unique_explanations[item_no] = exp
            else:
                # Append if multiple sections for same item?
                # Sometimes explanation is split.
                unique_explanations[item_no]["text"] += " " + exp["text"]

        merged = []
        # Sort by item number (numerically if possible)
        def sort_key(k):
            try:
                return int(k)
            except ValueError:
                return 999

        sorted_keys = sorted(unique_resolutions.keys(), key=sort_key)

        for item_no in sorted_keys:
            res = unique_resolutions[item_no]
            exp = unique_explanations.get(item_no)

            description = self._clean_text(res["text"])
            explanation = self._clean_text(exp["text"]) if exp else ""

            # Identify Resolution Type
            res_type = "Unknown"
            desc_lower = description.lower()
            if "ordinary resolution" in desc_lower:
                res_type = "Ordinary"
            elif "special resolution" in desc_lower:
                res_type = "Special"

            merged.append(
                {
                    "item_no": item_no,
                    "description": description,
                    "resolution_type": res_type,
                    "explanatory_statement": explanation,
                }
            )

        return merged, text

    def _extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using pdfplumber."""
        full_text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
        return full_text

    def _parse_items(self, text: str) -> List[Dict[str, str]]:
        """Parse text into items based on 'Item No.' regex.

        Returns:
            List of dicts with 'item_no' and 'text'.
        """
        # Regex to find "Item No. X" or "Resolution No. X"
        # We use a pattern that attempts to be robust against spacing
        item_pattern = re.compile(
            r"(?:Item|Resolution)\s*(?:No\.?)?\s*(\d+)", re.IGNORECASE
        )

        matches = list(item_pattern.finditer(text))
        items = []

        if not matches:
            return []

        for i, match in enumerate(matches):
            item_no = match.group(1)
            start_pos = match.end()

            # End position is the start of the next match or end of text
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(text)

            content = text[start_pos:end_pos].strip()
            items.append({"item_no": item_no, "text": content})

        return items

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Replace newlines with spaces, remove multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text
