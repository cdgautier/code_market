#  recorer en reverso, comentarios en ingles, comparar versiones de archivos, webscraping DF.

# actualizacion pendiente: si un .txt se encuentra como pdf, entonces reemplazar .txt por pdf

# ajustar tiempos de descarga
# comentar código

# Libraries

import os
import re
import time  # Import the `time` module
from datetime import datetime # Entrega fecha y hora
#import pandas as pd  # Import the `pandas` library as `pd`
import parameters as p
from PyPDF2 import PdfReader
# ---
from scraper import Scraper # clase con metodos comunes de scrapping y se hereda
# ---
from selenium import webdriver  # (controller) Import the `webdriver` class from the `selenium` module
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait  # espera a que carguen los elementos para realizar cualquier operación
from selenium.webdriver.support import expected_conditions as EC  # Import `expected_conditions` from the `selenium.webdriver.support` module
from selenium.webdriver.common.by import By  # Import `By` from the `selenium.webdriver.common` module

class Scraper_PanelExpertos(Scraper):

    def __init__(self, db) -> None:
        
        super().__init__(db)
        self.path_discrepancys = p.PATH_DISCRS
        self.actual_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.driver = self.__driver_init()
        self.disc_counter = 0
        # id_general, titulo, fecha_captura, pagina
        self.data_general = {
            'titulo_discrepancia': None,
            'fecha_captura': None,
            'pagina': None  }

        # id_local, id_documento, id_general, titulo, numero_discr, materia, submateria, fecha_presentacion
        # fecha_audiencia, interesados, estado, titulo_doc, fecha_publi_doc, tipo_doc, archivo, tipo_archivo, ruta_local, url, fecha_captura  
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
            
            self.new_table('panel_expertos', [('id_local', 'INTEGER PRIMARY KEY AUTOINCREMENT'),    # id discrepancia   - CHECK
                                              ('id_documento', 'INTEGER'),                                 # id documento ppal - CHECK
                                              ('id_general', 'INTEGER'),                                   # id archivo        - CHECK
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
                                              ('ruta_local', 'TEXT'),                                          # titulo discrepancia 
                                              ('url', 'TEXT'), 
                                              ('fecha_captura', 'TEXT'),
                                              ('FOREIGN KEY (id_general)', 'REFERENCES general (id_general)'),
                                              ('UNIQUE', '(titulo_documento, url)')])
    
        # Maneja la existencia de tablas preexistentes    
        except:
            print('Se encontró una tabla, se trabajará encima de esta.')
    
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
        
        # Obtener la ruta absoluta de la carpeta de descarga
        download_folder = os.path.abspath(self.path_discrepancys)
        # Verificar si la carpeta de descarga existe
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        
        prefs = {
            'download.default_directory': download_folder,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
            'safebrowsing.enabled': False
        }
        
        # Opciones del navegador
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_experimental_option('prefs', prefs)

        # Iniciar el navegador Chrome con las opciones configuradas
        driver = webdriver.Chrome(options=options)
        return driver
    
    def __download(self, xpath_name, start_folder, end_folder, xpath_btn_dwld):
        # recibe xpath del nombre del elemento, carpeta inicio, carpeta destino, y xpath del boton de descarga
        driver = self.driver
        name_file = driver.find_element(By.XPATH, xpath_name)
        name_file = name_file.text # nombre del archivo
        print(name_file)
        path_start = os.path.join(start_folder, name_file) # ruta de inicio
        path_end = os.path.join(end_folder, name_file)  # ruta destino
        print(path_start)
        print(path_end)
        # debug cuando el archivo ya fue descargado
        if not os.path.exists(path_end): # si el archivo no ha sido descargado
            print(1)
            WebDriverWait(driver, p.WAIT_TIME_6)\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_dwld))).click() # lo descargamos
            time.sleep(p.WAIT_TIME_4)  # Esperar a que el archivo se descargue completamente
            # -- debug cuando el archivo no se encuentra en la web
            if not os.path.exists(path_start): # si no se ha descargado el archivo
                print(2)
                error_message = 'ERROR - Archivo no encontrado'
                match = re.match(r'^(.*)\.pdf$', name_file) # verifica si la extensión del archivo es .pdf
                if match:   # extrae la extensión
                    name_file = match.group(1)
                else:   # mantiene nombre completo si no es .pdf
                    print('El nombre del archivo no tiene la extensión .pdf')
                path_end = os.path.join(end_folder, name_file + '.txt')
                if not os.path.exists(path_end): # si no se ha descargado previamente este .txt
                    with open(path_end, 'w') as error_file:
                        error_file.write(error_message) # escribe el archivo
                        data_text, num_pages, total_words = error_message, 0, 0
                else:
                    print(f'El archivo - {name_file + ".txt"} - ya existe en la carpeta de destino')
                    # extraer archivo en txt
                    data_text, num_pages, total_words = error_message, 0, 0
            else:
                os.rename(path_start, path_end)  # Mover el archivo a la carpeta destino
                print(f'El archivo - {name_file} - se ha guardado exitosamente en la carpeta de destino')
                # extraer archivo en txt
                data_text, num_pages, total_words = self.__extract_text_from_pdf(path_end)
        else:
            print(f'El archivo - {name_file} - ya existe en la carpeta de destino')
            # extraer archivo en txt
            data_text, num_pages, total_words = self.__extract_text_from_pdf(path_end)
        return data_text, num_pages, total_words 

    # Método que extrae la cantidad de elementos de una estructura tipo lista
        # recibe driver, xpath de la lista y parámetro html de la lista
    def __num_rows_table(self, driver, xpath, param):
        WebDriverWait(driver, p.WAIT_TIME_6)\
            .until(EC.presence_of_element_located((By.XPATH, xpath)))   # Espera a que la lista se haya cargado
        table = driver.find_element(By.XPATH, xpath)    # Encontrar la lista
        rows = table.find_elements(By.XPATH, param)     # Extraer sus elementos en función del parámetro html
        num_rows = len(rows)    # Contar el número de elementos
        return num_rows     # Retornar número de elementos

    def __extract_discrepancys(self):   # Método que hace webscraping de las discrepancias en la página
        
        # obtiene los datos de la tabla de discrepancias en la página y la lista de interesados en cada discrepancia
        # ejecuta el método que extrae los documentos de cada discrepancia
       
        driver = self.driver    # Llama al driver
        data_general = self.data_general
        data_local = self.data_local

        path_discrepancys = self.path_discrepancys
        driver.maximize_window()    # Maximiza la ventana
        time.sleep(p.WAIT_TIME_1)   # Espera un intervalo de tiempo
        driver.get(p.MAIN_PAGE)     # Abre el sitio web

        WebDriverWait(driver, p.WAIT_TIME_6)\
            .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_NEW_DISCR)))   # Espera hasta que aparezca el último elemento de la página web (un botón)
        
        last_table = driver.find_element(By.XPATH, p.XPATH_BTN_LAST_TABLE)
        last_table = int(last_table.text)

        for j in range(last_table):

            if (j > 0) and (j < last_table):    
                # click en boton de tabla de discrepancia actual
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_ACTUAL_TABLE))).click()
                
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_NEW_DISCR)))   # Espera hasta que aparezca el último elemento de la página web (un botón)
         
            num_rows_discrs = self.__num_rows_table(driver, p.XPATH_TAB_DISCRS, './/tr')    # Obtener la cant de discrepancias  
            for i in range(num_rows_discrs):    # Crear iterador para carpeta de discrepancia
                
                #xpath_btn_discr = p.XPATH_BTN_DISCR_L + str(i + 1) + p.XPATH_BTN_DISCR_R    # path del evento/botón de la discrepancia
                xpath_btn_discr = p.XPATH_BTN_DISCR
                xpath_btn_discr.format(i=i+1)
                self.disc_counter = self.disc_counter + 1
                if i < 9999:
                    iterator = f'{self.disc_counter:05}'
                else:
                    iterator = str(self.disc_counter)

                discr_table_data = self.__extract_discr_data(xpath_btn_discr)   # Extraer data de la discrepancia
                name_discr = discr_table_data[1]
                rest_path = iterator + '_' + name_discr[:p.CANT_WORDS] 
                if rest_path[-1] == ' ':
                    rest_path = rest_path + '_'
                print(path_discrepancys)
                print(rest_path)
                path_discr = os.path.join(path_discrepancys, rest_path) # Crear el path de la carpeta de la discrepancia
                os.makedirs(path_discr, exist_ok=True) # Crea carpeta de la discrepancia

                # titulo, fecha_captura, pagina
                data_general['titulo_discrepancia'] = discr_table_data[1]
                data_general['fecha_captura'] = self.actual_date
                data_general['pagina'] = 'Panel de Expertos'
                
                # click en la discrepancia
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_discr))).click() 
                
                # click en boton interesados
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_INTER))).click()
                
                disc_inter_data = self.__extract_discr_inter(p.XPATH_TAB_INTER) # Obtener lista de interesados en la discrepancia
            

                # id_local, id_documento, id_general, titulo, numero_discr, materia, submateria, fecha_presentacion
                # fecha_audiencia, interesados, estado, titulo_doc, fecha_publi_doc, tipo_doc, archivo, tipo_archivo, ruta_local, url, fecha_captura
                
                data_local['titulo_discrepancia'] = discr_table_data[1]
                data_local['numero_discrepancia'] = discr_table_data[0]
                data_local['materia'] = discr_table_data[3]
                data_local['submateria'] = discr_table_data[4]
                data_local['fecha_presentacion'] = discr_table_data[2]
                data_local['fecha_audiencia'] = discr_table_data[6]
                data_local['interesados'] = disc_inter_data
                data_local['estado'] = discr_table_data[5]
                
                # click en boton expediente
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_EXPED))).click()

                self.__extract_documents(path_discr) # ejecuta método que extrae los documentos de cada discrepancia

    def __extract_discr_data(self, xpath_row):
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

    def __extract_discr_inter(self, xpath_comps_inter):
        #for para empresas
        driver = self.driver
        inter_comps_data = list()
        num_cols_comp_inter = self.__num_rows_table(driver, xpath_comps_inter, 'div')
        for i in range(num_cols_comp_inter):
            inter_comp_data = list()
            #xpath_comp_inter = p.XPATH_NAME_COMP_INTER_L + str(i + 1) + p.XPATH_NAME_COMP_INTER_R
            xpath_comp_inter = p.XPATH_NAME_COMP_INTER
            xpath_comp_inter.format(i=i+1)
            #xpath_btn_inter = p.XPATH_BTN_COMP_INTER_L + str(i + 1) + p.XPATH_BTN_COMP_INTER_R
            xpath_btn_inter = p.XPATH_BTN_COMP_INTER
            xpath_btn_inter.format(i=i+1)
            name_comp_inter = driver.find_element(By.XPATH, xpath_comp_inter)
            name_comp_inter = name_comp_inter.text
            inter_comp_data.append(name_comp_inter)
            #for para personas
            # click en la empresa intresada
            WebDriverWait(driver, p.WAIT_TIME_6)\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_inter))).click()
            xpath_pers_inter = p.XPATH_TAB_PERS_INTER
            num_cols_pers_inter = self.__num_rows_table(driver, xpath_pers_inter, 'div')
            for j in range(num_cols_pers_inter):
                #xpath_name_pers_inter_v1 = p.XPATH_NAME_PERS_INTER_V1_L + str(i + 1) + p.XPATH_NAME_PERS_INTER_V1_R
                xpath_name_pers_inter_v1 = p.XPATH_NAME_PERS_INTER_V1
                xpath_name_pers_inter_v1.format(i=i+1)
                #xpath_name_pers_inter_v2 = p.XPATH_NAME_PERS_INTER_V2_L + str(i + 1) + p.XPATH_NAME_PERS_INTER_V2_M + str(j + 1) + p.XPATH_NAME_PERS_INTER_V2_R
                xpath_name_pers_inter_v2 = p.XPATH_NAME_PERS_INTER_V2
                xpath_name_pers_inter_v2.format(i=i+1, j=i+1)
                # Intentar encontrar el elemento utilizando el primer XPath
                try:
                    elemento = driver.find_elements(By.XPATH, xpath_name_pers_inter_v1)
                    # Realizar acciones con el elemento aquí, si es necesario
                    xpath_name_pers_inter = xpath_name_pers_inter_v1
                except NoSuchElementException:
                    # Si no se encuentra el elemento utilizando el primer XPath, intentar con el segundo XPath
                    try:
                        elemento = driver.find_elements(By.XPATH, xpath_name_pers_inter_v2)
                        # Realizar acciones con el elemento aquí, si es necesario
                        xpath_name_pers_inter = xpath_name_pers_inter_v2
                    except NoSuchElementException:
                        print('No se encontró el elemento utilizando ninguno de los XPaths')

                name_pers_inter = driver.find_element(By.XPATH, xpath_name_pers_inter)
                name_pers_inter = name_pers_inter.text
                inter_comp_data.append(name_pers_inter)
            inter_comps_data.append(inter_comp_data)
        
        print(f'Lista de interesados - {inter_comps_data}')
        return inter_comps_data

    def __extract_document_data(self, i):
        driver = self.driver
        data_local = self.data_local

        #xpath_name_doc = p.XPATH_NAME_DOC_L + str(i+1) + p.XPATH_NAME_DOC_R
        xpath_name_doc = p.XPATH_NAME_DOC
        xpath_name_doc.format(i=i+1)
        #xpath_date_doc = p.XPATH_DATE_DOC_L + str(i+1) + p.XPATH_DATE_DOC_R
        xpath_date_doc = p.XPATH_DATE_DOC
        xpath_date_doc.format(i=i+1)
        #xpath_type_doc = p.XPATH_TYPE_DOC_L + str(i+1) + p.XPATH_TYPE_DOC_R
        xpath_type_doc = p.XPATH_TYPE_DOC
        xpath_type_doc.format(i=i+1)

        name_docu = driver.find_element(By.XPATH, xpath_name_doc)
        date_docu = driver.find_element(By.XPATH, xpath_date_doc)
        type_docu = driver.find_element(By.XPATH, xpath_type_doc)
        name_docu = name_docu.text
        date_docu = date_docu.text
        type_docu = type_docu.text

        data_local['titulo_documento'] = name_docu
        data_local['fecha_publicacion_documento'] = date_docu
        data_local['tipo_documento'] = type_docu
        
    # Método que extrae y descarga la data de cada documento en el expediente de la discrepancia
    def __extract_documents(self, path_discr):

        # Ejecuta el método que extrae archivos adjuntos
        # Retorna la data del documento, su id, su url, el archivo principal, el tipo principal, la ruta de descarga principal
        
        driver = self.driver
        data_local = self.data_local
        

        path_discrepancys = self.path_discrepancys
        num_rows_docs = self.__num_rows_table(driver, p.XPATH_TAB_DOCS, 'a')    # obtiene la cantidad de documentos

        for i in range(num_rows_docs):  # crea identificador númerico para los documentos
            #crear carpeta de documento
            if i < 999:
                iterator = f'{i + 1:03}'
            else:
                iterator = str(i)

            # click en documento
            #xpath_btn_doc = p.XPATH_BTN_DOC_L + str(i + 1) + p.XPATH_BTN_DOC_R
            xpath_btn_doc = p.XPATH_BTN_DOC
            xpath_btn_doc.format(i=i+1)
            WebDriverWait(driver, p.WAIT_TIME_6)\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_doc))).click()  
            
            self.__extract_document_data(i) # extraer data del documento
            id_document = str(iterator) # extraer identificador del documento
            url_document = str(driver.current_url) # extraer url del documento

            name_docu = data_local['titulo_documento']
            rest_path =  iterator + '_' + name_docu[:p.CANT_WORDS]
            if rest_path[-1] == ' ':
                rest_path = rest_path + '_'
            path_docu = os.path.join(path_discr, rest_path) # Crear el path de la carpeta del documento
            path_attach = os.path.join(path_docu, p.PATHR_ATTACH)  # Crear el path de la carpeta de adjuntos
            os.makedirs(path_docu, exist_ok=True)

            test_text = driver.find_element(By.XPATH, p.XPATH_BTN_PPAL)
            test_text = test_text.text
            print(f'button text: {test_text}')

            try:
                # click en principal
                WebDriverWait(driver, p.WAIT_TIME_6)\
                    .until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_PPAL))).click()
                
                # descarga los archivos en las rutas de destino y devuelve la data de el archivo
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
                print('No hay archivo principal en este documento')

                # id_documento, archivo, tipo_archivo, ruta_local, url, fecha_captura
                data_local['id_documento'] = id_document
                data_local['archivo'] = 'None'
                data_local['tipo_archivo'] = 'None'
                data_local['cant_pag_archivo'] = 'None'
                data_local['cant_palabras_archivo'] = 'None'
                data_local['ruta_local'] = 'None'
                data_local['url'] = url_document
                data_local['fecha_captura'] = self.actual_date

            # copiar local para imprimir sin archivo
            data_local_copy = data_local.copy()
            # Eliminar archivo
            archivo = 'archivo'
            if archivo in data_local_copy:
                del data_local_copy[archivo]
            # Imprimir el diccionario resultante
            print(' - Principal -')
            print(data_local_copy)

            # subir a la base de datos general y local
            id_general = None
            #id_general = self.__push_general()
            #self.__push_local(id_general)

            self.__extract_adjoints(path_attach, id_general)
                    
            
        # vuelve a la pag principal
        WebDriverWait(driver, p.WAIT_TIME_6).\
            until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_RETURN))).click()
        
    
    def __extract_adjoints(self, path_attach, id_general):

        driver = self.driver
        path_discrepancys = self.path_discrepancys
        data_local = self.data_local

        try:
            elemento = driver.find_element(By.XPATH, p.XPATH_BTN_ADJO)
            os.makedirs(path_attach, exist_ok=True) # Crear carpeta de adjuntos
            
            # click en adjunto
            WebDriverWait(driver, p.WAIT_TIME_6).\
                until(EC.element_to_be_clickable((By.XPATH, p.XPATH_BTN_ADJO))).click()
            
            num_rows_adjo = self.__num_rows_table(driver, p.XPATH_TAB_ADJO, './/tr') # Cantidad de archivos adjuntos
            
            for i in range(num_rows_adjo):
                
                #xpath_btn_adjo_dwld = p.XPATH_BTN_ADJO_DWLD_L + str(i+1) + p.XPATH_BTN_ADJO_DWLD_R
                xpath_btn_adjo_dwld = p.XPATH_BTN_ADJO_DWLD
                xpath_btn_adjo_dwld.format(i=i+1)
                #xpath_name_adjo = p.XPATH_NAME_ADJO_L + str(i+1) + p.XPATH_NAME_ADJO_R
                xpath_name_adjo = p.XPATH_NAME_ADJO
                xpath_name_adjo.format(i=i+1)
                # descarga los archivos en las rutas de destino y devuelve la data de el archivo
                data_adjoint, num_pages_adjoint, total_words_adjoint = self.__download(xpath_name_adjo, path_discrepancys, path_attach, xpath_btn_adjo_dwld)
                type_adjoint = 'Adjunto'
                path_download_adjoint = path_attach

                # archivo, tipo_archivo, ruta_local
                data_local['archivo'] = data_adjoint
                data_local['tipo_archivo'] = type_adjoint
                data_local['cant_pag_archivo'] = num_pages_adjoint
                data_local['cant_palabras_archivo'] = total_words_adjoint
                data_local['ruta_local'] = path_download_adjoint

                # copiar local para imprimir sin archivo
                data_local_copy = data_local.copy()
                # Eliminar archivo
                archivo = 'archivo'
                if archivo in data_local_copy:
                    del data_local_copy[archivo]
                # Imprimir el diccionario resultante
                print(' - Adjunto -')
                print(data_local_copy)

                # subir a la base de datos
                #self.__push_local(id_general)
                
        except NoSuchElementException:
            print('No hay archivos adjuntos en este documento')

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
                
                # Contar las palabras en la página actual
                words = re.findall(r'\w+', page_text)
                total_words += len(words)
                
        return text, num_pages, total_words

        
    # método que actualiza la base de datos
    def update(self):
        driver = self.driver # llama al driver
        self.__extract_discrepancys() # ejecuta método que hace webscraping de las discrepancias en la página
        time.sleep(p.WAIT_TIME_3)  # esperar un tiempo y cerrar el browser - prescindible
        driver.quit() 
