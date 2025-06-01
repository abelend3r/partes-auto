import getpass
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
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
    Automates the login process for the specified website.
    """
    driver = None
    print("\nIniciando el navegador...")
    page_load_failed = False
    try:
        driver = webdriver.Firefox()

        print(
            f"Navegando a la URL: https://hospedajes.ses.mir.es/hospedajes-sede/#/comunicacion/inicio"
        )
        # Set a page load timeout to better catch URL accessibility issues
        driver.set_page_load_timeout(30)  # 30 seconds timeout for page load
        try:
            driver.get(
                "https://hospedajes.ses.mir.es/hospedajes-sede/#/comunicacion/inicio"
            )
        except (
            TimeoutException
        ):  # Catching TimeoutException specifically for driver.get()
            page_load_failed = True  # Flag that page load itself timed out
            raise  # Re-raise to be caught by the generic TimeoutException handler below

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
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        print("Botón de inicio de sesión encontrado. Haciendo clic...")
        login_button.click()

        print("Clic en el botón de inicio de sesión realizado.")
        time.sleep(5)

        print("Proceso de inicio de sesión completado.")
        return True

    except TimeoutException:
        if page_load_failed:  # Check if the timeout was due to page load
            print("Error: No se pudo acceder a la URL especificada.")
        else:
            # This implies timeout occurred while waiting for an element
            print(
                "Error: No se pudieron encontrar los elementos necesarios en la página para el inicio de sesión."
            )
        return False
    except NoSuchElementException:
        # This specific message is for when an element is not found (less
        # likely with WebDriverWait)
        print(
            "Error: No se pudieron encontrar los elementos necesarios en la página para el inicio de sesión."
        )
        return False
    except WebDriverException as e:
        # This can be due to various WebDriver issues, including failure to connect to the browser or if geckodriver is not found/working
        # For this subtask, we'll assume it relates to URL accessibility if it
        # occurs after trying to load.
        print("Error: No se pudo acceder a la URL especificada.")
        # print(f"Detalles del WebDriverException: {e}") # For debugging
        return False
    except Exception as e:  # Catch any other unexpected errors
        print(f"Ocurrió un error inesperado: {e}")
        return False
    finally:
        if driver:
            print("Cerrando el navegador.")
            driver.quit()


if __name__ == "__main__":
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
