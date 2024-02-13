# Libraries
import os
import re
import requests
import time  # Import the `time` module
#import pandas as pd  # Import the `pandas` library as `pd`
import parameters as p
#from pathlib import Path # Maneja rutas de archivos
from bs4 import BeautifulSoup
# ---
#from db_expl import DB_sql # importa implementación propia
from scraper_expl import Scraper # clase con metodos comunes de scrapping y se hereda
# ---
from selenium import webdriver  # (controller) Import the `webdriver` class from the `selenium` module
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait  # espera a que carguen los elementos para realizar cualquier operación
from selenium.webdriver.support import expected_conditions as EC  # Import `expected_conditions` from the `selenium.webdriver.support` module
from selenium.webdriver.common.by import By  # Import `By` from the `selenium.webdriver.common` module

# DB1 = db discrepancias o casos
# DB2 = db documentos

wait_time_1 = p.WAIT_TIME_1
wait_time_2 = p.WAIT_TIME_2
wait_time_3 = p.WAIT_TIME_3
wait_time_4 = p.WAIT_TIME_4
wait_time_5 = p.WAIT_TIME_5
wait_time_6 = p.WAIT_TIME_6

# Crear las carpetas si no existen
path_discrepancias = p.PATH_DATA + p.PATHR_DISCRS
path_discr = "C:\\WS_Systep\\Scraper_experts\\data\\discrepancias\\discr_01"
path_docu = "C:\\WS_Systep\\Scraper_experts\\data\\discrepancias\\discr_01\\documento_01"
path_attach = "C:\\WS_Systep\\Scraper_experts\\data\\discrepancias\\discr_01\\documento_01\\Adjuntos"

# buttons paths
xpath_btn_discr = p.XPATH_BTN_DISCR_L + str(1) + p.XPATH_BTN_DISCR_R
xpath_btn_doc = p.XPATH_BTN_DOC_L + str(1) + p.XPATH_BTN_DOC_R

class Scraper_PanelExpertos(Scraper):

    def __init__(self, db) -> None:
        
        super().__init__(db)
        
        self.__create_folder(path_discrepancias)
        self.__create_folder(path_docu)
        self.__create_folder(path_attach)
        self.driver = self.__driver_init()

        # Define las tablas de la base de datos 
        # extrae data de las discrepancias (DB1):
        # id_dcpy | título |  número | fecha y hora ingreso | materia | submateria | fecha audiencia | interesados | estado 
        
        # extrae data de una discrepancia especifica (DB2):
        # id_dcpy | id_document | fecha y hora publicacion | principal.txt | adj1.txt | ... | adjn.txt
        try:
            self.new_table('general', [('id_general', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                                       ('titulo', 'TEXT'),
                                       ('fecha_captura', 'TEXT'),
                                       ('pagina', 'TEXT'),
                                       ('UNIQUE', '(titulo, pagina)')])
            
            self.new_table('panel_expertos', [('id_discrepancia', 'INTEGER PRIMARY KEY AUTOINCREMENT'),    # id discrepancia
                                              ('id_documento', 'INTEGER'),                                 # id documento ppal
                                              ('id_general', 'INTEGER'),                                   # id archivo
                                              ('titulo', 'TEXT'),                                         # link documento 
                                              ('numero_discr', 'TEXT'),
                                              ('materia', 'TEXT'),
                                              ('submateria', 'TEXT'),
                                              ('fecha_presentacion', 'TEXT'),
                                              ('fecha_audiencia', 'TEXT'),
                                              ('interesados', 'TEXT'),
                                              ('estado', 'TEXT'),
                                              ('titulo_doc', 'TEXT'),
                                              ('fecha_publi_doc', 'TEXT'),
                                              ('tipo_doc', 'TEXT'),
                                              ('archivo', 'TEXT'),
                                              ('tipo_archivo', 'TEXT'),
                                              ('ruta_local', 'TEXT'),                                          # titulo discrepancia 
                                              ('url', 'TEXT'), 
                                              ('fecha_captura', 'TEXT'),
                                              ('FOREIGN KEY (id_general)', 'REFERENCES general (id_general)'),
                                              ('UNIQUE', '(titulo_doc, enlace)')])
            
            ''' 
            # esta tabla debería crearse solo cuando se accede a una nueva discrepancia

            self.new_table('discrepancia_01', [('id_discrepancia', 'INTEGER'),
                                               ('id_documento', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                                               ('titulo_doc', 'TEXT'),
                                               ('fecha_publi_doc', 'TEXT'),
                                               ('tipo_doc', 'TEXT'),
                                               ('doc_ppal', 'TEXT'),
                                               ('doc_adjo_1', 'TEXT'),
                                               ('doc_adjo_2', 'TEXT'),
                                               ('doc_adjo_3', 'TEXT'),
                                               ('doc_adjo_4', 'TEXT'),
                                               ('doc_adjo_5', 'TEXT'),
                                               ('FOREIGN KEY (id_discrepancia)', 'REFERENCES general (id_discrepancia)'),
                                               ('UNIQUE', '(id_documento, titulo_doc)')])
            '''
        # Maneja la existencia de tablas preexistentes    
        except:
            print("Se encontró una tabla, se trabajará encima de esta.")

    def __create_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        os.makedirs(path, exist_ok=True)

    def __driver_init(self):
        # Navigation options
        options = webdriver.ChromeOptions()  
        options.add_argument('--start-maximized')  # Argument to maximize the window upon start
        options.add_argument('--disable-extensions')  # Argument to disable browser extensions
        options.add_experimental_option('prefs', {
        "download.default_directory": path_discrepancias, #Change default directory for downloads
        "download.prompt_for_download": False, #To auto download the file
        #"download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
        })

        driver = webdriver.Chrome(options=options) # Configure Chrome browser options
        return driver
    
    def __download(self, xpath_name, start, end, btn_dwld):
        # devuelve cant de palabras en cada archivo del documento y para cada documento (i,j) y el path de la discrepancia 

        # en la carpeta Documentos| se desarga en formato txt la data de las discrepancias en el archivo info_discrepancias.txt

        # en la carpeta Documentos|discrepancia_XX se crea un archivo .txt con la data de una discrepancia especifica
        # en esta carpeta tambien se descarga el .pdf principal y los adjuntos en la carpeta adjuntos
        # click en boton de descarga archivo principal
        # debug cuando el archivo ya fue descargado
        driver = self.driver
        name = driver.find_element(By.XPATH, xpath_name)
        name = name.text
        path_start = os.path.join(start, name)
        path_end = os.path.join(end, name)
        # debug cuando el archivo ya fue descargado
        if not os.path.exists(path_end):
            WebDriverWait(driver, wait_time_2)\
                .until(EC.element_to_be_clickable((By.XPATH, btn_dwld))).click()
            time.sleep(wait_time_3)  # Esperar a que el archivo se descargue completamente
            # debug cuando el archivo no se encuentra en la web
            if not os.path.exists(path_start):
                # Extraer el nombre del archivo sin la extensión .pdf
                match = re.match(r'^(.*)\.pdf$', name)
                if match:
                    name = match.group(1)
                else:
                    print("El nombre del archivo no tiene la extensión .pdf")
                error_message = "ERROR - Archivo no encontrado" 
                path_end = os.path.join(end, name + ".txt")
                if not os.path.exists(path_end):
                    with open(path_end, 'w') as error_file:
                        error_file.write(error_message)
                else:
                    print(f'El archivo - {name + ".txt"} - ya existe en la carpeta de destino')
            else:
                os.rename(path_start, path_end)  # Mover el archivo a la carpeta destino
                print(f'El archivo - {name} - se ha descargado exitosamente')
        else:
            print(f'El archivo - {name} - ya existe en la carpeta de destino')

    def __num_rows_table(self, driver, path, param):
        WebDriverWait(driver, wait_time_3).until(EC.presence_of_element_located((By.XPATH, path)))
        table = driver.find_element(By.XPATH, path)    # Esperar a que la tabla esté presente en la página
        rows = table.find_elements(By.XPATH, param)  # Obtener todas las filas de la tabla
        num_rows = len(rows)    # Contar el número de filas
        return num_rows

    def __extract_discrepancys(self):
        # ejecuta __extract_documents()
    
        driver = self.driver
        driver.maximize_window()  # Maximize the browser window
        time.sleep(p.WAIT_TIME_1)  # Wait for 1 second
        driver.get(p.MAIN_PAGE)  # Open the website 
        # Espera hasta
        WebDriverWait(driver, wait_time_6)\
            .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_NEW_DISCR)))
        
        # extraer data tabla discrepancias
        num_rows_discrs = self.__num_rows_table(driver, p.XPATH_TAB_DISCRS, './/tr')
        for i in range(num_rows_discrs):
            
            xpath_btn_discr = p.XPATH_BTN_DISCR_L + str(i + 1) + p.XPATH_BTN_DISCR_R
            #extraer data de la discrepancia
            discr_table_data = self.__extract_discr_data(xpath_btn_discr)

            # click en la discrepancia
            WebDriverWait(driver, wait_time_2)\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_discr))).click()
            
            # click en boton interesados
            WebDriverWait(driver, wait_time_2)\
                .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_INTER))).click()
            
            disc_inter_data = self.__extract_discr_inter(p.XPATH_TAB_INTER)
            print(disc_inter_data)
            # click en boton expediente
            WebDriverWait(driver, wait_time_2)\
                .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_EXPED))).click()

            self.__extract_documents()

    def __extract_discr_inter_2(self, path):
        driver = self.driver

        # Ruta de la tabla de empresas
        ruta_tabla_empresas = "/html/body/div[1]/div/div/div/div/div[2]/div[4]"
        # Esperar hasta que el elemento esté presente en la página
        wait = WebDriverWait(driver, 10)
        tabla_empresas = wait.until(EC.presence_of_element_located((By.XPATH, ruta_tabla_empresas)))

        # Encontrar la tabla de empresas
        tabla_empresas = driver.find_element(By.XPATH, ruta_tabla_empresas)

        # Obtener todas las filas de la tabla (cada fila corresponde a una empresa)
        filas_empresas = tabla_empresas.find_elements(By.TAG_NAME, "div")

        # Iterar sobre las filas de empresas
        for fila_empresa in filas_empresas:
            # Obtener el nombre de la empresa (asumiendo que está en el primer enlace dentro de cada fila)
            nombre_empresa = fila_empresa.find_element(By.XPATH, "./div[1]/nav/a/div[2]/span").text
            
            # Imprimir el nombre de la empresa
            print("Empresa:", nombre_empresa)
            
            # Obtener los nombres de las personas interesadas (asumiendo que están en los siguientes enlaces dentro de la misma fila)
            nombres_personas = fila_empresa.find_elements(By.XPATH, "./div[1]/nav/div/div[2]/span")
            
            # Iterar sobre los nombres de las personas interesadas
            for nombre_persona in nombres_personas:
                # Imprimir el nombre de la persona interesada
                print("Persona interesada:", nombre_persona.text)
            
    def __extract_discr_inter(self, xpath_comps_inter):
        #for para empresas
        driver = self.driver
        inter_comps_data = list()
        ## BUUUUUUUUG DOWN
        num_cols_comp_inter = self.__num_rows_table(driver, xpath_comps_inter, 'div')
        for i in range(num_cols_comp_inter):
            inter_comp_data = list()
            xpath_comp_inter = p.XPATH_NAME_COMP_INTER_L + str(i + 1) + p.XPATH_NAME_COMP_INTER_R
            xpath_btn_inter = p.XPATH_BTN_COMP_INTER_L + str(i + 1) + p.XPATH_BTN_COMP_INTER_R
            name_comp_inter = driver.find_element(By.XPATH, xpath_comp_inter)
            name_comp_inter = name_comp_inter.text
            inter_comp_data.append(name_comp_inter)
            #for para personas
            num_cols_pers_inter = self.__num_rows_table(driver, xpath_comps_inter, 'div')
            for j in range(num_cols_pers_inter):
                xpath_name_pers_inter_v1 = p.XPATH_NAME_PERS_INTER_V1_L + str(i + 1) + p.XPATH_NAME_PERS_INTER_V1_R
                xpath_name_pers_inter_v2 = p.XPATH_NAME_PERS_INTER_V2_L + str(i + 1) + p.XPATH_NAME_PERS_INTER_V2_M + str(j + 1) + p.XPATH_NAME_PERS_INTER_V2_R

                print(xpath_name_pers_inter_v1)
                print(xpath_name_pers_inter_v2)
                # Intentar encontrar el elemento utilizando el primer XPath
                try:
                    elemento = driver.find_elements(By.XPATH, xpath_name_pers_inter_v1)
                    print("Se encontró el elemento utilizando el XPath 1")
                    # Realizar acciones con el elemento aquí, si es necesario
                    xpath_name_pers_inter = xpath_name_pers_inter_v1
                except NoSuchElementException:
                    # Si no se encuentra el elemento utilizando el primer XPath, intentar con el segundo XPath
                    try:
                        elemento = driver.find_elements(By.XPATH, xpath_name_pers_inter_v2)
                        print("Se encontró el elemento utilizando el XPath 2")
                        # Realizar acciones con el elemento aquí, si es necesario
                        xpath_name_pers_inter = xpath_name_pers_inter_v2
                    except NoSuchElementException:
                        print("No se encontró el elemento utilizando ninguno de los XPaths")


                # click en la discrepancia
                WebDriverWait(driver, wait_time_2)\
                    .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_inter))).click()
                WebDriverWait(driver, wait_time_2).until(EC.presence_of_element_located((By.XPATH, xpath_name_pers_inter)))
                name_pers_inter = driver.find_element(By.XPATH, xpath_name_pers_inter)
                name_pers_inter = name_pers_inter.text
                inter_comp_data.append(name_pers_inter)
            inter_comps_data.append(inter_comp_data)
        return inter_comps_data

    def __extract_discr_data(self, xpath_row):
        driver = self.driver
        num_cols_discr = self.__num_rows_table(driver, xpath_row, './/td')
        row_data = list()
        for i in range(num_cols_discr):
            xpath_elem = xpath_row + '/td[' + str(i + 1) + ']'
            text_inc = driver.find_element(By.XPATH, xpath_elem)
            text_inc = text_inc.text
            row_data.append(text_inc)
        return row_data

 
    def __extract_documents(self):
        # ejecuta __download()

        # extrae data de las discrepancias (DB1):
        # id_dcpy | título | enlace | número | fecha y hora ingreso | materia | submateria | fecha audiencia | interesados | estado 
        
        # extrae data de una discrepancia especifica (DB2):
        # id_dcpy | id_document | fecha y hora publicacion | principal.txt | adj1.txt | ... | adjn.txt
        
        driver = self.driver
        
        # FOR 2
        # click en documento
        WebDriverWait(driver, wait_time_2)\
            .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_doc))).click()  
                                
        # click en principal
        WebDriverWait(driver, wait_time_2)\
            .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_PPAL))).click()

        self.__download(p.XPATH_NAME_PPAL, path_discrepancias, path_docu, p.XPATH_BTN_PPAL_DWLD)
        self.__extract_adjoints()
        
    def __extract_adjoints(self):

        driver = self.driver

        # FOR 3 - CHECK
        # click en adjunto
        WebDriverWait(driver, wait_time_2).\
            until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_ADJO))).click()
        num_rows_adjo = self.__num_rows_table(driver, p.XPATH_TAB_ADJO, './/tr')
        
        for i in range(num_rows_adjo):
            # click en boton de descarga archivo adjunto i
            xpath_btn_adjo_dwld = p.XPATH_BTN_ADJO_DWLD_L + str(i+1) + p.XPATH_BTN_ADJO_DWLD_R
            xpath_name_adjo = p.XPATH_NAME_ADJO_L + str(i+1) + p.XPATH_NAME_ADJO_R
            self.__download(xpath_name_adjo, path_discrepancias, path_attach, xpath_btn_adjo_dwld)
        
        # vuelve a la pag principal
        WebDriverWait(driver, wait_time_2).\
            until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_RETURN))).click()

    # añade al db información sobre la discrepancia (id, titulo, enlace y fecha)
    def update(self):
        # ejecuta __extract discrepancys()
        # usa new_row y update_row

        # sube la data de las discrepancias a la <DB1> como texto plano 
        # sube los documentos a la <DB2> como texto plano 
        driver = self.driver
        self.__extract_discrepancys()
        # Close the browser
        time.sleep(wait_time_3)  # Wait for 60 second
        driver.quit()

        pass

    

    

    # clase db