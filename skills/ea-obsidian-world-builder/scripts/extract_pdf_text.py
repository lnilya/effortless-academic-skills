#!/usr/bin/env python3
"""
extract_pdf_text.py — Extract plain text from a PDF file.

Usage:
    python extract_pdf_text.py <input_pdf> <output_txt>

Tries pdfplumber first (preserves layout better), falls back to pypdf.
Outputs UTF-8 plain text. Reports page count and word count to stderr.
"""

import sys
import os
import re


def clean_text(text: str) -> str:
    """Clean extracted text: normalize whitespace, remove junk characters."""
    if not text:
        return ""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove null bytes and other control characters (keep \n and \t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Collapse runs of blank lines to max 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def extract_with_pdfplumber(pdf_path: str) -> tuple[str, int]:
    """Extract text using pdfplumber. Returns (text, page_count)."""
    import pdfplumber  # type: ignore

    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            try:
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if page_text:
                    pages_text.append(f"[Page {i + 1}]\n{page_text}")
            except Exception as e:
                print(f"  Warning: pdfplumber failed on page {i + 1}: {e}", file=sys.stderr)
    return "\n\n".join(pages_text), page_count


def extract_with_pypdf(pdf_path: str) -> tuple[str, int]:
    """Extract text using pypdf as fallback. Returns (text, page_count)."""
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        from PyPDF2 import PdfReader  # type: ignore

    pages_text = []
    reader = PdfReader(pdf_path)
    page_count = len(reader.pages)
    for i, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(f"[Page {i + 1}]\n{page_text}")
        except Exception as e:
            print(f"  Warning: pypdf failed on page {i + 1}: {e}", file=sys.stderr)
    return "\n\n".join(pages_text), page_count


def extract_pdf(pdf_path: str) -> tuple[str, int, str]:
    """
    Extract text from a PDF. Returns (text, page_count, method_used).
    Tries pdfplumber first, then pypdf.
    """
    # Try pdfplumber
    try:
        text, pages = extract_with_pdfplumber(pdf_path)
        if text.strip():
            return text, pages, "pdfplumber"
        print("  pdfplumber returned empty text, trying pypdf...", file=sys.stderr)
    except ImportError:
        print("  pdfplumber not available, trying pypdf...", file=sys.stderr)
    except Exception as e:
        print(f"  pdfplumber error: {e}, trying pypdf...", file=sys.stderr)

    # Fallback to pypdf
    try:
        text, pages = extract_with_pypdf(pdf_path)
        return text, pages, "pypdf"
    except ImportError:
        raise RuntimeError(
            "Neither pdfplumber nor pypdf is installed. "
            "Run: pip install pdfplumber --break-system-packages"
        )
    except Exception as e:
        raise RuntimeError(f"All PDF extraction methods failed: {e}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_pdf> <output_txt>", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting: {os.path.basename(pdf_path)}", file=sys.stderr)

    try:
        raw_text, page_count, method = extract_pdf(pdf_path)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    text = clean_text(raw_text)
    word_count = len(text.split())

    # Warn if very little text was extracted (likely scanned PDF)
    if word_count < 200:
        print(
            f"  WARNING: Only {word_count} words extracted from {page_count} pages. "
            "This PDF may be image-based (scanned). OCR not available.",
            file=sys.stderr,
        )

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(
        f"  Done: {page_count} pages, {word_count} words extracted via {method} → {output_path}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
