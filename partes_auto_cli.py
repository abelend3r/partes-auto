# Script: partes_auto_cli.py
# Author: Jules @ Google
# Date: 2024-09-16
# Description: Automates login to https://hospedajes.ses.mir.es/hospedajes-sede/#/comunicacion/inicio
#              using Google Chrome (Flatpak) and Selenium.
#
# --- PRE-REQUISITOS ---
# 1. Google Chrome (Flatpak):
#    - Este script requiere que tengas Google Chrome instalado como una aplicación Flatpak.
#    - El ID de la aplicación Flatpak de Chrome debe ser 'com.google.Chrome'.
#    - Puedes instalarlo en Fedora con: flatpak install flathub com.google.Chrome
#
# 2. chromedriver:
#    - Necesitas descargar el 'chromedriver' compatible con TU versión de Google Chrome (Flatpak).
#    - Verifica la versión de tu Chrome Flatpak (ej. `flatpak info com.google.Chrome` o desde el menú de Chrome).
#    - Descarga chromedriver desde: https://googlechromelabs.github.io/chrome-for-testing/
#    - IMPORTANTE: Coloca el archivo ejecutable 'chromedriver' en el MISMO DIRECTORIO que este script (`partes_auto_cli.py`).
#                  Alternativamente, asegúrate de que esté en tu PATH y sea localizable.
#
# --- Ejecución ---
# python partes_auto_cli.py
# ----------------------

import getpass
import time
import os
import sys
from shutil import which # To find chromedriver in PATH

# from selenium.webdriver.firefox.service import Service as FirefoxService # Removed
from selenium.webdriver.chrome.service import Service as ChromeService  # Added
from selenium.webdriver.chrome.options import Options as ChromeOptions  # Added
from selenium import webdriver  # Keep webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)


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
    Automates the login process for the specified website using Google Chrome (Flatpak).
    """
    driver = None
    print("\nIniciando el navegador Google Chrome (Flatpak)...")
    page_load_failed = False

    try:
        # --- Configuración de ChromeDriver y Chrome (Flatpak) ---
        # Se asume que 'chromedriver' está en el mismo directorio que este script o en el PATH.
        # sys.argv[0] se usa para obtener la ruta del script actual como primera opción.
        try:
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        except Exception:
            script_dir = os.getcwd() # Fallback si sys.argv[0] no es usable
            print(f"Advertencia: No se pudo determinar el directorio del script vía sys.argv[0], usando CWD: {script_dir}")

        chromedriver_path_local = os.path.join(script_dir, "chromedriver")
        chromedriver_path = None

        if os.path.exists(chromedriver_path_local):
            chromedriver_path = chromedriver_path_local
            print(f"Usando chromedriver local: {chromedriver_path}")
        else:
            print(f"chromedriver no encontrado en: {chromedriver_path_local}. Buscando en PATH...")
            chromedriver_in_path = which("chromedriver")
            if chromedriver_in_path:
                chromedriver_path = chromedriver_in_path
                print(f"chromedriver encontrado en PATH: {chromedriver_path}")
            else:
                print("Error: chromedriver no encontrado en el directorio del script ni en PATH.")
                print("Por favor, descargue la versión compatible de chromedriver desde https://googlechromelabs.github.io/chrome-for-testing/")
                print("y colóquela en el mismo directorio que este script o en una ubicación en su PATH.")
                return False

        if not os.access(chromedriver_path, os.X_OK):
            print(f"Error: chromedriver en {chromedriver_path} no tiene permisos de ejecución.")
            print("Por favor, otórguele permisos de ejecución (ej. `chmod +x chromedriver_path`).")
            return False

        chrome_options = ChromeOptions()
        # Ruta al ejecutable de flatpak. '/usr/bin/flatpak' es estándar en muchas distros.
        # Se verifica también /bin/flatpak como alternativa.
        flatpak_exe_path = "/usr/bin/flatpak"
        if not os.path.exists(flatpak_exe_path):
            flatpak_exe_path = "/bin/flatpak"
            if not os.path.exists(flatpak_exe_path):
                print("Error: El ejecutable de Flatpak no se encontró en /usr/bin/flatpak ni en /bin/flatpak.")
                print("Asegúrese de que Flatpak esté instalado y accesible.")
                return False

        chrome_options.binary_location = flatpak_exe_path
        # Argumentos para que flatpak ejecute la aplicación Chrome deseada.
        chrome_options.add_argument("run")
        chrome_options.add_argument("com.google.Chrome")

        # Argumentos comunes para mejorar la estabilidad/compatibilidad con Selenium:
        chrome_options.add_argument("--no-sandbox") # A menudo necesario en entornos restringidos o CI.
        chrome_options.add_argument("--disable-dev-shm-usage") # Evita problemas de recursos de memoria compartida.
        chrome_options.add_argument("--remote-debugging-port=9222") # Útil para depuración.
        # chrome_options.add_argument('--headless') # Descomentar para ejecutar en modo headless (sin GUI)

        service = ChromeService(executable_path=chromedriver_path)

        print(f"Usando chromedriver en: {chromedriver_path}")
        print(f"Intentando iniciar Chrome Flatpak con el comando: {flatpak_exe_path} run com.google.Chrome")
        # --- Fin de Configuración ---

        driver = webdriver.Chrome(service=service, options=chrome_options)

        print(f"Navegando a la URL: https://hospedajes.ses.mir.es/hospedajes-sede/#/comunicacion/inicio")
        driver.set_page_load_timeout(30)

        try:
            driver.get(
                "https://hospedajes.ses.mir.es/hospedajes-sede/#/comunicacion/inicio"
            )
        except TimeoutException:
            page_load_failed = True
            raise

        print("Navegación exitosa a la página de inicio.")
        wait = WebDriverWait(driver, 20)

        print("Localizando campo de nombre de usuario...")
        user_field_id = "mat-input-130" # ID observado, puede ser dinámico
        user_field = wait.until(EC.presence_of_element_located((By.ID, user_field_id)))
        print("Campo de nombre de usuario encontrado. Ingresando datos...")
        user_field.send_keys(username)

        print("Localizando campo de contraseña...")
        pass_field_id = "mat-input-131" # ID observado, puede ser dinámico
        pass_field = wait.until(EC.presence_of_element_located((By.ID, pass_field_id)))
        print("Campo de contraseña encontrado. Ingresando datos...")
        pass_field.send_keys(password)

        print("Localizando botón de inicio de sesión...")
        login_button_xpath = "/html/body/div[1]/app-root/app-root/div/div[3]/app-pagina/div[2]/mat-card/app-login/div/div[1]/div/form/div/button"
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        print("Botón de inicio de sesión encontrado. Haciendo clic...")
        login_button.click()

        print("Clic en el botón de inicio de sesión realizado.")
        time.sleep(5) # Pausa para observar el resultado antes de cerrar.

        print("Proceso de inicio de sesión completado.")
        return True

    except TimeoutException:
        if page_load_failed:
             print("Error: No se pudo acceder a la URL especificada (timeout de carga de página).")
        else:
            print("Error: No se pudieron encontrar los elementos necesarios en la página para el inicio de sesión (timeout esperando elemento).")
        return False
    except NoSuchElementException: # Aunque WebDriverWait debería prevenir esto, se mantiene por robustez.
        print("Error: No se pudieron encontrar los elementos necesarios en la página para el inicio de sesión (elemento no encontrado).")
        return False
    except WebDriverException as e:
        print(f"Error de WebDriver: {e}")
        # Intentar dar mensajes más específicos basados en el error de WebDriver
        if "net::ERR_NAME_NOT_RESOLVED" in str(e) or "net::ERR_CONNECTION_REFUSED" in str(e):
            print("Adicional: Error de red o DNS al intentar acceder a la URL.")
        elif (
            "Failed to current OS stats" in str(e)
            or "DevToolsActivePort file doesn't exist" in str(e)
            or "cannot connect to browser" in str(e)
            or "response code 1" in str(e) # Código de error común de Flatpak
        ):
            print("Adicional: Problema al iniciar o conectar con Google Chrome (Flatpak).")
            print("Verifique lo siguiente:")
            print("  1. Que Google Chrome Flatpak ('com.google.Chrome') esté correctamente instalado y funcional.")
            print(f"  2. Que 'chromedriver' (en '{chromedriver_path}') sea compatible con su versión de Chrome y tenga permisos de ejecución.")
            print(f"  3. Que Flatpak ('{chrome_options.binary_location}') pueda ejecutar Chrome (ej. intente `{chrome_options.binary_location} run com.google.Chrome` manualmente).")
            print("  4. Si está en un entorno sin GUI (headless server), asegúrese de que Chrome se ejecute con la opción '--headless'.")
        else:
            print("Adicional: Problema general del WebDriver o al acceder a la URL.")
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
