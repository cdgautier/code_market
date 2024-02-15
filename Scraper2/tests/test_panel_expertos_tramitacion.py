import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

#------------------------------------------------------------------------------
from db.db import DB_sql
from scraper.panel_de_expertos.scraper_sistema_tramitacion import Scraper_SistemaTramitacion

#------------------------------------------------------------------------------

# Database
db = DB_sql(r"tests/Bases de datos/db.db")

# Scraper
scraper = Scraper_SistemaTramitacion(
    path_files=os.path.abspath(r"tests/Documentos/Discrepancias_SistemaTramitacion"),
    db=db)

# Scraping
activate_reverse = False # set True to activate reverse update
activate_short_path = False # set True to activate reverse update
discr_number = 1 # set the number to start scraping
scraper.update(activate_reverse, activate_short_path, discr_number - 1)






