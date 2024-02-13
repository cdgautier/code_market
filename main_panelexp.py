import os
import parameters as p
#sys.path.append(str(Path(__file__).resolve().parent.parent))

#------------------------------------------------------------------------------

from db import DB_sql
#from alarm_expl import Alarm
from scraper_panelexp import Scraper_PanelExpertos

#------------------------------------------------------------------------------

# Database
db = DB_sql(p.PATH_DB)

# Scraper
scraper = Scraper_PanelExpertos(
    path_files=os.path.abspath(p.PATH_DISCRS),
    db=db)

# Scraping
scraper.update()

'''

# Alarm
alarm = Alarm(
    {'EM': db},
    {'EM': scraper},
    [['sandoval.hector2002@gmail.com', '13:31', ['EM']],
      ['hector.sabbath666@gmail.com', '13:32', ['EM']]]
)

alarm.alarm_programer()
alarm.run_alarms()

'''

