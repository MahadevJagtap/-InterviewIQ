"""
Document parser service.
Extracts text content from PDF and DOCX files.
"""

import io
import docx2txt
from pypdf import PdfReader


class DocumentParseError(Exception):
    """Raised when document parsing fails."""
    pass


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file.
    
    Args:
        file_bytes: Raw bytes of the PDF file.
        
    Returns:
        Extracted text content.
        
    Raises:
        DocumentParseError: If the PDF cannot be parsed.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        
        if len(reader.pages) == 0:
            raise DocumentParseError("PDF file has no pages.")
        
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())
        
        full_text = "\n\n".join(text_parts)
        
        if not full_text.strip():
            raise DocumentParseError(
                "Could not extract text from the PDF. "
                "It may be a scanned document (image-based). "
                "Please upload a text-based PDF or a DOCX file."
            )
        
        return full_text
        
    except DocumentParseError:
        raise
    except Exception as e:
        raise DocumentParseError(f"Failed to parse PDF: {str(e)}")


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file.
    
    Args:
        file_bytes: Raw bytes of the DOCX file.
        
    Returns:
        Extracted text content.
        
    Raises:
        DocumentParseError: If the DOCX cannot be parsed.
    """
    try:
        # docx2txt handles paragraphs and embedded tables cleanly
        full_text = docx2txt.process(io.BytesIO(file_bytes))
        
        if not full_text or not full_text.strip():
            raise DocumentParseError("The DOCX file appears to be empty or contains no readable text.")
        
        return full_text.strip()
        
    except DocumentParseError:
        raise
    except Exception as e:
        raise DocumentParseError(f"Failed to parse DOCX: {str(e)}")


def parse_document(filename: str, file_bytes: bytes) -> str:
    """Route to the correct parser based on file extension.
    
    Args:
        filename: Original filename (used to determine format).
        file_bytes: Raw bytes of the file.
        
    Returns:
        Extracted text content.
        
    Raises:
        DocumentParseError: If the file format is unsupported or parsing fails.
    """
    if not file_bytes:
        raise DocumentParseError("The uploaded file is empty.")
    
    lower_name = filename.lower()
    
    if lower_name.endswith(".pdf"):
        return parse_pdf(file_bytes)
    elif lower_name.endswith(".docx"):
        return parse_docx(file_bytes)
    elif lower_name.endswith(".doc"):
        raise DocumentParseError(
            "The .doc format (legacy Word) is not supported. "
            "Please save the file as .docx and upload again."
        )
    else:
        raise DocumentParseError(
            f"Unsupported file format: '{filename}'. "
            "Please upload a PDF (.pdf) or Word (.docx) file."
        )
