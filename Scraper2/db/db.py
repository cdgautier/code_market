import os
import sqlite3
from pathlib import Path
import numpy as np

# -----------------------------------------------------------------------------

class DB:
    def __init__(self, path_db):

        self.path_db = path_db

        # Create folder to save database
        self.create_folder()


    # Create folder to save database
    def create_folder(self):
        os.makedirs(os.path.dirname(self.path_db), exist_ok=True)


    # Add a list of new elements
    def new_rows(self, table: str, rows: list) -> None:
        for row in range(rows):
            self.new_row(table, row)

# -----------------------------------------------------------------------------

class DB_test(DB):

    def __init__(self, path_db):
        super().__init__(path_db)


    def create_folder(self):
        print(f"Folder for {self.path_db} is created.")


    # Create new table
    def new_table(self, table: str, columns: list) -> None:
        print(f"New table:")
        self.print_row(columns)


    def new_row(self, table: str, row: list) -> None:
        print(f"New row:")
        self.print_row(row)


    def update_row(self, table: str, index: str, new_row: list) -> None:
        print(f"Row '{index}' of Table '{table}' modified. New row:")
        self.print_row(new_row)


    def delete_row(self, table: str, index: str) -> None:
        print(f"Row '{index}' of Table '{table}' deleted.")


    def search_row(self, table: str, index: str) -> list:
        print(f"Row '{index}' is searched.")


    def db_structure(self):
        pass


    def table_structure(self):
        pass


    def print_row(self, row):
        for i in row:
            print(i)

# -----------------------------------------------------------------------------

class DB_sql(DB):

    def __init__(self, path_db):
        super().__init__(path_db)


    def new_table(self, table: str, columns: list) -> None:

        """
        Method for creating a table in the database, constraints must be of the form 
        [("column 1", "data type 1"), ("column 2", "data type 2"),...]", restrictions like uniqueness of elements could be inserted here.
        """

        connection = sqlite3.connect(self.path_db)
        cursor = connection.cursor()
        
        restrictions = ""
        
        for i in range(len(columns)):
            
            restrictions += f"{columns[i][0]} {columns[i][1]},"
            
        restrictions = restrictions[:-1]
        
        try:
            connection.execute('PRAGMA foreign_keys = ON')
            connection.commit()
            
            comando = f"CREATE TABLE IF NOT EXISTS {table} ({restrictions})"
            
            cursor.execute(comando)
            connection.commit()
            
            connection.close()
            
        except Exception as e:
            print(f'Error executing command: {e}')
            connection.close()


    def new_row(self, table: str, row: dict) -> int:

        """
        Method to insert data into a specific table, data must be in the form {'column name': data of that column, ... },
        remember that numbers should be of type int, float, or similar, and text should be of type str.
        """

        connection = sqlite3.connect(self.path_db)
        cursor = connection.cursor()
        
        try:
            
            placeholders = ', '.join(['?' for _ in row])
            columns = ', '.join([list(row.keys())[i] for i in range(len(row))])
            command = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
            valores = tuple(row.values())
            cursor.execute(command, valores)
            
            id_last = cursor.lastrowid
            
            connection.commit()
            connection.close()
            
            return id_last
        
        except Exception as e:
            print(f'Error executing command: {e}')
            connection.close()  
            return None 


    def update_row(self, table: str, id_column: str, row_id: int, new_data: dict) -> bool:
        """
        Method to update data in a specific row of a table.
        :param table: The name of the table to update data in.
        :param id_column: The name of the column containing the ID.
        :param row_id: The ID of the row to update.
        :param new_data: A dictionary containing column names as keys and new data as values.
        :return: True if the update was successful, False otherwise.
        """
        connection = sqlite3.connect(self.path_db)
        cursor = connection.cursor()

        try:
            # Construct the SET part of the SQL query
            set_values = ', '.join([f"{key} = ?" for key in new_data])

            # Construct the parameters for the query
            query_params = tuple(new_data.values())
            query_params += (row_id,)  # Add the row ID to the parameters

            # Construct and execute the SQL query
            command = f"UPDATE {table} SET {set_values} WHERE {id_column} = ?"
            cursor.execute(command, query_params)

            connection.commit()
            connection.close()

            return True

        except Exception as e:
            print(f'Error executing command: {e}')
            connection.close()
            return False


    def delete_row(self, table: str, index: str) -> None:
        
        """
        Method to delete a record from a specific table, the identifier must be in the form ['identifying column (e.g., id)', column value].
        """
        
        connection = sqlite3.connect(self.path_db)
        cursor = connection.cursor()
        
        try:
            
            if type(index[1]) == str:
            
                command = f"DELETE FROM {table} WHERE {index[0]} = '{index[1]}'"
                
            else:
                
                command = f"DELETE FROM {table} WHERE {index[0]} = {index[1]}"
            
            cursor.execute(command)
            connection.commit()
            
            connection.close()
        
        except Exception as e:
            
            print(f'Error executing command: {e}')
            connection.close()   


    def search_row(self, table: str, index: str) -> list:

        """
        Method to search/filter data in a specific table, the identifier must be in the form ['identifying column (e.g., id)', column value].
        """
        
        connection = sqlite3.connect(self.path_db)
        cursor = connection.cursor()
        
        try:
            
            if type(index[1]) == str:
            
                command = f"SELECT * FROM {table} WHERE {index[0]} = '{index[1]}'"
                
            else:
                
                command = f"SELECT * FROM {table} WHERE {index[0]} = {index[1]}"
            
            cursor.execute(command)
            rows = cursor.fetchall()
            
            result = [ data for data in rows]
            
            connection.close()
            
            return result
        
        except Exception as e:
            
            print(f'Error executing command: {e}')
            connection.close() 


    def execute_sql(self, command: str) -> None:
        
        """
        Method to interact directly with the database using SQL commands.
        """
        
        try:
        
            connection = sqlite3.connect(self.path_db)
            cursor = connection.cursor()
            
            cursor.execute(command)
            connection.commit()
            
            connection.close()
        
        except Exception as e:
            
            print(f'Error executing command: {e}')    


    def show_table(self, table: str) -> list:
        
        """
        Method to display the structure of a specific table.
        """
        
        connection = sqlite3.connect(self.path_db)
        cursor = connection.cursor()
        
        command = f"PRAGMA table_info({table})"
        
        try:
            
            cursor.execute(command)
            column_info = cursor.fetchall()
            
            column_names = [(column[1], column[2]) for column in column_info]
            
            connection.close()
            
            return column_names
        
        except Exception as e:
            
            print(f'Error executing command: {e}')
            connection.close()  


    def show_tables_names(self) -> list:
        
        """
        Method to display the names of the tables within the .db file being worked on.
        """
        
        connection = sqlite3.connect(self.path_db)
        cursor = connection.cursor()
        
        try:
        # Obtener los nombres de las tablas en la base de datos
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # Extraer los nombres de las tablas
            tables_names = [table[0] for table in tables]
            
            connection.close()

            return tables_names

        except Exception as e:
            
            print(f'Error executing command: {e}')
            connection.close()   
               

    def search_data_by_date(self, table: str, date_column: str,  starting_date: str, ending_date: str) -> list:
        
        """
        Método para buscar/filtrar datos en alguna tabla en específico según fechas en formato ISO-8601.
        """
        
        connection = sqlite3.connect(self.path_db)
        cursor = connection.cursor()
        
        try:
           
            command = f"SELECT * FROM {table} WHERE {date_column} BETWEEN '{starting_date}' AND '{ending_date}'"

            cursor.execute(command)
            rows = cursor.fetchall()
            
            result = [ data for data in rows]
            
            connection.close()
            
            return result
        
        except Exception as e:
            
            print(f'Error executing command: {e}')
            connection.close() 
            
            
    def table_as_array(self, table) -> np.ndarray:

        connection = sqlite3.connect(self.path_db)
        cursor = connection.cursor()

        try:

            # Ejecutar una consulta SQL para seleccionar todos los datos de la tabla
            command = f"SELECT * FROM {table}"
            cursor.execute(command)

            # Obtener todos los resultados como una lista de tuplas
            data = cursor.fetchall()

            # Cerrar la conexión a la base de datos
            connection.close()

            # Convertir la lista de tuplas a un array NumPy
            array = np.array(data)

            return array
            
        except Exception as e:
            
            print(f'Error executing command: {e}')
            connection.close() 
            
# -----------------------------------------------------------------------------
