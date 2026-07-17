# loaders/pdf.py
import logging
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from loaders.base import DocumentLoader

logger = logging.getLogger(__name__)

class PDFLoader(DocumentLoader):
    """
    Extracts text from PDF files.
    Uses pdfplumber for native text. Falls back to Tesseract OCR for scanned pages.
    """
    
    def load(self, file_path: str) -> str:
        logger.info(f"[LOADER] Extracting text from PDF: {file_path}")
        full_text = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    
                    # Heuristic: If extracted text is too short, assume it's a scanned page
                    if not page_text or len(page_text.strip()) < 50:
                        logger.info(f"[LOADER] Page {i+1} appears scanned. Falling back to OCR.")
                        page_text = self._perform_ocr(file_path, i + 1)
                    
                    # Add clear page delimiters for future metadata extraction
                    full_text.append(f"\n--- Page {i+1} ---\n{page_text}")
                    
        except Exception as e:
            logger.error(f"[LOADER] Critical error reading PDF {file_path}: {e}")
            raise
            
        return "\n".join(full_text)

    def _perform_ocr(self, file_path: str, page_number: int) -> str:
        """Helper method to perform OCR on a specific page."""
        try:
            # Convert only the specific page to an image
            images = convert_from_path(
                file_path, 
                first_page=page_number, 
                last_page=page_number,
                dpi=300  # Higher DPI for better OCR accuracy
            )
            if images:
                # Perform OCR using Tesseract
                return pytesseract.image_to_string(images[0])
            return "[OCR Failed: No image generated]"
        except Exception as e:
            logger.error(f"[LOADER] OCR failed for page {page_number}: {e}")
            return f"[OCR Failed: {str(e)}]"