# Script: partes_auto_cli.py
# Author: Jules @ Google
# Date: 2024-09-16
# Description: Automates login to https://hospedajes.ses.mir.es/hospedajes-sede/#/comunicacion/inicio
#              using Google Chrome on a Windows environment.
#
# --- PRE-REQUISITOS (Windows) ---
# 1. Google Chrome:
#    - Este script requiere que tengas Google Chrome instalado en tu sistema Windows.
#    - Puedes descargarlo desde: https://www.google.com/chrome/
#
# 2. chromedriver.exe:
#    - Necesitas descargar el 'chromedriver.exe' compatible con TU versión de Google Chrome.
#    - Verifica la versión de tu Google Chrome (Menú de Chrome -> Ayuda -> Información de Google Chrome).
#    - Descarga 'chromedriver.exe' desde: https://googlechromelabs.github.io/chrome-for-testing/
#      (Busca el directorio que coincida con tu versión de Chrome, luego ve a win32 o win64 y descarga chromedriver.zip)
#    - IMPORTANTE: Extrae 'chromedriver.exe' del archivo .zip y colócalo en el MISMO DIRECTORIO que este script (`partes_auto_cli.py`).
#      Alternativamente, puedes añadir la carpeta que contiene 'chromedriver.exe' a la variable de entorno PATH de tu sistema.
#
# --- Ejecución (Windows) ---
# 1. Abre una terminal (Command Prompt o PowerShell).
# 2. Navega al directorio donde guardaste este script y 'chromedriver.exe'.
# 3. Ejecuta el script con: python partes_auto_cli.py
# ----------------------------------------------------

import getpass
import time
import os
import sys
from shutil import which # To find chromedriver.exe in PATH

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

def get_credentials():
    """Prompts the user for username and password.

    Returns:
        tuple: A tuple containing the username (str) and password (str).
               Returns (None, None) if the user aborts input (e.g., Ctrl+C).
    """
    try:
        username = input("Ingrese su nombre de usuario: ")
        password = getpass.getpass("Ingrese su contraseña: ")
        return username, password
    except (KeyboardInterrupt, EOFError):
        print("\nOperación cancelada por el usuario.")
        return None, None

def login_to_website(username, password):
    """
    Automates the login process for the specified website using Google Chrome on Windows.
    """
    driver = None
    print("\nIniciando el navegador Google Chrome...")
    page_load_failed = False 

    try:
        # --- ChromeDriver and Chrome Configuration for Windows ---
        # Intenta encontrar el directorio del script.
        try:
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        except Exception:
            script_dir = os.getcwd() # Fallback si sys.argv[0] no es usable
            print(f"Advertencia: No se pudo determinar el directorio del script vía sys.argv[0], usando CWD: {script_dir}")

        # Busca chromedriver.exe en el directorio del script primero, luego en el PATH.
        chromedriver_filename = "chromedriver.exe"
        chromedriver_path_local = os.path.join(script_dir, chromedriver_filename)
        chromedriver_path = None

        if os.path.exists(chromedriver_path_local):
            chromedriver_path = chromedriver_path_local
            print(f"Usando {chromedriver_filename} local: {chromedriver_path}")
        else:
            print(f"{chromedriver_filename} no encontrado en: {chromedriver_path_local}. Buscando en PATH...")
            chromedriver_in_path = which(chromedriver_filename)
            if chromedriver_in_path:
                chromedriver_path = chromedriver_in_path
                print(f"{chromedriver_filename} encontrado en PATH: {chromedriver_path}")
            else:
                print(f"Error: {chromedriver_filename} no encontrado en el directorio del script ni en PATH.")
                print("Por favor, descargue la versión compatible de chromedriver.exe desde https://googlechromelabs.github.io/chrome-for-testing/")
                print(f"y colóquela en el mismo directorio que este script ({script_dir}) o en una ubicación en su PATH.")
                return False
        
        # La comprobación de permisos de ejecución os.access con os.X_OK no es relevante para .exe en Windows.
        # Si el archivo existe, Windows intentará ejecutarlo.

        chrome_options = ChromeOptions()
        # No se establece chrome_options.binary_location aquí; Selenium intentará encontrar Chrome
        # en su ubicación de instalación predeterminada en Windows.
        # Si Chrome está en una ubicación no estándar, el usuario podría necesitar agregar:
        # chrome_options.binary_location = "C:\\Ruta\\No\\Estandar\\Google\\Chrome\\Application\\chrome.exe"
        
        # Argumentos generales de Chrome. Revisar si todos son necesarios o beneficiosos en Windows.
        # --no-sandbox puede no ser necesario o incluso problemático en algunos entornos Windows.
        # chrome_options.add_argument('--no-sandbox') 
        chrome_options.add_argument('--disable-dev-shm-usage') # Útil en entornos con recursos limitados.
        chrome_options.add_argument('--remote-debugging-port=9222') # Para depuración.
        chrome_options.add_argument('--start-maximized') # Iniciar Chrome maximizado.
        # chrome_options.add_argument('--headless') # Descomentar para modo sin GUI.

        service = ChromeService(executable_path=chromedriver_path)
        
        print(f"Usando {chromedriver_filename} en: {chromedriver_path}")
        print(f"Intentando iniciar Google Chrome...")
        # --- Fin de Configuración ---

        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"Navegando a la URL: https://hospedajes.ses.mir.es/hospedajes-sede/#/comunicacion/inicio")
        driver.set_page_load_timeout(30) 
        
        try:
            driver.get("https://hospedajes.ses.mir.es/hospedajes-sede/#/comunicacion/inicio")
        except TimeoutException: 
            page_load_failed = True
            raise 

        print("Navegación exitosa a la página de inicio.")
        wait = WebDriverWait(driver, 20) 

        print("Localizando campo de nombre de usuario...")
        user_field_id = "mat-input-130"
        user_field = wait.until(EC.presence_of_element_located((By.ID, user_field_id)))
        print("Campo de nombre de usuario encontrado. Ingresando datos...")
        user_field.send_keys(username)

        print("Localizando campo de contraseña...")
        pass_field_id = "mat-input-131"
        pass_field = wait.until(EC.presence_of_element_located((By.ID, pass_field_id)))
        print("Campo de contraseña encontrado. Ingresando datos...")
        pass_field.send_keys(password)

        print("Localizando botón de inicio de sesión...")
        login_button_xpath = "/html/body/div[1]/app-root/app-root/div/div[3]/app-pagina/div[2]/mat-card/app-login/div/div[1]/div/form/div/button"
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, login_button_xpath)))
        print("Botón de inicio de sesión encontrado. Haciendo clic...")
        login_button.click()
        
        print("Clic en el botón de inicio de sesión realizado.")
        time.sleep(5) 
        
        print("Proceso de inicio de sesión completado.")
        return True

    except TimeoutException:
        if page_load_failed:
             print("Error: No se pudo acceder a la URL especificada (timeout de carga de página).")
        else:
            print("Error: No se pudieron encontrar los elementos necesarios en la página para el inicio de sesión (timeout esperando elemento).")
        return False
    except NoSuchElementException:
        print("Error: No se pudieron encontrar los elementos necesarios en la página para el inicio de sesión (elemento no encontrado).")
        return False
    except WebDriverException as e:
        print(f"Error de WebDriver: {e}")
        if "net::ERR_NAME_NOT_RESOLVED" in str(e) or "net::ERR_CONNECTION_REFUSED" in str(e):
            print("Adicional: Error de red o DNS al intentar acceder a la URL.")
        elif "This version of ChromeDriver only supports Chrome version" in str(e):
            print("Adicional: La versión de chromedriver.exe no es compatible con su versión de Google Chrome.")
            print("Descargue la versión correcta de: https://googlechromelabs.github.io/chrome-for-testing/")
        elif "cannot find chrome binary" in str(e).lower() or "failed to start browser" in str(e).lower():
             print("Adicional: Selenium no pudo encontrar o iniciar la instalación de Google Chrome.")
             print("Asegúrese de que Chrome esté instalado en su ubicación predeterminada.")
             print("Si está en una ubicación no estándar, considere configurar 'options.binary_location' en el script.")
        else:
            print("Adicional: Problema general del WebDriver, al iniciar Chrome, o al acceder a la URL.")
        return False
    except Exception as e: 
        print(f"Ocurrió un error inesperado: {type(e).__name__} - {e}")
        return False
    finally:
        if driver:
            print("Cerrando el navegador.")
            driver.quit()


if __name__ == '__main__':
    user, pwd = get_credentials()
    if user and pwd:
        print("Intentando iniciar sesión...")
        success = login_to_website(user, pwd)
        if success:
            print("Intento de inicio de sesión finalizado.")
        else:
            print("El proceso de inicio de sesión falló.")
    else:
        print("No se ingresaron credenciales.")
