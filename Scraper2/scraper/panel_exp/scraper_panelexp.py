'''
Pending_work:   Reverse update(), 
                Compare file versions, webscraping DF.
                If a .txt is found as .pdf, then replace .txt with .pdf
                Adjust download times
                Comment code
'''

# Libraries
import os
import re
import sys
import time  # Import the `time` module
from pathlib import Path
from PyPDF2 import PdfReader
from datetime import datetime # Delivers date and time
# ---
from scraper.panel_exp import parameters_panelexp as p
from scraper.scraper import Scraper # class with common scrapping methods and inherited
# ---
from selenium import webdriver  # (controller) Import the `webdriver` class from the `selenium` module
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait  # wait for elements to load before performing any operation
from selenium.webdriver.support import expected_conditions as EC  # Import `expected_conditions` from the `selenium.webdriver.support` module
from selenium.webdriver.common.by import By  # Import `By` from the `selenium.webdriver.common` module

sys.path.append(str(Path(__file__).resolve().parent.parent))

class Scraper_PanelExpertos(Scraper):

    def __init__(self, path_files, db) -> None:
        
        super().__init__(path_files, db)
        self.path_discrepancys = p.PATH_DISCRS
        self.actual_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.driver = self.__driver_init()
        self.disc_counter = 0
        # general, title, capture_date, page
        self.data_general = {
            'titulo_discrepancia': None,
            'fecha_captura': None,
            'pagina': None  }
        # id_local, id_document, id_general, title, discrepancy_number, subject, subsubject, presentation_date
        # hearing_date, stakeholders, status, doc_title, doc_publication_date, doc_type, file, file_type, local_path, url, capture_date  
        self.data_local = {
            'id_documento': None,
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
            'archivo': None,
            'tipo_archivo': None,
            'cant_pag_archivo': None,
            'cant_palabras_archivo': None,
            'ruta_local': None,
            'url': None,
            'fecha_captura': None }
        
        try:
            self.new_table('general', [('id_general', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                                       ('titulo', 'TEXT'),
                                       ('fecha_captura', 'TEXT'),
                                       ('pagina', 'TEXT'),
                                       ('UNIQUE', '(titulo, pagina)')])
            
            self.new_table('panel_expertos', [('id_local', 'INTEGER PRIMARY KEY AUTOINCREMENT'),    # discrepancy id   - CHECK
                                              ('id_documento', 'INTEGER'),                                 # main document id - CHECK
                                              ('id_general', 'INTEGER'),                                   # file id          - CHECK
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
                                              ('archivo', 'TEXT'),
                                              ('tipo_archivo', 'TEXT'),
                                              ('cant_pag_archivo', 'TEXT'),
                                              ('cant_palabras_archivo', 'TEXT'),
                                              ('ruta_local', 'TEXT'),                                          # discrepancy title 
                                              ('url', 'TEXT'), 
                                              ('fecha_captura', 'TEXT'),
                                              ('FOREIGN KEY (id_general)', 'REFERENCES general (id_general)'),
                                              ('UNIQUE', '(titulo_documento, url)')])
        # Handles pre-existing table existence
        except:
            print('Taba encontrada, se trabajará sobre ella')

    def __push_general(self):
        data_general = self.data_general
        id_general = self.new_row('general', 
                            {'id_general': None,
                             'titulo': data_general['titulo'],
                             'fecha_captura': data_general['fecha_captura'],
                             'pagina': data_general['pagina']})
        return id_general

    def __push_local(self, id_general):
        data_local = self.data_local
        id_local = self.new_row('panel_expertos', 
                            {'id_local': None,
                             'id_documento': data_local['id_documento'],
                             'id_general': id_general,
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
                             'archivo': data_local['archivo'],
                             'tipo_archivo': data_local['tipo_archivo'],
                             'cant_pag_archivo': data_local['cant_pag_archivo'],
                             'cant_palabras_archivo': data_local['cant_palabras_archivo'],
                             'ruta_local': data_local['ruta_local'],
                             'url': data_local['url'],
                             'fecha_captura': data_local['fecha_captura']})
        
        if id_local != None:
            self.update_row('panel_expertos', 'id_local', id_local, 
                            {'estado': data_local['estado'],
                            'titulo_documento': data_local['titulo_documento'],
                            'fecha_publicacion_documento': data_local['fecha_publicacion_documento'],
                            'tipo_documento': data_local['tipo_documento'],
                            'archivo': data_local['archivo'],
                            'tipo_archivo': data_local['tipo_archivo'],
                            'cant_pag_archivo': data_local['cant_pag_archivo'],
                            'cant_palabras_archivo': data_local['cant_palabras_archivo'],
                            'ruta_local': data_local['ruta_local'],
                            'url': data_local['url']})

    def __driver_init(self):
        # Get the absolute path of the download folder
        download_folder = os.path.abspath(self.path_discrepancys) 
        # Check if the download folder exists
        if not os.path.exists(download_folder): 
            os.makedirs(download_folder)
        prefs = {
            'download.default_directory': download_folder,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
            'safebrowsing.enabled': False}
        # Browser options
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_experimental_option('prefs', prefs)
        # Start Chrome browser with configured options
        driver = webdriver.Chrome(options=options)
        return driver

    def __download(self, xpath_name, start_folder, end_folder, xpath_btn_dwld):
        # receives xpath of the element name, start folder, end folder, and xpath of the download button
        driver = self.driver
        name_file = driver.find_element(By.XPATH, xpath_name)
        name_file = name_file.text # file name
        path_start = os.path.join(start_folder, name_file) # start path
        path_end = os.path.join(end_folder, name_file)  # end path
        if not os.path.exists(path_end): # debug when the file has already been downloaded
            WebDriverWait(driver, p.WAIT_TIME_6)\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_dwld))).click() # download it
            time.sleep(p.WAIT_TIME_4)  # Wait for the file to download completely
            # -- debug when the file is not found on the web
            if not os.path.exists(path_start): # if the file has not been downloaded
                print(2)
                error_message = 'ERROR - Archivo no econtrado'
                match = re.match(r'^(.*)\.pdf$', name_file) # checks if the file extension is .pdf
                if match:   # extract the extension
                    name_file = match.group(1)
                else:   # keep full name if it is not .pdf
                    print('El nombre del archivo no tiene la extensión .pdf')
                path_end = os.path.join(end_folder, name_file + '.txt')
                if not os.path.exists(path_end): # if this .txt has not been previously downloaded
                    with open(path_end, 'w') as error_file:
                        error_file.write(error_message) # write the file
                        data_text, num_pages, total_words = error_message, 0, 0
                else:
                    print(f'El archivo - {name_file + ".txt"} - ya existe en la carpeta de destino')
                    # extract file to txt
                    data_text, num_pages, total_words = error_message, 0, 0
            else:
                os.rename(path_start, path_end)  # Move the file to the destination folder
                print(f'El archivo  - {name_file} - se ha descargado exitosamente en la carpeta de destino')
                # extract file to txt
                data_text, num_pages, total_words = self.__extract_text_from_pdf(path_end)
        else:
            print(f'El archivo  - {name_file} - ya existe en la carpeta de destino')
            # extract file to txt
            data_text, num_pages, total_words = self.__extract_text_from_pdf(path_end)
        return data_text, num_pages, total_words 

    # Method that extracts the number of elements from a list-like structure
        # receives driver, xpath of the list, and html parameter of the list
    def __num_rows_table(self, driver, xpath, param):
        WebDriverWait(driver, p.WAIT_TIME_6)\
            .until(EC.presence_of_element_located((By.XPATH, xpath)))   # Wait until the list is loaded
        table = driver.find_element(By.XPATH, xpath)    # Find the list
        rows = table.find_elements(By.XPATH, param)     # Extract its elements based on the html parameter
        num_rows = len(rows)    # Count the number of elements
        return num_rows     # Return number of elements

    def __extract_discrepancys(self):   # Method that does web scraping of discrepancies on the page

        # get data from the discrepancies table on the page and the list of interested parties in each discrepancy
        # execute the method that extracts the documents from each discrepancy
       
        driver = self.driver    # Call the driver
        data_general = self.data_general
        data_local = self.data_local

        path_discrepancys = self.path_discrepancys
        driver.maximize_window()    # Maximize the window
        time.sleep(p.WAIT_TIME_1)   # Wait for a time interval
        driver.get(p.MAIN_PAGE)     # Open the website

        WebDriverWait(driver, p.WAIT_TIME_6)\
            .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_NEW_DISCR)))   # Wait until the last element of the web page appears (a button)
        
        last_table = driver.find_element(By.XPATH, p.XPATH_BTN_LAST_TABLE)
        last_table = int(last_table.text)

        for j in range(last_table):

            if (j > 0) and (j < last_table):    
                # click on current discrepancy table button
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_ACTUAL_TABLE))).click()
                
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_NEW_DISCR)))   # Wait until the last element of the web page appears (a button)
         
            num_rows_discrs = self.__num_rows_table(driver, p.XPATH_TAB_DISCRS, './/tr')    # Get the number of discrepancies  
            for i in range(num_rows_discrs):    # Create iterator for discrepancy folder
                # path of the event/button of the discrepancy
                xpath_btn_discr = p.XPATH_BTN_DISCR.format(str(i+1))
                self.disc_counter = self.disc_counter + 1
                if i < 9999:
                    iterator = f'{self.disc_counter:05}'
                else:
                    iterator = str(self.disc_counter)

                discr_table_data = self.__extract_discr_data(xpath_btn_discr)   # Extract discrepancy data
                name_discr = discr_table_data[1]
                rest_path = iterator + '_' + name_discr[:p.CANT_WORDS] 
                if rest_path[-1] == ' ':
                    rest_path = rest_path + '_'
                print(path_discrepancys)
                print(rest_path)
                path_discr = os.path.join(path_discrepancys, rest_path) # Create the path of the discrepancy folder
                os.makedirs(path_discr, exist_ok=True) # Create discrepancy folder

                # title, capture date, page
                data_general['titulo_discrepancia'] = discr_table_data[1]
                data_general['fecha_captura'] = self.actual_date
                data_general['pagina'] = 'Panel de Expertos'
                
                # click on the discrepancy
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_discr))).click() 
                
                # click on interested parties button
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_INTER))).click()
                
                disc_inter_data = self.__extract_discr_inter(p.XPATH_TAB_INTER) # Get list of interested parties in the discrepancy
            
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
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_EXPED))).click()

                self.__extract_documents(path_discr) # execute method that extracts documents from each discrepancy

    def __extract_discr_data(self, xpath_row):
        driver = self.driver
        num_cols_discr = self.__num_rows_table(driver, xpath_row, './/td')
        row_data = list()
        for i in range(num_cols_discr):
            xpath_elem = xpath_row + '/td[' + str(i + 1) + ']'
            text_inc = driver.find_element(By.XPATH, xpath_elem)
            text_inc = text_inc.text
            row_data.append(text_inc)
        print(f'Discrepancy accessed - {row_data}')
        return row_data

    def __extract_discr_inter(self, xpath_comps_inter):
        #for companies loop
        driver = self.driver
        inter_comps_data = list()
        num_cols_comp_inter = self.__num_rows_table(driver, xpath_comps_inter, 'div')
        for i in range(num_cols_comp_inter):
            inter_comp_data = list()
            xpath_comp_inter = p.XPATH_NAME_COMP_INTER.format(str(i+1))
            xpath_btn_inter = p.XPATH_BTN_COMP_INTER.format(str(i+1))
            name_comp_inter = driver.find_element(By.XPATH, xpath_comp_inter)
            name_comp_inter = name_comp_inter.text
            inter_comp_data.append(name_comp_inter)
            #for people loop
            # click on interested company
            WebDriverWait(driver, p.WAIT_TIME_6)\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_inter))).click()
            xpath_pers_inter = p.XPATH_TAB_PERS_INTER
            num_cols_pers_inter = self.__num_rows_table(driver, xpath_pers_inter, 'div')
            for j in range(num_cols_pers_inter):
                xpath_name_pers_inter_v1 = p.XPATH_NAME_PERS_INTER_V1.format(str(i+1))
                xpath_name_pers_inter_v2 = p.XPATH_NAME_PERS_INTER_V2.format(str(i+1), str(j+1))
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

    def __extract_document_data(self, i):
        driver = self.driver
        data_local = self.data_local

        xpath_name_doc = p.XPATH_NAME_DOC.format(str(i+1))
        xpath_date_doc = p.XPATH_DATE_DOC.format(str(i+1))
        xpath_type_doc = p.XPATH_TYPE_DOC.format(str(i+1))

        name_docu = driver.find_element(By.XPATH, xpath_name_doc)
        date_docu = driver.find_element(By.XPATH, xpath_date_doc)
        type_docu = driver.find_element(By.XPATH, xpath_type_doc)

        name_docu = name_docu.text
        date_docu = date_docu.text
        type_docu = type_docu.text

        data_local['titulo_documento'] = name_docu
        data_local['fecha_publicacion_documento'] = date_docu
        data_local['tipo_documento'] = type_docu
        
    # Method that extracts and downloads data for each document in the discrepancy's record
    def __extract_documents(self, path_discr):

        # Execute method that extracts attached files
        # Return document data, its id, its url, main file, main type, main download path
        
        driver = self.driver
        data_local = self.data_local
        

        path_discrepancys = self.path_discrepancys
        num_rows_docs = self.__num_rows_table(driver, p.XPATH_TAB_DOCS, 'a')    # get the number of documents

        for i in range(num_rows_docs):  # create numeric identifier for the documents
            # create document folder
            if i < 999:
                iterator = f'{i + 1:03}'
            else:
                iterator = str(i)

            # click on document
            xpath_btn_doc = p.XPATH_BTN_DOC.format(str(i+1))
            WebDriverWait(driver, p.WAIT_TIME_6)\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_doc))).click()  
            
            self.__extract_document_data(i) # extract document data
            id_document = str(iterator) # extract document identifier
            url_document = str(driver.current_url) # extract document url

            name_docu = data_local['titulo_documento']
            rest_path =  iterator + '_' + name_docu[:p.CANT_WORDS]
            if rest_path[-1] == ' ':
                rest_path = rest_path + '_'
            path_docu = os.path.join(path_discr, rest_path) # Create document folder path
            path_attach = os.path.join(path_docu, p.PATHR_ATTACH)  # Create attachment folder path
            os.makedirs(path_docu, exist_ok=True)

            test_text = driver.find_element(By.XPATH, p.XPATH_BTN_PPAL)
            test_text = test_text.text
            print(f'button text: {test_text}')

            try:
                # click on main
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_PPAL))).click()
                
                # download files to destination paths and return file data
                data_principal, num_pages_principal, total_words_principal = self.__download(p.XPATH_NAME_PPAL, path_discrepancys, path_docu, p.XPATH_BTN_PPAL_DWLD) 
                type_principal = 'Principal'
                path_download_principal = path_docu

                # id_documento, archivo, tipo_archivo, ruta_local, url, fecha_captura
                data_local['id_documento'] = id_document
                data_local['archivo'] = data_principal
                data_local['tipo_archivo'] = type_principal
                data_local['cant_pag_archivo'] = num_pages_principal
                data_local['cant_palabras_archivo'] = total_words_principal
                data_local['ruta_local'] = path_download_principal
                data_local['url'] = url_document
                data_local['fecha_captura'] = self.actual_date

            except NoSuchElementException:
                print('There is no main file in this document')

                # id_documento, archivo, tipo_archivo, ruta_local, url, fecha_captura
                data_local['id_documento'] = id_document
                data_local['archivo'] = 'None'
                data_local['tipo_archivo'] = 'None'
                data_local['cant_pag_archivo'] = 'None'
                data_local['cant_palabras_archivo'] = 'None'
                data_local['ruta_local'] = 'None'
                data_local['url'] = url_document
                data_local['fecha_captura'] = self.actual_date

            # make a local copy to print without file
            data_local_copy = data_local.copy()
            # Delete file
            file = 'file'
            if file in data_local_copy:
                del data_local_copy[file]
            # Print the resulting dictionary
            print(' - Main -')
            print(data_local_copy)

            # upload to general and local database
            id_general = None
            #id_general = self.__push_general()
            #self.__push_local(id_general)

            self.__extract_adjoints(path_attach, id_general)
                    
            
        # return to main page
        WebDriverWait(driver, p.WAIT_TIME_6).\
            until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_RETURN))).click()
        
    
    def __extract_adjoints(self, path_attach, id_general):

        driver = self.driver
        path_discrepancys = self.path_discrepancys
        data_local = self.data_local

        try:
            element = driver.find_element(By.XPATH, p.XPATH_BTN_ADJO)
            os.makedirs(path_attach, exist_ok=True) # Create attachment folder
            
            # click on attachment
            WebDriverWait(driver, p.WAIT_TIME_6).\
                until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_ADJO))).click()
            
            num_rows_adjo = self.__num_rows_table(driver, p.XPATH_TAB_ADJO, './/tr') # Number of attached files
            
            for i in range(num_rows_adjo):
                xpath_btn_adjo_dwld = p.XPATH_BTN_ADJO_DWLD.format(str(i+1))
                xpath_name_adjo = p.XPATH_NAME_ADJO.format(str(i+1))
                # download files to destination paths and return file data
                data_adjoint, num_pages_adjoint, total_words_adjoint = self.__download(xpath_name_adjo, path_discrepancys, path_attach, xpath_btn_adjo_dwld)
                type_adjoint = 'Adjunto'
                path_download_adjoint = path_attach

                # file, file type, local path
                data_local['archivo'] = data_adjoint
                data_local['tipo_archivo'] = type_adjoint
                data_local['cant_pag_archivo'] = num_pages_adjoint
                data_local['cant_palabras_archivo'] = total_words_adjoint
                data_local['ruta_local'] = path_download_adjoint

                # make a local copy to print without file
                data_local_copy = data_local.copy()
                # Delete file
                file = 'file'
                if file in data_local_copy:
                    del data_local_copy[file]
                # Print the resulting dictionary
                print(' - Adjunto -')
                print(data_local_copy)

                # upload to database
                #self.__push_local(id_general)
                
        except NoSuchElementException:
            print('There are no attached files in this document')

    def __extract_text_from_pdf(self, pdf_path):
        text = ''
        num_pages = 0
        total_words = 0
        
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                page_text = pdf_reader.pages[page_num].extract_text()
                text += page_text
                
                # Count words on the current page
                words = re.findall(r'\w+', page_text)
                total_words += len(words)
                
        return text, num_pages, total_words

        
    # method to update the database
    def update(self):
        driver = self.driver # call the driver
        self.__extract_discrepancys() # execute method that scrapes discrepancies from the page
        time.sleep(p.WAIT_TIME_3)  # wait for some time and close the browser - optional
        driver.quit() 

