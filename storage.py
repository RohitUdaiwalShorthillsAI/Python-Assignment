import os
import mysql.connector
from dotenv import load_dotenv
from abc import ABC, abstractmethod
import csv

class FileStorage():
    def __init__(self, extractor, output_dir):
        """
        Initialize FileStorage with an extractor and output directory.

        :param extractor: An instance of the data extractor.
        :param output_dir: The directory where extracted data will be saved.
        """
        self.extractor = extractor
        self.output_dir = output_dir
        # Create the output directory if it does not exist
        os.makedirs(self.output_dir, exist_ok=True)

    def save(self):
        """
        Save the extracted data (text, metadata, images, links, tables) to the specified output directory.
        """
        # Save extracted text
        text, metadata = self.extractor.extract_text()
        text_file_path = os.path.join(self.output_dir, 'extracted_text.txt')
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text)

        # Save metadata to a separate file
        metadata_file_path = os.path.join(self.output_dir, "metadata.txt")
        with open(metadata_file_path, "w") as metadata_file:
            for key, value in metadata.items():
                metadata_file.write(f"{key}: {value}\n")

        # Save extracted links
        links = self.extractor.extract_links()
        links_file_path = os.path.join(self.output_dir, 'extracted_links.txt')
        with open(links_file_path, 'w', encoding='utf-8') as links_file:
            for link in links:
                links_file.write(f"{link['url']} (Page/Slide: {link.get('page_number', link.get('slide_number'))})\n")

        # Save extracted images
        images = self.extractor.extract_images()
        images_dir = os.path.join(self.output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        for idx, img in enumerate(images):
            image_file_path = os.path.join(images_dir, f'image_{idx+1}.{img["image_format"]}')
            with open(image_file_path, 'wb') as image_file:
                image_file.write(img['image'])

        # Save extracted tables to CSV files
        tables = self.extractor.extract_tables()
        for table_id, table in enumerate(tables):
            table_file_path = os.path.join(self.output_dir, f'table_{table_id+1}.csv')
            with open(table_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                for row in table:
                    writer.writerow(row)  # Write each row of the table to the CSV file

        print(f"Data saved to file system in directory {self.output_dir}")


class MySQLStorage():
    table_name = 1

    def __init__(self, extractor):
        """
        Initialize MySQLStorage with an extractor and create necessary database tables.

        :param extractor: An instance of the data extractor.
        """
        load_dotenv()  # Load environment variables

        self.extractor = extractor
        self.conn = mysql.connector.connect(
            host= os.getenv('DB_HOST'),
            user= os.getenv('DB_USER'),
            password= os.getenv('DB_PASSWORD'),
            database= os.getenv('DB_DATABASE'),  # MySQL database name
            auth_plugin='mysql_native_password'  # Use the native authentication plugin
        )
        self.cursor = self.conn.cursor()  # Create a cursor to interact with the database
        self.create_tables()  # Create tables if they don't exist

    def create_tables(self):
        """
        Create tables for storing extracted text, links, images, and tables in the MySQL database.
        The tables are created if they do not already exist.
        """
        # Create tables for text, links, and images
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS extracted_text (content TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS extracted_links (link TEXT, page_number INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS extracted_images (image LONGBLOB, image_format TEXT, resolution TEXT, page_number INTEGER)''')
        self.conn.commit()  # Commit the table creation to the database

    def save(self):
        """
        Save the extracted data (text, links, images, tables) to the MySQL database.
        """
        # Save extracted text
        text_content, _ = self.extractor.extract_text()  # Extract the text, discard metadata
        if text_content:  # Only insert if there is text data
            self.cursor.execute('INSERT INTO extracted_text (content) VALUES (%s)', (text_content,))

        # Save extracted links
        links = self.extractor.extract_links()  # Extract links from the document
        for link in links:
            self.cursor.execute('INSERT INTO extracted_links (link, page_number) VALUES (%s, %s)', 
                                (link['url'], link.get('page_number', link.get('slide_number'))))  # Insert links into the database

        # Save extracted images
        images = self.extractor.extract_images()
        for img in images:
            # Convert memoryview object to bytes before saving to MySQL
            img_data = bytes(img['image'])  # Convert memoryview to bytes
            self.cursor.execute('INSERT INTO extracted_images (image, image_format, resolution, page_number) VALUES (%s, %s, %s, %s)',
                                (img_data, img['image_format'], img['image_resolution'], img.get('page_number', img.get('slide_number'))))

        # Save extracted tables
        tables = self.extractor.extract_tables()  # Extract tables from the document
        for table_id, table in enumerate(tables):
            if not table:  # Skip empty tables
                continue

            # Sanitize column names for SQL compatibility
            sanitized_columns = [col.strip().replace(" ", "_").replace("-", "_").replace(".", "_") for col in table[0]]

            table_name = f'extracted_table_{MySQLStorage.table_name}'  # Unique table name for each table
            MySQLStorage.table_name += 1

            # Create table if not exists, add missing columns if needed
            try:
                self.cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                result = self.cursor.fetchone()

                if result:  # Table exists
                    self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                    existing_columns = [col[0] for col in self.cursor.fetchall()]

                    # Add missing columns
                    for col in sanitized_columns:
                        if col not in existing_columns:
                            self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN `{col}` TEXT")

                else:  # Create new table
                    sanitized_column_defs = [f'`{col}` TEXT' for col in sanitized_columns]
                    create_table_query = f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, {', '.join(sanitized_column_defs)})"
                    self.cursor.execute(create_table_query)

            except mysql.connector.Error as err:
                print(f"Error checking/creating table {table_name}: {err}")
                continue  # Skip to the next table if there's an error

            # Insert table rows
            for row in table[1:]:
                try:
                    insert_query = f"INSERT INTO {table_name} ({', '.join([f'`{col}`' for col in sanitized_columns])}) VALUES ({', '.join(['%s'] * len(row))})"
                    self.cursor.execute(insert_query, tuple(row))  # Insert the row into the table
                except mysql.connector.Error as err:
                    print(f"Error inserting into table {table_name}: {err} for row: {row}")
                    continue  # Skip to the next row if there's an error

        # Commit all inserts
        self.conn.commit()

        print(f"Data saved to MySQL database")

    def close(self):
        """Close the database connection to free up resources."""
        self.conn.close()
