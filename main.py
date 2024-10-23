import os
from file_loader import Loader
from file_extractor import DataExtractor
from storage import FileStorage
from storage import MySQLStorage
from show_data import DisplayData

class Main:
    """
    Main class to handle file processing, data extraction, 
    and storage based on the user-selected method.
    """
    def __init__(self, filePath, storage_type):
        """
        Initialize the Main class with file path and storage type.
        """
        self.file_path = filePath
        self.storage_type = storage_type

    def run(self):
        """
        Main function to validate the file and process it.
        """
        # Extract the file extension
        file_type = os.path.splitext(filePath)[1][1:]  # Extracts the file extension
        self.file_type = file_type
        # Validate file type and path
        Loader(self.file_path, self.file_type).validate_file()
        
        # Process the file contents
        self.process_file()

    def process_file(self):
        """
        Load, extract, display, and store data from the file.
        """
        self.storage_path = f"./output/{os.path.basename(self.file_path)}_files"
        print(f"Processing {self.file_type.upper()} file: {self.file_path}")

        # Load the file contents
        loader = Loader(self.file_path, self.file_type)
        loader.load_file()

        # Extract data from the file
        extractor = DataExtractor(loader)
        data = {
            'text': extractor.extract_text(),
            'links': extractor.extract_links(),
            'images': extractor.extract_images(),
            'tables': extractor.extract_tables(),
        }

        # Optionally display the extracted data
        ch = input("Do you want to show data(y/n) :: ")
        if ch == 'y':
            show = DisplayData(self.file_type, data)
            show.display_extracted_data()

        # Save the data to file or SQL based on user choice
        if self.storage_type == "file":
            if not self.storage_path:
                raise ValueError("Storage path is required for file storage.")
            storage = FileStorage(extractor, self.storage_path)
        else:
            storage = MySQLStorage(extractor)
        
        # Save extracted data
        storage.save()


if __name__ == "__main__":
    # Input file path and storage type from user
    filePath = input("Enter File Path : ")
    storage_type = input("Enter the storage type (sql or file): ")
    
    # Create an instance and run the main process
    instance = Main(filePath, storage_type)
    instance.run()
