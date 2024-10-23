# Python-Assignment

# Extract Text, Links, Images, and Tables from PDF, DOCX, and PPT with Metadata
 
## Assignment Overview
 
This Assignment provides a modular Python class structure for extracting text, hyperlinks, images, and tables from **PDF**, **DOCX**, and **PPT** files, while capturing metadata such as page numbers, font styles, and dimensions. The extracted data is stored in local files and in an SQL database.
 
## Features
 
- **Text Extraction:** Extracts text and metadata such as page numbers, headings, and font styles.
- **Link Extraction:** Extracts hyperlinks and metadata like the linked text, URL, and page number.
- **Image Extraction:** Extracts images and metadata such as resolution, format, and page number.
- **Table Extraction:** Extracts tables and metadata such as dimensions and page numbers.
- **Storage Options:** Supports storing extracted data either as files or in an SQL database.
 
## Assignment Folder Structure
```
Assignment3-Python/
├── file_loader.py             # Class for loading and processing PDF, DOCX and PPTX files
|── file_extractor.py          # Class for extracting links, images, texts and tables
├── storage.py                 # Class for storage handling
├── tests/                     # Directory containing test files (PDF, DOCX, PPT) for testing
├── output/                    # Directory where extracted files will be stored
├── main.py                    # Script for running the tests and extraction
├── show_data.py               # To optionally show data
└── README.md                  # Project documentation (this file)
```
- Set up a Python virtual environment and install dependencies:
```
python -m venv env
source env/bin/activate   # On Windows use `env\Scripts\activate`
pip freeze > requirements.txt
```
- Set up your MySQL database and create a .env file for MySQL credentials:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=extract_data_db
```
 
```
Dependencies
pdfplumber: For extracting content from PDF files.
PyPDF2: For handling PDF metadata.
python-docx: For extracting data from DOCX files.
python-pptx: For extracting data from PPT files.
Pillow: For handling image files.
mysql-connector-python: For storing metadata in a MySQL database.
```
## Version
- Python Version: 3.10.0
## Usage
- Run the main script:
```
python main.py
```
- The extracted data will be saved in the output/ folder and organized into subfolders based on file type (PDF, DOCX, PPTX). Additionally, data will be stored in the MySQL database.
 
## Features
 
- **Modular Structure**: The project is structured to be modular and extendable, using abstract and concrete classes.
- **File Formats Supported**: 
  - PDF
  - DOCX
  - PPT
- **Data Extraction**: The following data types are extracted:
  - Text
  - Images
  - Hyperlinks
  - Tables
- **Metadata**: The extracted metadata includes file size, author (if available), creation/modification date, and more.
- **Storage Options**: 
  - File-based storage.
  - SQL-based storage using `mysql-connector` (preferred).
- **Unit Testing**: Thorough test cases cover:
  - All supported file types.
  - Edge cases such as missing hyperlinks and complex tables.
 
## How It Works
 
1. **File Loaders**: 
   - Abstract `FileLoader` class with concrete implementations for handling PDF, DOCX, and PPT files.
   - Each loader reads the respective file type and provides a standard interface for extracting data.
 
2. **Data Extraction**:
   - `DataExtractor` class handles the actual extraction of text, images, links, and tables from the files.
   - It interacts with the file loaders to retrieve the data and metadata.
 
3. **Storage**:
   - Data can be stored in either files or an SQL database.
   - The `FileStorage` class handles saving data in a file format, while `SQLStorage` handles saving it into a MySQL database.
 
## Testing
 
The project includes both manual and automated test cases to ensure functionality across different scenarios.
 
- **Manual Testing**:
  - Basic functionality checks for each file type.
  - Edge case scenarios (e.g., handling files with no hyperlinks, complex nested tables).
- **Automated Testing**:
  - Unit tests using Python's `unittest` module to ensure code correctness and coverage.
  - Automated tests cover different file types and edge cases.
