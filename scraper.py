import os
from db import DB_sql

# -----------------------------------------------------------------------------

class Scraper:

    def __init__(self, path_files, db):

        self.path_files = path_files
        self.db = db

        # Create folder to save downloads
        self.create_folder()

    def new_table(self, table, columns):
        self.db.new_table(table, columns)

    def new_row(self, table, row):
        return self.db.new_row(table, row)

    def new_rows(self, table, rows):
        self.db.new_rows(table, rows)
        
    def update_row(self, table: str, id_column: str, row_id: int, new_data: dict):
        self.db.update_row(table, id_column, row_id, new_data)

    # Create folder to save downloads
    def create_folder(self):
        os.makedirs(self.path_files, exist_ok=True)


    def update(self):
        pass

# -----------------------------------------------------------------------------

