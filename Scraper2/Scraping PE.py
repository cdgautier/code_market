from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# Configuración de opciones de Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("download.default_directory=RUTA_DE_DESCARGA")


# Inicializar el navegador Chrome
driver = webdriver.Chrome(options=chrome_options)


    # Visitar la primera página
driver.get("https://panelexpertos.cl/discrepancias/tramitadas/")



    # Realizar la secuencia de clics con pausas de 15 segundos entre cada uno
time.sleep(30)
driver.find_element(By.XPATH, '/html/body/main/div[2]/ul/li[1]/a').click()
print("Pasa 1")
time.sleep(30)
driver.find_element(By.XPATH, '/html/body/main/div[3]/div/div/article/div/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/div/div[1]/div[1]/div/div/div[2]').click()
print("Pasa 2")
time.sleep(30)
driver.find_element(By.XPATH, '/html/body/main/div[3]/div/div/article/div/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div[2]').click()
print("Pasa 3")

# Esperar a que se abra una nueva ventana o pestaña (ajusta el tiempo según sea necesario)
time.sleep(30)
xpath_selector = "/html/body/main/div[3]/div/div/article/div/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/div/div[2]/div[2]"
hover_element = driver.find_element(By.XPATH, xpath_selector)

# Crear y disparar un evento 'mouseenter'
driver.execute_script("""
var event = new MouseEvent('mouseenter', {
    'view': window,
    'bubbles': true,
    'cancelable': true
});
arguments[0].dispatchEvent(event);
""", hover_element)




print("Pasa 4")
time.sleep(3)

button_xpath = '/html/body/main/div[3]/div/div/article/div/div[1]/div[2]/div/div/div/div/div/div/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/div[3]/a'
download_button = driver.find_element(By.XPATH, button_xpath)

# Hacer clic en el botón
driver.execute_script("arguments[0].click();", download_button)

time.sleep(10)