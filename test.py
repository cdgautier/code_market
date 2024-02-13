
    def __download(self, xpath_name, start_folder, end_folder, xpath_btn_dwld):
        # recibe xpath del nombre del elemento, carpeta inicio, carpeta destino, y xpath del boton de descarga
        driver = self.driver
        name_file = driver.find_element(By.XPATH, xpath_name)
        name_file = name_file.text # nombre del archivo
        path_start = os.path.join(start_folder, name_file) # ruta de inicio
        path_end = os.path.join(end_folder, name_file)  # ruta destino
        # debug cuando el archivo ya fue descargado
        if not os.path.exists(path_end):
            WebDriverWait(driver, p.WAIT_TIME_6)\
                .until(EC.element_to_be_clickable((By.XPATH, xpath_btn_dwld))).click()
            time.sleep(p.WAIT_TIME_4)  # Esperar a que el archivo se descargue completamente
            # debug cuando el archivo no se encuentra en la web
            if not os.path.exists(path_start): # si no se ha descargado el archivo
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
                        data_text = error_message
                else:
                    print(f'El archivo - {name_file + '.txt'} - ya existe en la carpeta de destino')
                    # extraer archivo en txt
                    data_text = error_message
            else:
                os.rename(path_start, path_end)  # Mover el archivo a la carpeta destino
                print(f'El archivo - {name_file} - se ha guardado exitosamente en la carpeta de destino')
                # extraer archivo en txt
                data_text = self.__extract_text_from_pdf(path_end)
        else:
            print(f'El archivo - {name_file} - ya existe en la carpeta de destino')
            # extraer archivo en txt
            data_text = self.__extract_text_from_pdf(path_end)
        return data_text