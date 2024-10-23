import os
import io
import fitz
import sqlite3
import pdfplumber
from PIL import Image
from io import BytesIO

class DataExtractor:
    """
    Extracts text, images, tables, and links from PDF, DOCX, and PPTX files.
    """
    def __init__(self, loader):
        """
        Initialize with the loaded file and file path.
        """
        self.file = loader.file
        self.file_path = loader.file_path
        self.file_type = os.path.splitext(loader.file_path)[1][1:]

    def extract_text(self):
        """
        Extract text and metadata from the file based on its type.
        """
        metadata = {}
        if self.file_type == 'pdf':    
            text = "".join([page.extract_text() or "" for page in self.file.pages])
            metadata = self._extract_metadata(self.file.metadata)  # Extract PDF metadata
            return text, metadata

        elif self.file_type == 'docx':
            text = "\n".join([para.text for para in self.file.paragraphs])
            metadata = self._extract_metadata(self.file.core_properties)  # Extract DOCX metadata
            return text, metadata

        elif self.file_type == 'pptx':
            text = "\n".join([shape.text for slide in self.file.slides for shape in slide.shapes if hasattr(shape, "text")])
            metadata = self._extract_metadata(self.file.core_properties)  # Extract PPTX metadata
            return text, metadata

        else:
            raise ValueError("Unsupported file format. Only PDF, DOCX, and PPTX are supported.")
        
    def extract_images(self):
        """
        Extract images from the file based on its type (PDF, DOCX, PPTX).
        """
        images = []
        if self.file_type == 'pdf':
            with fitz.open(self.file_path) as doc:
                for page_num in range(len(doc)):
                    for img in doc[page_num].get_images(full=True):
                        images.append(self._process_image("pdf", img, doc, page_num + 1))  # Process PDF images

        elif self.file_type == 'docx':
            for rel in self.file.part.rels.values():
                if "image" in rel.target_ref:
                    image_blob = rel.target_part.blob
                    images.append(self._process_image("docx", image_blob))  # Process DOCX images

        elif self.file_type == 'pptx':
            for slide_num, slide in enumerate(self.file.slides):
                for shape in slide.shapes:
                    if hasattr(shape, "image") and shape.image:
                        images.append(self._process_image("pptx", shape, slide_num + 1))  # Process PPTX images

        else:
            raise ValueError("Unsupported file format. Only PDF, DOCX, and PPTX are supported.")

        return images    
    

    def extract_tables(self):
        """
        Extract tables from the file based on its type (PDF, DOCX, PPTX).
        """
        tables = []
        if self.file_type == 'pdf':
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    tables.extend(page.extract_tables() or [])  # Extract tables from PDF

        elif self.file_type == 'docx':
            tables = [[self._extract_table_row(row) for row in table.rows] for table in self.file.tables]  # Extract DOCX tables

        elif self.file_type == 'pptx':
            for slide in self.file.slides:
                for shape in slide.shapes:
                    if shape.has_table:
                        tables.append([self._extract_table_row(row) for row in shape.table.rows])  # Extract PPTX tables

        else:
            raise ValueError("Unsupported file format. Only PDF, DOCX, and PPTX are supported.")

        return tables

    def extract_links(self):
        """
        Extract links from the file based on its type (PDF, DOCX, PPTX).
        """
        links = []
        if self.file_type == 'pdf':
            with fitz.open(self.file_path) as doc:
                for page_num in range(len(doc)):
                    links.extend(self._extract_pdf_link(doc[page_num], page_num + 1))  # Extract PDF links

        elif self.file_type == 'docx':
            for para in self.file.paragraphs:
                for rel in para._p.xpath('.//w:hyperlink'):
                    rId = rel.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                    if rId in para.part.rels:
                        links.append({"url": para.part.rels[rId].target_ref, "page_number": None})  # Extract DOCX links

        elif self.file_type == 'pptx':
            for slide_num, slide in enumerate(self.file.slides):
                for shape in slide.shapes:
                    # Check for hyperlinks in PPTX shapes and text
                    if hasattr(shape, "hyperlink") and shape.hyperlink.address:
                        links.append({"url": shape.hyperlink.address, "slide_number": slide_num + 1})
                    if hasattr(shape, "text_frame"):
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                if hasattr(run, "hyperlink") and run.hyperlink.address:
                                    links.append({"url": run.hyperlink.address, "slide_number": slide_num + 1})

        else:
            raise ValueError("Unsupported file format. Only PDF, DOCX, and PPTX are supported.")

        return links
        

    def _extract_metadata(self, properties):
        """
        Extract metadata from the file properties for DOCX and PPTX files.
        """
        return {
            "author": getattr(properties, 'author', ''),
            "created": getattr(properties, 'created', ''),
            "last_modified_by": getattr(properties, 'last_modified_by', ''),
            "title": getattr(properties, 'title', '')
        }
              
    def _process_image(self, file_type, img, doc=None, page_number=None):
        """
        Process images from PDF, DOCX, and PPTX files.
        """
        if file_type == "pdf":
            base_image = doc.extract_image(img[0])  # Extract image from PDF
            return {
                "image": sqlite3.Binary(base_image["image"]),
                "image_format": base_image["ext"],
                "image_resolution": f"{base_image['width']}x{base_image['height']}",
                "page_number": page_number
            }
        elif file_type == "docx":
            image_blob = img  # Directly use the blob for DOCX
            image = Image.open(BytesIO(image_blob))
            return {
                "image": sqlite3.Binary(image_blob),
                "image_format": image.format.lower(),
                "image_resolution": f"{image.width}x{image.height}",
            }
        elif file_type == "pptx":
            image_blob = io.BytesIO(img.image.blob)  # Extract image from PPTX
            img = Image.open(image_blob)
            return {
                "image": sqlite3.Binary(image_blob.getvalue()),
                "image_format": img.format.lower(),
                "image_resolution": f"{img.width}x{img.height}",
                "slide_number": page_number
            }
        else:
            raise ValueError("Unsupported file type for image processing.")
        
    def _extract_table_row(self, row):
        """
        Extract a row of table data from DOCX or PPTX files.
        """
        return [cell.text.strip() for cell in row.cells]
    
    def _extract_pdf_link(self, page, page_number):
        """
        Extract links from a PDF page and return the URL and page number.
        """
        return [{"url": link.get("uri", ""), "page_number": page_number} for link in page.get_links()]
