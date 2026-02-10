import pdfplumber


def extract_tables(pdf_path: str) -> list[list[list[str]]]:
    with pdfplumber.open(pdf_path) as pdf:
        return [
            table
            for page in pdf.pages
            for table in (page.extract_tables() or [])
        ]


def extract_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n\n".join(page.extract_text() or "" for page in pdf.pages)
