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
scraper = Scraper_PanelExpertos(db=db)
# Scraping
scraper.update()

