from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------------------------------------------------------

# Obtencion de los URLS 

# Funcion que obtiene los links de los periodos usando selenium para seleccionar
# las fechas
def url_letters_calendar(fecha_inicio, fecha_fin): 
    driver = webdriver.Chrome()
    driver.get("https://cartas.coordinador.cl/")

    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/section[2]/div[1]/form/div/div/div[2]/a"))
    )

    element.click()

    input_fecha = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input-periodo"))
    )

    input_fecha.clear()
    input_fecha.send_keys(fecha_inicio + " - " + fecha_fin)

    boton_buscar = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/section[2]/div[1]/form/div/div/span/button[1]")
    boton_buscar.click()

    WebDriverWait(driver, 10).until(
        lambda driver: driver.current_url != "https://cartas.coordinador.cl/"
    )

    url_despues_busqueda = driver.current_url

    driver.quit()

    return url_despues_busqueda

# -----------------------------------------------------------------------------

# Obtencion de los URLS 
def url_letter_str(fecha_inicio, fecha_fin):
    pass