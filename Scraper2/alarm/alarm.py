import time
from email.message import EmailMessage
import ssl
import smtplib
from datetime import datetime, timedelta
from db import DB_sql
import time
import schedule
from functools import partial

class Alarm:
    
    def __init__(self, data_base: DB_sql, scrapers: dict, users_configurations: list, table_index: dict, date_index: str = 'fecha_captura') -> None:
        
        """
        databases = {"letters": Letters Database, "reports": Reports Database, ...}
        scrapers = {"letters": scraper of the db letters, "reports": scraper of the db reports, ...}
        Atenttion: the key names of the databases dict must be equal to the key names of scrapers dict.
        user_configurations = [(email, update time, database to monitor (same name as the keys in databases)), ...],
        the 'identifiers' variables correspond to the name of the table you want to work with within the .db files,
        and how the column containing the date in the .db tables is named.
        """
    
        self.data_base = data_base
        self.scrapers = scrapers
        self.users_configurations = users_configurations
        self.schedule = schedule.Scheduler()
        self.date_index = date_index
        self.table_index = table_index
        
    def __send_mail_alert(self, addressee: str, subject: str, message: str) -> None:

        smtp_server = 'smtp.gmail.com'
        smtp_port = 465

        mail_sender = 'alarmas.systep@gmail.com'
        password = 'dgclzrdmfivbshbb'

        mail_message = EmailMessage()
        mail_message['From'] = mail_sender
        mail_message['To'] = addressee
        mail_message['Subject'] = subject

        mail_message.set_content(message)
        
        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(mail_sender, password)
                server.sendmail(mail_sender, addressee, mail_message.as_string())
            print('Correo enviado exitosamente.')
        except Exception as e:
            print(f'Error al enviar el correo: {e}')
            
    def __updates_delivery(self, mail: str, hour_to_update: str, data_bases_to_search: list) -> None:
        
        result =[]
        
        for data_bases in data_bases_to_search:
            
            self.scrapers[data_bases].update()
            
            actual_date = datetime.now()
            date_day_before = actual_date - timedelta(days=1)
            date_format = "%Y-%m-%d"
            formated_actual_date = actual_date.strftime(date_format)
            formated_date_day_before = date_day_before.strftime(date_format)
            date_i = formated_date_day_before + f" {hour_to_update}"
            date_f = formated_actual_date + f" {hour_to_update}"

            result.append(self.data_base.search_data_by_date(self.table_index[data_bases], self.date_index, date_i, date_f))
            
        print(result)
        
        message = f"Estas son las novedades en las bases de datos inscritas desde las {hour_to_update} de ayer {formated_date_day_before} hasta las {hour_to_update} de hoy {formated_actual_date}:\n" 
        
        for i in range(len(data_bases_to_search)):
            
            msg = ""
            
            for data in result[i]:
                
                msg += f'* {data[1]} - {data[2]} - ({data[7]})\n'
                msg += f'{data[3]}\n'
                msg += '\n'
            
            message += f"Para {data_bases_to_search[i]}: \n{msg}\n"
        
        self.__send_mail_alert(mail, 'Actualización de bases de datos', message)
                     
    def alarm_programer(self) -> None:
        
        """
        Method to schedule alarms according to the configurations provided when initializing the class.
        """
        
        for i in range(len(self.users_configurations)):
            
            programed_task = partial(self.__updates_delivery, 
                                       self.users_configurations[i][0], 
                                       self.users_configurations[i][1], 
                                       self.users_configurations[i][2])
            
            self.schedule.every().day.at(self.users_configurations[i][1]).do(programed_task)
            
        print("Alarmas programadas")
            
    def cancel_alarms(self) -> None:
        """
        Method to cancel scheduled alarms.
        """
        self.schedule.clear()
        print("Alarmas desprogramadas")
            
    def run_alarms(self) -> None:
        """
        Method for the system to remain attentive to send alarms at the specified times.
        This method runs indefinitely until externally stopped (CTRL + C).
        """
        print("Comenzó ejecución de las alarmas")
        try:
            while True:
                self.schedule.run_pending()
                time.sleep(1)  # Esperar 1 segundo entre verificaciones de tareas programadas
        except KeyboardInterrupt:
            self.cancel_alarms()
            print("Programa detenido mediante Ctrl + C")
        

