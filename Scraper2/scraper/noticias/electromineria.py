import requests
from datetime import datetime
from bs4 import BeautifulSoup
import random
import os
from pathlib import Path
from db import DB_sql

# -----------------------------------------------------------------------------

from scraper import Scraper

#------------------------------------------------------------------------------

class Scraper_Electromineria(Scraper):
    
    def __init__(self, path_files, db: str) -> None:
        
        super().__init__(path_files, db)
        
        self.main_page = "https://electromineria.cl/category/panorama-energetico/"
        self.next_page = self.main_page
        
        try:
            
            self.new_table('general', [('id_general', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                                        ('titulo', 'TEXT'),
                                        ('fecha_captura', 'TEXT'),
                                        ('pagina', 'TEXT'),
                                        ('UNIQUE', '(titulo, pagina)')])
            
            
        
            self.new_table('electromineria', [('id_local', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                                              ('id_general', 'INTEGER'),
                                              ('titulo', 'TEXT'),
                                              ('enlace', 'TEXT'),
                                              ('cantidad_palabras', 'INTEGER'),
                                              ('ruta_descarga', 'TEXT'),
                                              ('fecha_pagina', 'TEXT'),
                                              ('fecha_captura', 'TEXT'),
                                              ('FOREIGN KEY (id_general)', 'REFERENCES general (id_general)'),
                                              ('UNIQUE', '(titulo, enlace)')])
            
        except:
            
            print("Se encontró una tabla, se trabajará encima de esta.")
            
    def __extract_html(self, link):
        
        user_agents =[
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        ]
 
        target_website = link
 
        # Add user agents at random
        request_headers = {
            'user-agent': random.choice(user_agents)
        }
 
        # Initiate HTTP request
        response = requests.get(target_website, headers=request_headers)
        soup = BeautifulSoup(response.content, 'lxml', multi_valued_attributes=None)
        
        return soup
             
    def __extract_articles(self, link: str) -> list:
 
        soup = self.__extract_html(link)
        
        section = soup.find('div', class_="et_pb_ajax_pagination_container")
        articles = section.find_all('article')
        
        info = [x.find('h2') for x in articles]
        dates = [x.find('span', class_="published") for x in articles]
        
        info = [x.find('a') for x in info]
        dates = [x.text for x in dates]
        
        info = [[x.text ,x.get('href')] for x in info]
        result = [info[i] + [dates[i]] for i in range(len(info))]
        
        return result
    
    def __extract_news(self, link):
        
        soup = self.__extract_html(link)
        
        text = soup.find('div', class_="et_pb_column et_pb_column_1_2 et_pb_column_1_tb_body  et_pb_css_mix_blend_mode_passthrough")
        
        title = text.find('h1', class_="entry-title").text
        sub_title = text.find_all('div', class_="et_pb_text_inner")[0].text
        body = text.find_all('div', class_="et_pb_text_inner")[2].text.strip('\n').replace('\n', ' ')
        
        return [title, sub_title, body]
    
    def update(self):
        
        articles = self.__extract_articles(self.main_page)
        
        for x in articles: # Hacer la inserción alrevez
            
            actual_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            id_general = self.new_row('general', {'id_general': None,
                                                  'titulo': x[0],
                                                  'fecha_captura': actual_date,
                                                  'pagina': 'electromineria'})
            
            id_local = self.new_row('electromineria', {'id_local': None,
                                            'id_general': id_general,
                                            'titulo': x[0],
                                            'enlace': x[1],
                                            'fecha_pagina': x[2],
                                            'fecha_captura': actual_date})
            
            if id_local != None:
                n_of_words, complete_path = self.__download(x[1], id_local)
                self.update_row('electromineria', 'id_local', id_local, {'cantidad_palabras': n_of_words, 'ruta_descarga': complete_path})
            
        print("Database updated.")
        
    def __download(self, link, id):
        
        complete_path = os.path.join(self.path_files, Path(f'{id}.txt'))
           
        with open(complete_path, 'w', encoding='utf-8') as archive:
            try:
                text = self.__extract_news(link)
                text = f"""
                {text[0]}
                        
                {text[1]}
                        
                {text[2]}"""
                        
                archive.write(text)
                
                n_of_words = len(text.split())
                
                return n_of_words, complete_path
                
            except:
                text = "NOT FOUND"
                archive.write(text)
                
                return None, None
        
#-------------------------------------------------------------------