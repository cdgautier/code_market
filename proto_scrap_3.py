# Libraries
from selenium import webdriver  # (controller) Import the `webdriver` class from the `selenium` module
from selenium.webdriver.support.ui import WebDriverWait  # espera a que carguen los elementos para realizar cualquier operación
from selenium.webdriver.support import expected_conditions as EC  # Import `expected_conditions` from the `selenium.webdriver.support` module
from selenium.webdriver.common.by import By  # Import `By` from the `selenium.webdriver.common` module
import time  # Import the `time` module
import pandas as pd  # Import the `pandas` library as `pd`
import requests
import os
import re
import parameters as p

wait_time_1 = p.WAIT_TIME_1
wait_time_2 = p.WAIT_TIME_2
wait_time_3 = p.WAIT_TIME_3
wait_time_4 = p.WAIT_TIME_4
wait_time_5 = p.WAIT_TIME_5
wait_time_6 = p.WAIT_TIME_6

# Crear las carpetas si no existen
path_docs = p.PATH_DATA + p.PATHR_DISCRS
path_discr = "C:\\WS_Systep\\Scraper_experts\\data\\discrepancias\\discr_01"
path_docu = "C:\\WS_Systep\\Scraper_experts\\data\\discrepancias\\discr_01\\documento_01"
path_attach = "C:\\WS_Systep\\Scraper_experts\\data\\discrepancias\\discr_01\\documento_01\\Adjuntos"

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    os.makedirs(path, exist_ok=True)

def change_directory(xpath_name, start, end):
    name = driver.find_element(By.XPATH, xpath_name)
    name = name.text
    path_start = os.path.join(start, name)
    path_endd = os.path.join(end, name)

    if not os.path.exists(path_start):
        # Extraer el nombre del archivo sin la extensión .pdf
        match = re.match(r'^(.*)\.pdf$', name)
        if match:
            name = match.group(1)
        else:
            print("El nombre del archivo no tiene la extensión .pdf")
        error_message = "ERROR - Archivo no encontrado" 
        path_start = os.path.join(start, name + ".txt")
        path_endd = os.path.join(end, name + ".txt")
        with open(path_start, 'w') as error_file:
            error_file.write(error_message)
    os.rename(path_start, path_endd)  # Mover el archivo a la carpeta destino

def driver_init():
    # Navigation options
    options = webdriver.ChromeOptions()  
    options.add_argument('--start-maximized')  # Argument to maximize the window upon start
    options.add_argument('--disable-extensions')  # Argument to disable browser extensions
    options.add_experimental_option('prefs', {
    "download.default_directory": path_docs, #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    #"download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
    })

    driver = webdriver.Chrome(options=options) # Configure Chrome browser options
    return driver

def num_rows_table(driver, path):
    table_adjo = driver.find_element(By.XPATH, path)    # Esperar a que la tabla esté presente en la página
    rows = table_adjo.find_elements(By.XPATH, './/tr')  # Obtener todas las filas de la tabla
    num_rows = len(rows)    # Contar el número de filas
    return num_rows

create_folder(path_docs)
create_folder(path_docu)
create_folder(path_attach)

driver = driver_init()
driver.maximize_window()  # Maximize the browser window
time.sleep(p.WAIT_TIME_1)  # Wait for 1 second
driver.get(p.MAIN_PAGE)  # Open the website 

# buttons paths
xpath_btn_discr = p.XPATH_BTN_DISCR_L + str(1) + p.XPATH_BTN_DISCR_R
xpath_btn_doc = p.XPATH_BTN_DOC_L + str(1) + p.XPATH_BTN_DOC_R

# Espera hasta
WebDriverWait(driver, wait_time_6)\
    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_NEW_DISCR)))

# FOR 1
# click on  discrepancy
WebDriverWait(driver, wait_time_2)\
    .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_discr))).click()

url_obtenida = driver.current_url
print(url_obtenida)

# click en expediente
WebDriverWait(driver, wait_time_2)\
    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_EXPED))).click()

# FOR 2
# click en documento
WebDriverWait(driver, wait_time_2)\
    .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_doc))).click()  
                           
# click en principal
WebDriverWait(driver, wait_time_2)\
    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_PPAL))).click()

# click en boton de descarga archivo principal
WebDriverWait(driver, wait_time_2)\
    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_PPAL_DWLD))).click()

time.sleep(wait_time_3)  # Esperar a que el archivo se descargue completamente

change_directory(p.XPATH_NAME_PPAL, path_docs, path_docu)

# FOR 3 - CHECK
# click en adjunto
WebDriverWait(driver, wait_time_2).\
    until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_ADJO))).click()

num_rows_adjo = num_rows_table(driver, p.XPATH_TAB_ADJO)
 
for i in range(num_rows_adjo):
    # click en boton de descarga archivo adjunto i
    xpath_btn_adjo_dwld = p.XPATH_BTN_ADJO_DWLD_L + str(i+1) + p.XPATH_BTN_ADJO_DWLD_R
    xpath_name_adjo = p.XPATH_NAME_ADJO_L + str(i+1) + p.XPATH_NAME_ADJO_R

    WebDriverWait(driver, wait_time_2).\
        until(EC.element_to_be_clickable((By.XPATH, xpath_btn_adjo_dwld))).click()
    time.sleep(wait_time_3)  # Esperar a que el primer archivo adjunto se descargue completamente
    
    change_directory(xpath_name_adjo, path_docs, path_attach)

    # extrae data de las discrepancias (DB1):
    # id_dcpy | título | enlace | número | fecha y hora ingreso | materia | submateria | fecha audiencia | interesados | estado 
    
    # extrae data de una discrepancia especifica (DB2):
    # id_dcpy | id_document | fecha y hora publicacion | principal.txt | adj1.txt | ... | adjn.txt

    # sube la data de las discrepancias a la <DB1> como texto plano 
    # sube los documentos a la <DB2> como texto plano 

    # devuelve cant de palabras en cada archivo del documento y para cada documento (i,j) y el path de la discrepancia 

    # en la carpeta Documentos| se desarga en formato txt la data de las discrepancias en el archivo info_discrepancias.txt

    # en la carpeta Documentos|discrepancia_XX se crea un archivo .txt con la data de una discrepancia especifica
    # en esta carpeta tambien se descarga el .pdf principal y los adjuntos en la carpeta adjuntos

# Close the browser
time.sleep(wait_time_4)  # Wait for 60 second
driver.quit()