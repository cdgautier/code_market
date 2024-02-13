import os
from db import DB_sql  # Importa la clase DB_sql desde el módulo db_expl

# Definición de la clase Scraper
class Scraper:

    # Método constructor
    def __init__(self,  db):
        # Inicialización de variables de instancia
        self.db = db  # Instancia de la base de datos

        

    # Método para crear una nueva tabla en la base de datos
    def new_table(self, table, columns):
        self.db.new_table(table, columns)

    # Método para agregar una nueva fila a una tabla en la base de datos
    def new_row(self, table, row):
        return self.db.new_row(table, row)

    # Método para agregar múltiples filas a una tabla en la base de datos
    def new_rows(self, table, rows):
        self.db.new_rows(table, rows)
        
    # Método para actualizar una fila en una tabla de la base de datos
    def update_row(self, table: str, id_column: str, row_id: int, new_data: dict):
        self.db.update_row(table, id_column, row_id, new_data)

    # Método para crear una carpeta donde se guardarán los archivos descargados
    #def create_folder(self, path):
    #    if not os.path.exists(path):
    #        os.makedirs(path)
    #    os.makedirs(path, exist_ok=True)

    # Método para actualizar los datos (por implementar)
    # def update(self):
    #    pass  # Tarea de actualización aún no implementada

# -----------------------------------------------------------------------------

