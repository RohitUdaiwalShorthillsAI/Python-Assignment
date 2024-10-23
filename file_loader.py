from abc import ABC, abstractmethod
import os
from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation


class FileLoader(ABC):
    """
    Abstract base class for file loaders.
    """
    def __init__(self, file_path, file_type):
        """
        Initialize with file path and file type.
        """
        self.file_path = file_path
        self.file_type = file_type
        self.file = None

    @abstractmethod
    def load_file(self):
        """
        Abstract method to load file content.
        """
        pass


class Loader(FileLoader):
    """
    Concrete loader class for loading PDF, DOCX, and PPTX files.
    """
    
    # Dictionary to map file types to their respective loaders
    file_reader = {
        'pdf': PdfReader,
        'docx': Document,
        'pptx': Presentation,
    }

    def validate_file(self):
        """
        Validate if the file exists and is a supported type.
        """
        if not os.path.exists(self.file_path):
            print("File does not exist.")  # Check if the file exists
            exit()
        # Check file extension and validate type
        if self.file_type in ['pdf', 'docx', 'pptx']:
            print("File is valid.")  # File exists and is valid
        else:
            print("Unsupported file type. Only PDF, DOCX, and PPTX files are supported.")
            exit()

    def load_file(self):
        """
        Load the file based on its type (PDF, DOCX, PPTX).
        """
        try:
            file = self.file_reader[self.file_type](self.file_path)  # Load file using the appropriate reader
            self.file = file  # Store loaded file
        except Exception as e:
            raise ValueError(f"Invalid file : {e}")  # Handle file loading errors
