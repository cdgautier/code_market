'''
Pending_work:   
                Reverse update() -> cambio de boton
                if a .txt is found as .pdf, then replace .txt with .pdf -> si no existe path_end pero si txt, elimina txt y mueve pdf 
                funciones db
                webscraping DF

                Comment code
                Compare file versions
                Adjust download times

            # casos particulares:
                discr 65 doc 18
                discr 64 doc 07
'''

# Libraries
import os
import re
import time  # Import the `time` module
import copy
from datetime import datetime # Delivers date and time
from PyPDF2 import PdfReader
from PyPDF2.errors import EmptyFileError
# ---
from scraper.scraper import Scraper # class with common scrapping methods and inherited
# ---
from selenium import webdriver  # (controller) Import the `webdriver` class from the `selenium` module
from selenium.webdriver.common.by import By  # Import `By` from the `selenium.webdriver.common` module
from selenium.webdriver.support.ui import WebDriverWait  # wait for elements to load before performing any operation
from selenium.webdriver.support import expected_conditions as EC  # Import `expected_conditions` from the `selenium.webdriver.support` module
from selenium.common.exceptions import NoSuchElementException

class Scraper_SistemaTramitacion(Scraper):

    parameters = {
        "CANT_WORDS": 20,
        "WAIT_TIME_1": 1,
        "WAIT_TIME_2": 5,
        "WAIT_TIME_3": 10,
        "WAIT_TIME_4": 20,
        "WAIT_TIME_5": 40,
        "WAIT_TIME_6": 60,
        "MAIN_PAGE": 'https://discrepancias.panelexpertos.cl/',
        "XPATH_BTN_NEW_DISCR": '/html/body/div[1]/div/div/div/div/div[2]/div/div[3]/button/span[2]',
        "XPATH_ITEM_LAST_TABLE": '/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/nav/ul/li[8]',
        "XPATH_BTN_LAST_TABLE": '/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/nav/ul/li[8]/button',
        "XPATH_BTN_ACTUAL_TABLE_L": '/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/nav/ul/li[1]/button',   
        "XPATH_BTN_ACTUAL_TABLE_R": '/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/nav/ul/li[9]/button',
        "XPATH_BTN_DISCR": '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/table/tbody/tr[{}]',
        "XPATH_BTN_EXPED": '/html/body/div[1]/div/div/div/div/div[2]/div[2]/div[1]/button',
        "XPATH_BTN_INTER": '/html/body/div[1]/div/div/div/div/div[2]/div[2]/div[2]/button',
        "XPATH_TAB_INTER": '/html/body/div[1]/div/div/div/div/div[2]/div[4]',
        "XPATH_BTN_COMP_INTER": '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div[{}]/nav/a',
        "XPATH_NAME_COMP_INTER": '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div[{}]/nav/a/div[2]/span',
        "XPATH_TAB_PERS_INTER": '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div[1]/nav/div/div/div/a',
        "XPATH_NAME_PERS_INTER_V1": '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div[{}]/nav/div/div/div/a/div/div/span',
        "XPATH_NAME_PERS_INTER_V2": '/html/body/div[1]/div/div/div/div/div[2]/div[4]/div[{}]/nav/div/div/div/a/div[{}]/div/span',
        "XPATH_TAB_DOCS": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]',
        "XPATH_BTN_DOC": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]/a[{}]',
        "XPATH_NAME_DOC": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]/a[{}]/ul/div[1]/span/p[1]',
        "XPATH_DATE_DOC": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]/a[{}]/ul/div[1]/span/p[2]',
        "XPATH_TYPE_DOC": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[3]/a[{}]/ul/div[2]/span',
        "XPATH_BTN_PPAL": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[1]/div/div/div/button[1]',
        "XPATH_BTN_ADJO": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[1]/div/div/div/button[2]',
        "XPATH_BTN_PPAL_DWLD": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/p/div/table/tr/td[5]/button',
        "XPATH_BTN_ADJO_DWLD": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[3]/div/p/div/table/tr[{}]/td[5]/button',
        "XPATH_NAME_PPAL": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[2]/div/p/div/table/tr/td[1]',
        "XPATH_TAB_ADJO": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[3]/div/p/div/table',
        "XPATH_NAME_ADJO": '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[3]/div/p/div/table/tr[{}]/td[1]',
        "XPATH_BTN_RETURN": '/html/body/div[1]/header/div/div[2]/button[1]',
        "XPATH_TAB_DISCRS": '/html/body/div[1]/div/div/div/div/div[2]/div/div[1]/table/tbody'
    }

    def __init__(self, path_files, db) -> None:
        
        super().__init__(path_files, db)
        self.path_files = path_files
        self.actual_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.driver = self.__driver_init()
        self.activate_reverse = False
        self.discr_counter = 0
        # general, title, capture_date, page
        self.data_general = {
            'titulo': None,
            'url': None,
            'fecha_captura': None,
            'plataforma': None  }
        # id_local, id_document, id_general, title, discrepancy_number, subject, subsubject, presentation_date
        # hearing_date, stakeholders, status, doc_title, doc_publication_date, doc_type, file, file_type, local_path, url, capture_date  
        self.data_local = {
            'id_documento': None,
            'titulo': None,
            'titulo_discrepancia': None,
            'numero_discrepancia': None,
            'materia': None,
            'submateria': None, 
            'fecha_presentacion': None,
            'fecha_audiencia': None,
            'interesados': None,
            'estado': None,
            'titulo_documento': None,
            'fecha_publicacion_documento': None,
            'tipo_documento': None,
            'contenido': None,
            'titulo_contenido': None,
            'tipo_contenido': None,
            'cantidad_paginas': None,
            'cantidad_palabras': None,
            'ruta_local': None,
            'url': None,
            'fecha_captura': None }
        
        try:
            self.new_table('general', [('id_general', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                                       ('titulo', 'TEXT'),
                                       ('url', 'TEXT'),
                                       ('fecha_captura', 'TEXT'),
                                       ('pataforma', 'TEXT'),
                                       ('UNIQUE', '(titulo, url)')])
            
            self.new_table('panel_expertos', [('id_local', 'INTEGER PRIMARY KEY AUTOINCREMENT'),    # discrepancy id   - CHECK
                                              ('id_documento', 'INTEGER'),                                 # main document id - CHECK
                                              ('id_general', 'INTEGER'),                                   # file id          - CHECK
                                              ('titulo', 'TEXT'),
                                              ('titulo_discrepancia', 'TEXT'),                                          # - CHECK
                                              ('numero_discrepancia', 'TEXT'),                                    # - CHECK
                                              ('materia', 'TEXT'),                                         # - CHECK 
                                              ('submateria', 'TEXT'),                                      # - CHECK 
                                              ('fecha_presentacion', 'TEXT'),                              # - CHECK
                                              ('fecha_audiencia', 'TEXT'),                                 # - CHECK
                                              ('interesados', 'TEXT'),                                     # - CHECK         
                                              ('estado', 'TEXT'),                                          # - CHECK
                                              ('titulo_documento', 'TEXT'),
                                              ('fecha_publicacion_documento', 'TEXT'),
                                              ('tipo_documento', 'TEXT'),
                                              ('contenido', 'TEXT'),
                                              ('titulo_contenido', 'TEXT'),
                                              ('tipo_contenido', 'TEXT'),
                                              ('cantidad_paginas', 'TEXT'),
                                              ('cantidad_palabras', 'TEXT'),
                                              ('ruta_local', 'TEXT'),                                          # discrepancy title 
                                              ('url', 'TEXT'), 
                                              ('fecha_captura', 'TEXT'),
                                              ('FOREIGN KEY (id_general)', 'REFERENCES general (id_general)'),
                                              ('UNIQUE', '(titulo, url)')])
        # Handles pre-existing table existence
        except:
            print('Taba encontrada, se trabajará sobre ella')
    
    def __driver_init(self):    # Method that initializes and returns the driver 
        prefs = {
            'profile.default_content_settings.popups': 0,
            #'profile.content_settings.pattern_pairs.*.multiple-automatic-downloads': 1,
            'profile.default_content_setting_values.automatic_downloads': 1,
            'download.default_directory': self.path_files,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True
            #'safebrowsing.enabled': False
            }
        # Browser options
        options = webdriver.ChromeOptions()
        #options = webdriver.FirefoxOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_experimental_option("detach", True)
        #options.add_argument('--disable-popup-blocking')
        #options.add_argument('--headless')
        #options.add_argument('--no--sandbox')
        #options.add_argument('--disable-gpu')
        #options.add_argument('--disable-infobars')
        #options.add_argument('--disable-application-cache')
        #options.add_argument('--log-level=0')
        #options.add_argument('--log-level=3')
        #options.add_argument('--dns-prefetch-disable')
        #options.add_argument('--disable-features=NetworkService')
        #options.add_argument('--enable-features=NetworkServiceInProcess')
        #options.add_argument('--disable-domain-reliability')
        #options.add_argument('--enable-logging')
        #options.add_argument('--disable-logging')
        #options.add_argument('--disable-plugins-discovery')
        #options.add_argument('--disable-dev-shm-usage')
        #options.add_argument('--start-maximized')
        #options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('prefs', prefs)

        # Start Chrome browser with configured options
        driver = webdriver.Chrome(options=options)
        #driver = webdriver.Firefox(options=options)

        driver.set_window_position(2000,0)
        return driver

#  -  Data Extraction Functions
    def __extract_discrepancys(self, discr_number):     # Method that does web scraping of discrepancies on the page 

        # get data from the discrepancies table on the page and the list of interested parties in each discrepancy
        # execute the method that extracts the documents from each discrepancy
       
        driver = self.driver    # Call the driver
        data_general = self.data_general
        data_local = self.data_local
        # self.parameters.get(
        path_files = self.path_files
        driver.maximize_window()    # Maximize the window
        time.sleep(self.parameters.get("WAIT_TIME_1"))   # Wait for a time interval
        driver.get(self.parameters.get("MAIN_PAGE"))     # Open the website

        WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
            .until(EC.element_to_be_clickable((By.XPATH, self.parameters.get("XPATH_BTN_NEW_DISCR"))))   # Wait until the last element of the web page appears (a button)
        
        last_table = driver.find_element(By.XPATH, self.parameters.get("XPATH_ITEM_LAST_TABLE"))
        last_table = int(last_table.text)

        xpath_btn_actual_table = "XPATH_BTN_ACTUAL_TABLE_L" if self.activate_reverse else "XPATH_BTN_ACTUAL_TABLE_R"
        if self.activate_reverse:
            # click on last table
            WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                .until(EC.element_to_be_clickable((By.XPATH, self.parameters.get("XPATH_BTN_LAST_TABLE")))).click()

        search_finished = False
        discr_num_in_table, table_iterator = 0, 0
        if (discr_number != 0) and (not search_finished):
            self.discr_counter = discr_number 
            discr_num_in_table, table_iterator = self.__discr_selector(discr_number, xpath_btn_actual_table)
            search_finished = True

        for j in range(table_iterator, last_table):
            
            if (j > table_iterator) and (j < last_table):   
                discr_num_in_table = 0  
                # click on current discrepancy table button
                WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                    .until(EC.element_to_be_clickable((By.XPATH, self.parameters.get(xpath_btn_actual_table)))).click()
                
                WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                    .until(EC.element_to_be_clickable((By.XPATH, self.parameters.get("XPATH_BTN_NEW_DISCR"))))   # Wait until the last element of the web page appears (a button)
         
            num_rows_discrs = self.__num_rows_table(driver, self.parameters.get("XPATH_TAB_DISCRS"), './/tr')    # Get the number of discrepancies  
            for i in range(discr_num_in_table, num_rows_discrs):    # Create iterator for discrepancy folder
                # path of the event/button of the discrepancy
                xpath_btn_discr = self.parameters.get("XPATH_BTN_DISCR").format(str(i+1))
                
                self.discr_counter = self.discr_counter + 1
                if i < 9999:
                    iterator = f'{self.discr_counter:05}'
                else:
                    iterator = str(self.discr_counter)

                discr_table_data = self.__extract_discr_data(xpath_btn_discr)   # Extract discrepancy data
                num_discr = self._change_numdiscr_format(discr_table_data[0])
                name_discr = discr_table_data[1]
                #rest_path = iterator + '_' + name_discr[:self.parameters.get("CANT_WORDS")]
                #rest_path = num_discr + '_' + name_discr[:self.parameters.get("CANT_WORDS")] 
                rest_path = num_discr + '_' + name_discr
                if rest_path[-1] == ' ':
                    rest_path = rest_path + '_'
                path_discr = os.path.join(path_files, rest_path) # Create the path of the discrepancy folder
                os.makedirs(path_discr, exist_ok=True) # Create discrepancy folder

                # title, capture date, page
                #data_general['titulo_discrepancia'] = discr_table_data[1] # crear nuevo titulo
                data_general['fecha_captura'] = self.actual_date
                data_general['plataforma'] = 'Panel de Expertos'
                
                # click on the discrepancy
                WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                    .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_discr))).click() 
                
                # click on interested parties button
                WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                    .until(EC.element_to_be_clickable((By.XPATH, self.parameters.get("XPATH_BTN_INTER")))).click()
                
                disc_inter_data = self.__extract_discr_inter(self.parameters.get("XPATH_TAB_INTER")) # Get list of interested parties in the discrepancy
            
                # id_local, id_document, id_general, title, discrepancy_number, subject, subsubject, presentation_date
                # hearing_date, stakeholders, status, doc_title, doc_publication_date, doc_type, file, file_type, local_path, url, capture_date  
                data_local['titulo_discrepancia'] = discr_table_data[1]
                data_local['numero_discrepancia'] = discr_table_data[0]
                data_local['materia'] = discr_table_data[3]
                data_local['submateria'] = discr_table_data[4]
                data_local['fecha_presentacion'] = discr_table_data[2]
                data_local['fecha_audiencia'] = discr_table_data[6]
                data_local['interesados'] = disc_inter_data
                data_local['estado'] = discr_table_data[5]

                # click on the record button
                WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                    .until(EC.element_to_be_clickable((By.XPATH, self.parameters.get("XPATH_BTN_EXPED")))).click()

                self.__extract_documents(path_discr) # execute method that extracts documents from each discrepancy

    def __extract_discr_data(self, xpath_row):  # Method that extracts data from the discrepancies in the table for each discrepancy 
        driver = self.driver
        num_cols_discr = self.__num_rows_table(driver, xpath_row, './/td')
        row_data = list()
        for i in range(num_cols_discr):
            xpath_elem = xpath_row + '/td[' + str(i + 1) + ']'
            text_inc = driver.find_element(By.XPATH, xpath_elem)
            text_inc = text_inc.text
            row_data.append(text_inc)
        print(f'Discrepancia accedida - {row_data}')
        return row_data
    
    def __extract_discr_inter(self, xpath_comps_inter): # Method that extracts the list of interested parties in the discrepancy 
        #for companies loop
        driver = self.driver
        inter_comps_data = list()
        num_cols_comp_inter = self.__num_rows_table(driver, xpath_comps_inter, 'div')
        for i in range(num_cols_comp_inter):
            inter_comp_data = list()
            xpath_comp_inter = self.parameters.get("XPATH_NAME_COMP_INTER").format(str(i+1))
            xpath_btn_inter = self.parameters.get("XPATH_BTN_COMP_INTER").format(str(i+1))
            name_comp_inter = driver.find_element(By.XPATH, xpath_comp_inter)
            name_comp_inter = name_comp_inter.text
            inter_comp_data.append(name_comp_inter)
            #for people loop
            # click on interested company
            WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_inter))).click()
            xpath_pers_inter = self.parameters.get("XPATH_TAB_PERS_INTER")
            num_cols_pers_inter = self.__num_rows_table(driver, xpath_pers_inter, 'div')
            for j in range(num_cols_pers_inter):
                xpath_name_pers_inter_v1 = self.parameters.get("XPATH_NAME_PERS_INTER_V1").format(str(i+1))
                xpath_name_pers_inter_v2 = self.parameters.get("XPATH_NAME_PERS_INTER_V2").format(str(i+1), str(j+1))
                # Try to find the element using the first XPath
                try:
                    element = driver.find_elements(By.XPATH, xpath_name_pers_inter_v1)
                    # Perform actions with the element here if necessary
                    xpath_name_pers_inter = xpath_name_pers_inter_v1
                except NoSuchElementException:
                    # If the element is not found using the first XPath, try the second XPath
                    try:
                        element = driver.find_elements(By.XPATH, xpath_name_pers_inter_v2)
                        # Perform actions with the element here if necessary
                        xpath_name_pers_inter = xpath_name_pers_inter_v2
                    except NoSuchElementException:
                        print('The element was not found using either XPath')

                name_pers_inter = driver.find_element(By.XPATH, xpath_name_pers_inter)
                name_pers_inter = name_pers_inter.text
                inter_comp_data.append(name_pers_inter)
            inter_comps_data.append(inter_comp_data)
        
        print(f'List of interested parties - {inter_comps_data}')
        return inter_comps_data
    
    def __extract_documents(self, path_discr):  # Method that extracts and downloads data for each document in the discrepancy's record 

        # Execute method that extracts attached files
        # Return document data, its id, its url, main file, main type, main download path
        
        driver = self.driver
        data_general = self.data_general
        data_local = self.data_local
        

        path_files = self.path_files
        num_rows_docs = self.__num_rows_table(driver, self.parameters.get("XPATH_TAB_DOCS"), 'a')    # get the number of documents

        for i in range(num_rows_docs):  # create numeric identifier for the documents
            # create document folder
            if i < 999:
                iterator_docu = f'{i + 1:03}'
            else:
                iterator_docu = str(i)

            # click on document
            xpath_btn_doc = self.parameters.get("XPATH_BTN_DOC").format(str(i+1))
            WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_doc))).click()  
            
            self.__extract_document_data(i) # extract document data
            id_document = str(iterator_docu) # extract document identifier
            url_document = str(driver.current_url) # extract document url

            name_docu = data_local['titulo_documento']
            #rest_path =  iterator_docu + '_' + name_docu[:self.parameters.get("CANT_WORDS")]
            rest_path =  iterator_docu + '_' + name_docu
            if rest_path[-1] == ' ':
                rest_path = rest_path + '_'
            path_docu = os.path.join(path_discr, rest_path) # Create document folder path
            path_attach = os.path.join(path_docu, 'adjuntos')  # Create attachment folder path
            os.makedirs(path_docu, exist_ok=True)

            # BUG - Nombres distintos entre xpath y contenido descargado

            try:
                # click on main
                WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                    .until(EC.element_to_be_clickable((By.XPATH, self.parameters.get("XPATH_BTN_PPAL")))).click()
                
                # download files to destination paths and return file data
                data_principal, num_pages_principal, total_words_principal, title_principal = self.__download(self.parameters.get("XPATH_NAME_PPAL"), path_files, path_docu, self.parameters.get("XPATH_BTN_PPAL_DWLD")) 
                type_principal = 'Principal'
                path_download_principal = path_docu

                # id_documento, contenido, tipo_contenido, ruta_local, url, fecha_captura
                data_local['id_documento'] = id_document
                data_local['contenido'] = data_principal
                data_local['titulo_contenido'] = title_principal
                data_local['tipo_contenido'] = type_principal
                data_local['cantidad_paginas'] = num_pages_principal
                data_local['cantidad_palabras'] = total_words_principal
                data_local['ruta_local'] = path_download_principal
                data_local['url'] = url_document
                data_local['fecha_captura'] = self.actual_date
                
                data_general['titulo'] = data_local['titulo_discrepancia'] + '_' + iterator_docu + '_' + data_local['titulo_documento'] + '_' + data_local['titulo_contenido'] 
                data_local['titulo']   = data_local['titulo_discrepancia'] + '_' + iterator_docu + '_' + data_local['titulo_documento'] + '_' + data_local['titulo_contenido'] 

            except NoSuchElementException:
                print('No hay contenido principal en este documento')

                # id_documento, contenido, tipo_contenido, ruta_local, url, fecha_captura
                data_local['id_documento'] = id_document
                data_local['contenido'] = 'None'
                data_local['titulo_contenido'] = 'None'
                data_local['tipo_contenido'] = 'None'
                data_local['cantidad_paginas'] = 'None'
                data_local['cantidad_palabras'] = 'None'
                data_local['ruta_local'] = 'None'
                data_local['url'] = url_document
                data_local['fecha_captura'] = self.actual_date

                data_general['titulo'] = data_local['titulo_discrepancia'] + '_' + iterator_docu + '_' + data_local['titulo_documento'] + '_' + 'None' 
                data_local['titulo']   = data_local['titulo_discrepancia'] + '_' + iterator_docu + '_' + data_local['titulo_documento'] + '_' + 'None' 

            # make a local copy to print without file
            data_local_copy = copy.deepcopy(data_local)
            # Delete file
            file = 'contenido'
            if file in data_local_copy:
                del data_local_copy[file]
            # Print the resulting dictionary
            print(' - Principal -')
            print(data_local_copy)

            # upload to general and local database
            id_general = None
            #id_general = self.__push_general()
            #self.__push_local(id_general)

            self.__extract_adjoints(path_attach, id_general, iterator_docu)
                        
        # return to main page
        WebDriverWait(driver, self.parameters.get("WAIT_TIME_6")).\
            until(EC.element_to_be_clickable((By.XPATH, self.parameters.get("XPATH_BTN_RETURN")))).click()
 
    def __extract_document_data(self, i):   # Method that extracts name, type and date of the document 
        driver = self.driver
        data_local = self.data_local

        xpath_name_doc = self.parameters.get("XPATH_NAME_DOC").format(str(i+1))
        xpath_date_doc = self.parameters.get("XPATH_DATE_DOC").format(str(i+1))
        xpath_type_doc = self.parameters.get("XPATH_TYPE_DOC").format(str(i+1))

        name_docu = driver.find_element(By.XPATH, xpath_name_doc)
        date_docu = driver.find_element(By.XPATH, xpath_date_doc)
        type_docu = driver.find_element(By.XPATH, xpath_type_doc)

        name_docu = name_docu.text
        date_docu = date_docu.text
        type_docu = type_docu.text

        data_local['titulo_documento'] = name_docu
        data_local['fecha_publicacion_documento'] = date_docu
        data_local['tipo_documento'] = type_docu      
       
    def __extract_adjoints(self, path_attach, id_general, iterator_docu):  # Method that downloads attachments and extracts data from them 

        driver = self.driver
        path_files = self.path_files
        data_local = self.data_local
        data_general = self.data_general

        try:
            element = driver.find_element(By.XPATH, self.parameters.get("XPATH_BTN_ADJO"))
            os.makedirs(path_attach, exist_ok=True) # Create attachment folder
            
            # click on attachment
            WebDriverWait(driver, self.parameters.get("WAIT_TIME_6")).\
                until(EC.element_to_be_clickable((By.XPATH, self.parameters.get("XPATH_BTN_ADJO")))).click()
            
            num_rows_adjo = self.__num_rows_table(driver, self.parameters.get("XPATH_TAB_ADJO"), './/tr') # Number of attached files
            
            for i in range(num_rows_adjo):
                xpath_btn_adjo_dwld = self.parameters.get("XPATH_BTN_ADJO_DWLD").format(str(i+1))
                xpath_name_adjo = self.parameters.get("XPATH_NAME_ADJO").format(str(i+1))
                # download files to destination paths and return file data
                data_adjoint, num_pages_adjoint, total_words_adjoint, title_adjoint = self.__download(xpath_name_adjo, path_files, path_attach, xpath_btn_adjo_dwld)
                type_adjoint = 'Adjunto'
                path_download_adjoint = path_attach

                # file, file type, local path
                data_local['contenido'] = data_adjoint
                data_local['titulo_contenido'] = title_adjoint
                data_local['tipo_contenido'] = type_adjoint
                data_local['cantidad_paginas'] = num_pages_adjoint
                data_local['cantidad_palabras'] = total_words_adjoint
                data_local['ruta_local'] = path_download_adjoint

                data_general['titulo'] = data_local['titulo_discrepancia'] + '_' + iterator_docu + '_' + data_local['titulo_documento'] + '_' + data_local['titulo_contenido'] 
                data_local['titulo']   = data_local['titulo_discrepancia'] + '_' + iterator_docu + '_' + data_local['titulo_documento'] + '_' + data_local['titulo_contenido'] 

                # make a local copy to print without file
                data_local_copy = copy.deepcopy(data_local)
                # Delete file
                file = 'contenido'
                if file in data_local_copy:
                    del data_local_copy[file]
                # Print the resulting dictionary
                print(' - Adjunto -')
                print(data_local_copy)

                # upload to database
                #self.__push_local(id_general)
                
        except NoSuchElementException:
            print('No hay contenidos adjuntos en este documento')
 
 #  -  Additional Functions
    def __num_rows_table(self, driver, xpath, param):   # Method that extracts the number of elements from a list-like structure 
        WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
            .until(EC.presence_of_element_located((By.XPATH, xpath)))   # Wait until the list is loaded
        table = driver.find_element(By.XPATH, xpath)    # Find the list
        rows = table.find_elements(By.XPATH, param)     # Extract its elements based on the html parameter
        num_rows = len(rows)    # Count the number of elements
        return num_rows     # Return number of elements

    def __download(self, xpath_name, start_folder, end_folder, xpath_btn_dwld):     # Method that downloads files, reorganizes files and reads their content 
        # receives xpath of the element name, start folder, end folder, and xpath of the download button
        driver = self.driver
        name_file = driver.find_element(By.XPATH, xpath_name)
        name_file = name_file.text # file name
        path_start = os.path.join(start_folder, name_file) # start path
        path_end = os.path.join(end_folder, name_file)  # end path
        if not os.path.exists(path_end): # debug when the file has already been downloaded
            WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_dwld))).click() # download it
            time.sleep(self.parameters.get("WAIT_TIME_4"))  # Wait for the file to download completely
            self.__correct_file_name(self.path_files)
            # -- debug when the file is not found on the web
            if not os.path.exists(path_start): # if the file has not been downloaded
                error_message = 'ERROR - contenido no econtrado'
                path_end = self.__redo_path(end_folder, name_file)
                if not os.path.exists(path_end): # if this .txt has not been previously downloaded
                    with open(path_end, 'w') as error_file:
                        error_file.write(error_message) # write the file
                        data_text, num_pages, total_words = error_message, 0, 0
                else:
                    print(f'El contenido - {name_file + ".txt"} - ya existe en la carpeta de destino')
                    # extract file to txt
                    data_text, num_pages, total_words = error_message, 0, 0
            else:
                os.rename(path_start, path_end)  # Move the file to the destination folder
                print(f'El contenido  - {name_file} - se ha descargado exitosamente en la carpeta de destino')
                # eliminar .txt si existe en la ruta de destino
                path_end_txt = self.__redo_path(end_folder, name_file)
                if os.path.exists(path_end_txt):
                    os.remove(path_end_txt)
                # extract file to txt
                data_text, num_pages, total_words = self.__extract_text_from_pdf(path_end)
        else:
            print(f'El contenido  - {name_file} - ya existe en la carpeta de destino')
            # extract file to txt
            data_text, num_pages, total_words = self.__extract_text_from_pdf(path_end)
        return data_text, num_pages, total_words, name_file 
    
    def __redo_path(self, folder, name_file):    # Method that changes .pdf to .txt
        match = re.match(r'^(.*)\.pdf$', name_file, re.IGNORECASE) # checks if the file extension is .pdf
        if match:   # extract the extension
            name_file = match.group(1)
        else:   # keep full name if it is not .pdf
            print('El nombre del contenido no tiene la extensión .pdf')
        path_end = os.path.join(folder, name_file + '.txt')

        return path_end

    def __extract_text_from_pdf(self, pdf_path):
        text = ''
        num_pages = 0
        total_words = 0
        
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page_text = pdf_reader.pages[page_num].extract_text()
                    if page_text:  # Ensure there is text on the page
                        text += page_text
                        
                        # Count words on the current page
                        words = re.findall(r'\w+', page_text)
                        total_words += len(words)
                    else:
                        print(f"Warning: No text found on page {page_num+1}")
                        
            return text, num_pages, total_words
        
        except (EmptyFileError, Exception) as e:
            print(f"Error: Cannot read the file '{pdf_path}'. It may be damaged or in an unrecognized format.")
            return "", -1, -1

    def __discr_selector(self, discr_number, xpath_btn_actual_table):    # Method to debug. Select the discrepancy number from which scraping begins 
        driver = self.driver
        # recive discr_number
        # count in actual table
        finded = False
        table_iterator = 0
        num_rows_discrs = self.__num_rows_table(driver, self.parameters.get("XPATH_TAB_DISCRS"), './/tr')    # Get the number of discrepancies 
        accumulator = num_rows_discrs
        while not finded:
            spare = abs(discr_number - accumulator) 
            # si la discrepancia no está en esta tabla
            if accumulator < discr_number:
                # click on current discrepancy table button
                WebDriverWait(driver, self.parameters.get("WAIT_TIME_6"))\
                    .until(EC.element_to_be_clickable((By.XPATH, self.parameters.get(xpath_btn_actual_table)))).click()
                time.sleep(self.parameters.get("WAIT_TIME_2"))
                table_iterator = table_iterator + 1
                num_rows_discrs = self.__num_rows_table(driver, self.parameters.get("XPATH_TAB_DISCRS"), './/tr')    # Get the number of discrepancies 
                accumulator = accumulator + num_rows_discrs 
            else:
                discrepancy =  num_rows_discrs - spare
                finded = True
        return discrepancy, table_iterator

    def __correct_file_name(self, directory):  # Debugging method. Fix downloaded file name that mistakenly comes with '  ' instead of ' '
        # Iterate over the directory
        for filename in os.listdir(directory):
            # Check if the file is a PDF or PDF file
            if filename.lower().endswith('.pdf'):
                # Full path of the file
                filepath = os.path.join(directory, filename)
                # Replaces double spaces with a single space in the file name
                new_filename = re.sub(r'  +', ' ', filename)
                # Remove trailing whitespace if present
                new_filename = new_filename.strip() if new_filename.endswith(' ') else new_filename

                # If the filename has changed, rename the file
                if new_filename != filename:
                    new_filepath = os.path.join(directory, new_filename)
                    os.rename(filepath, new_filepath)
                    print(f"El contenido {filename} ha sido renombrado como {new_filename}")

    def _change_numdiscr_format(self, numdiscr):    # Method that reverses order in discrepancy number to use it as a folder path 
        # Split the string into num and year
        num, year = numdiscr.split()
        # Concatenate in the desired order
        new_format = year + ' ' + num

        return new_format

    def __push_general(self):   # Method that updates the general table of the DB 
        data_general = self.data_general
        id_general = self.new_row('general', 
                            {'id_general': None,
                             'titulo': data_general['titulo'],
                             'url': data_general['url'],
                             'fecha_captura': data_general['fecha_captura'],
                             'plataforma': data_general['plataforma']})
        return id_general

    def __push_local(self, id_general):     # Method that updates the local table of the DB 
        data_local = self.data_local
        id_local = self.new_row('panel_expertos', 
                            {'id_local': None,
                             'id_documento': data_local['id_documento'],
                             'id_general': id_general,
                             'titulo': data_local['titulo'],
                             'titulo_discrepancia': data_local['titulo_discrepancia'],
                             'numero_discrepancia': data_local['numero_discrepancia'],
                             'materia': data_local['materia'],
                             'submateria': data_local['submateria'],
                             'fecha_presentacion': data_local['fecha_presentacion'],
                             'fecha_audiencia': data_local['fecha_audiencia'],
                             'interesados': data_local['interesados'],
                             'estado': data_local['estado'],
                             'titulo_documento': data_local['titulo_documento'],
                             'fecha_publicacion_documento': data_local['fecha_publicacion_documento'],
                             'tipo_documento': data_local['tipo_documento'],
                             'contenido': data_local['contenido'],
                             'titulo_contenido': data_local['titulo_contenido'],
                             'tipo_contenido': data_local['tipo_contenido'],
                             'cantidad_paginas': data_local['cantidad_paginas'],
                             'cantidad_palabras': data_local['cantidad_palabras'],
                             'ruta_local': data_local['ruta_local'],
                             'url': data_local['url'],
                             'fecha_captura': data_local['fecha_captura']})
        
    def update(self, activate_reverse, discr_number):     # Public method that runs scraping and updates the database 
        driver = self.driver # call the driver
        self.activate_reverse = activate_reverse
        self.__extract_discrepancys(discr_number) # execute method that scrapes discrepancies from the page
        time.sleep(self.parameters.get("WAIT_TIME_3"))  # wait for some time and close the browser - optional
        driver.quit() 

