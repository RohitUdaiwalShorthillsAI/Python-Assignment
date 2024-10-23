from tabulate import tabulate

class Show:
    """
    Class to display extracted data including text, metadata, images, links, and tables.
    """

    def __init__(self, file_type, data):
        """
        Initialize Show class with file type and extracted data.
        
        :param file_type: The type of file (e.g., pdf, pptx, docx).
        :param data: Dictionary containing extracted content.
        """
        self.file_type = file_type
        self.data = data

    def display_extracted_data(self):
        """
        Display the extracted data (text, metadata, images, links, tables) for the given file type.
        """

        def display_metadata(metadata, allowed_keys):
            """
            Display metadata only for allowed keys.

            :param metadata: Extracted metadata as a dictionary.
            :param allowed_keys: List of keys to display from metadata.
            """
            for key, value in metadata.items():
                if key in allowed_keys:
                    print(f"{key.capitalize()}: {value}")

        print(f"\n========== Extracted Data from {self.file_type.upper()} ==========\n")

        # Display extracted text if available
        if 'text' in self.data:
            text, metadata = self.data['text']
            print("----- Extracted Text -----\n")
            print(text[:500] + '...' if len(text) > 500 else text)  # Display first 500 characters of text

        # Define and display metadata based on file type
        metadata_keys = {
            'pdf': ['author', 'title', 'subject', 'keywords', 'created', 'modified', 'producer'],
            'pptx': ['author', 'title', 'slide_count', 'created', 'last_modified_by', 'company', 'category'],
            'docx': ['author', 'title', 'revision', 'created', 'last_modified_by', 'word_count', 'character_count']
        }
        display_metadata(metadata, metadata_keys.get(self.file_type, []))

        # Display images if present with their metadata
        if 'images' in self.data and self.data['images']:
            print(f"----- Extracted Images ({self.file_type.upper()}) -----\n")
            location_key = {'pptx': 'slide_number', 'pdf': 'page_number', 'docx': 'section'}
            for idx, image in enumerate(self.data['images']):
                print(f"Image {idx + 1}: Format: {image['image_format']}, Resolution: {image['image_resolution']}, "
                      f"{location_key[self.file_type].capitalize()}: {image.get(location_key[self.file_type], 'N/A')}")
            print("\n")

        # Display extracted links if available
        if 'links' in self.data and self.data['links']:
            print("----- Extracted Links -----\n")
            location_key = {'pptx': 'slide_number', 'pdf': 'page_number', 'docx': 'section'}
            for link in self.data['links']:
                print(f"URL: {link['url']} ({location_key[self.file_type].capitalize()} {link.get(location_key[self.file_type], 'N/A')})")
            print("\n")

        # Display tables if available
        if 'tables' in self.data and self.data['tables']:
            print(f"----- Extracted Tables ({self.file_type.upper()}) -----\n")
            for table_id, table in enumerate(self.data['tables']):
                print(f"Table {table_id + 1}:\n")
                print(tabulate(table, headers="firstrow", tablefmt="grid"))  # Display table using 'tabulate'
                print("\n-----------------------------\n")

        print(f"========== End of Extraction for {self.file_type.upper()} ==========\n")
