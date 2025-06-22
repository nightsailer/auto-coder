# Minimal stub for RAG loaders - AutoCoder Slim version
# This provides basic compatibility without full loader functionality

def extract_text_from_pdf(*args, **kwargs):
    """Stub implementation for PDF text extraction"""
    print("⚠️ PDF text extraction not available in AutoCoder Slim")
    return ""

def extract_text_from_docx(*args, **kwargs):
    """Stub implementation for DOCX text extraction"""
    print("⚠️ DOCX text extraction not available in AutoCoder Slim")
    return ""

def extract_text_from_ppt(*args, **kwargs):
    """Stub implementation for PPT text extraction"""
    print("⚠️ PPT text extraction not available in AutoCoder Slim") 
    return ""

def extract_text_from_excel(*args, **kwargs):
    """Stub implementation for Excel text extraction"""
    print("⚠️ Excel text extraction not available in AutoCoder Slim")
    return ""

# Default exports for compatibility
__all__ = [
    'extract_text_from_pdf',
    'extract_text_from_docx', 
    'extract_text_from_ppt',
    'extract_text_from_excel'
]
