from pathlib import Path

from pypdf import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text(filename: str, data: bytes) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported resume format. Use PDF, DOCX, or TXT.")

    if extension == ".txt":
        return data.decode("utf-8", errors="ignore").strip()

    if extension == ".pdf":
        import io

        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    import io

    document = Document(io.BytesIO(data))
    return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
