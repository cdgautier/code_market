import os

def path_maker(*args):
    return os.path.join(*args)

# C:\WS_Systep\Scraper_experts\data

# Ruta independiente del sistema operativo
#PATH_DRIVER = path_maker('C:', 'Users', 'Usuario', 'Downloads', 'chromedriver_win32', 'chromedriver.exe')
PATH_DATA = path_maker('Scraper_experts', 'data')
PATH_DB = path_maker('Scraper_experts', 'data', 'DB', 'db.db')
PATH_DISCRS = path_maker('Scraper_experts', 'data', 'discrepancias')
PATHR_ATTACH = 'adjuntos' 
PATH_INIT_DOWNLOAD = 'C:\WS_Systep\Scraper_experts\data\discrepancias'

MAIN_PAGE = 'https://discrepancias.panelexpertos.cl/'

CANT_WORDS = 20

XPATH_BTN_NEW_DISCR = '/html/body/div[1]/div/div/div/div/div[2]/div/div[3]/button/span[2]'

XPATH_BTN_LAST_TABLE = '/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/nav/ul/li[8]'

XPATH_BTN_ACTUAL_TABLE = '/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/nav/ul/li[9]/button'
                  
XPATH_BTN_DISCR_L = '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/table/tbody/tr['
XPATH_BTN_DISCR_R = ']'

XPATH_BTN_EXPED = '/html/body/div[1]/div/div/div/div/div[2]/div[2]/div[1]/button'        
XPATH_BTN_INTER = '/html/body/div[1]/div/div/div/div/div[2]/div[2]/div[2]/button'

XPATH_TAB_INTER = '/html/body/div[1]/div/div/div/div/div[2]/div[4]'

XPATH_BTN_COMP_INTER_L = '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div['
XPATH_BTN_COMP_INTER_R = ']/nav/a'

XPATH_NAME_COMP_INTER_L = '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div['
XPATH_NAME_COMP_INTER_R = ']/nav/a/div[2]/span'

XPATH_TAB_PERS_INTER = '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div[1]/nav/div/div/div/a'

XPATH_NAME_PERS_INTER_V1_L = '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div['
XPATH_NAME_PERS_INTER_V1_R = ']/nav/div/div/div/a/div/div/span'

XPATH_NAME_PERS_INTER_V2_L = '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div['
XPATH_NAME_PERS_INTER_V2_M = ']/nav/div/div/div/a/div['
XPATH_NAME_PERS_INTER_V2_R = ']/div/span'

XPATH_TAB_DOCS = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]'

XPATH_BTN_DOC_L = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]/a['
XPATH_BTN_DOC_R = ']'

XPATH_NAME_DOC_L = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]/a['
XPATH_NAME_DOC_R = ']/ul/div[1]/span/p[1]'

XPATH_DATE_DOC_L = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]/a['
XPATH_DATE_DOC_R = ']/ul/div[1]/span/p[2]'

XPATH_TYPE_DOC_L = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]/a['
XPATH_TYPE_DOC_R = ']/ul/div[2]/span'

XPATH_BTN_PPAL = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[1]/div/div/div/button[1]'
XPATH_BTN_ADJO = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[1]/div/div/div/button[2]'

XPATH_BTN_PPAL_DWLD = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/p/div/table/tr/td[5]/button'
        
XPATH_BTN_ADJO_DWLD_L = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[3]/div/p/div/table/tr['
XPATH_BTN_ADJO_DWLD_R = ']/td[5]/button'
            
XPATH_NAME_PPAL = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/p/div/table/tr/td[1]'

XPATH_TAB_ADJO = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[3]/div/p/div/table'

XPATH_NAME_ADJO_L = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[3]/div/p/div/table/tr['
XPATH_NAME_ADJO_R = ']/td[1]'

XPATH_BTN_RETURN = '/html/body/div[1]/header/div/div[2]/button[1]'

XPATH_TAB_DISCRS = '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/table/tbody'

WAIT_TIME_1 = 1
WAIT_TIME_2 = 5
WAIT_TIME_3 = 10
WAIT_TIME_4 = 20
WAIT_TIME_5 = 40
WAIT_TIME_6 = 60

# en pag:          20240125 D1-2024 - Coordinador - Escrito.pdf
# en html:         20240125 D1-2024 - Coordinador  - Escrito.pdf

# en descarga:     20240125 D1-2024 - Coordinador  - Escrito.pdf
# extraido driver: 20240125 D1-2024 - Coordinador - Escrito.pdf
#                  20240125 D1-2024 - Coordinador - Escrito.pdf





        
