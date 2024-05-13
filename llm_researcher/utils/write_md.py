import aiofiles
import urllib
import uuid
import importlib.util
import os

from md2pdf.core import md2pdf
import mistune
from docx import Document
from htmldocx import HtmlToDocx

module_spec = importlib.util.find_spec(__name__)
package_path = os.path.dirname(module_spec.origin)
PDF_STYLES_PATH = os.path.join(package_path, 'pdf_styles.css')

async def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

async def write_to_file(filename: str, text: str) -> None:
    """Asynchronously write text to a file in UTF-8 encoding.

    Args:
        filename (str): The filename to write to.
        text (str): The text to write.
    """
    directory = os.path.dirname(filename)
    await ensure_directory_exists(directory)

    # Convert text to UTF-8, replacing any problematic characters
    text_utf8 = text.encode('utf-8', errors='replace').decode('utf-8')

    async with aiofiles.open(filename, "w", encoding='utf-8') as file:
        await file.write(text_utf8)

async def write_md_to_pdf(text: str) -> str:
    """Converts Markdown text to a PDF file and returns the file path.

    Args:
        text (str): Markdown text to convert.

    Returns:
        str: The encoded file path of the generated PDF.
    """
    task = uuid.uuid4().hex
    file_path = f"test_output/{task}"
    await write_to_file(f"{file_path}.md", text)

    try:
        md2pdf(f"{file_path}.pdf",
               md_content=None,
               md_file_path=f"{file_path}.md",
               css_file_path=PDF_STYLES_PATH,
               base_url=None)
        print(f"Report written to {file_path}.pdf")
    except Exception as e:
        print(f"Error in converting Markdown to PDF: {e}")
        return ""

    encoded_file_path = urllib.parse.quote(f"{file_path}.pdf")
    return encoded_file_path

async def write_md_to_word(text: str) -> str:
    """Converts Markdown text to a DOCX file and returns the file path.

    Args:
        text (str): Markdown text to convert.

    Returns:
        str: The encoded file path of the generated DOCX.
    """
    task = uuid.uuid4().hex
    file_path = f"outputs/{task}"

    try:
        # Convert report markdown to HTML
        html = mistune.html(text)
        # Create a document object
        doc = Document()
        # Convert the html generated from the report to document format
        HtmlToDocx().add_html_to_document(html, doc)

        # Saving the docx document to file_path
        doc.save(f"{file_path}.docx")
        
        print(f"Report written to {file_path}.docx")

        encoded_file_path = urllib.parse.quote(f"{file_path}.docx")
        return encoded_file_path
    
    except Exception as e:
        print(f"Error in converting Markdown to DOCX: {e}")
        return ""
