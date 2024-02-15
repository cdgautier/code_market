import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

#------------------------------------------------------------------------------

from db import DB_sql, DB_test
from alarm import Alarm
from scraper.noticias.electromineria import Scraper_Electromineria

#------------------------------------------------------------------------------

# Database
db = DB_sql(path_db=Path(r"tests/Bases de datos/db.db"))

# Scraper
scraper = Scraper_Electromineria(
    path_files=Path(r"tests/Documentos/CNE_tarificacion"),
    db=db
)

# Scraping
scraper.update()

# Alarm
alarm = Alarm(
    {'EM': db},
    {'EM': scraper},
    [['sandoval.hector2002@gmail.com', '13:31', ['EM']],
      ['hector.sabbath666@gmail.com', '13:32', ['EM']]]
)

alarm.alarm_programer()
alarm.run_alarms()

#------------------------------------------------------------------------------

