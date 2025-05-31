import os
import re
import subprocess
import time
import shutil
import traceback
from time import sleep

from selenium import webdriver
from selenium.common import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

from flask import current_app

from app.utils.LogService import LogService
from app.repositories.documento_repository import DocumentoRepository
from app.utils.funciones import backup_compressed_file


# Se inicializa nombre de tarea
TASK_NAME = "davibox.py"

class SeleniumBot:
    def __init__(self, download_folder):
        self.download_folder = download_folder
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        options = Options()
        options.add_experimental_option('prefs', {
            "download.default_directory": self.download_folder,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": False
        })
        options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--remote-debugging-port=9222")  # Ensure DevTools port is set
        options.add_argument("--disable-software-rasterizer")  # Improve performance
        options.add_argument("--disable-blink-features=AutomationControlled") # Helps prevent bot detection.
        options.add_experimental_option("detach", True)

        try:
            # Usar el ChromeDriver instalado en Docker
            chromedriver_path = current_app.config['WEBSCRAPING']['ChromeDriverPath']
            print(f"Usando ChromeDriver en la ruta: {chromedriver_path}")

            # Verificar si ChromeDriver está disponible
            if not os.path.exists(chromedriver_path):
                raise Exception("⚠️ ChromeDriver no está instalado en la ruta esperada.")
            
            self.driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
            self.wait = WebDriverWait(self.driver, 15)
            print("✅ WebDriver iniciado correctamente.")

        except Exception as e:
            print(f"❌ Error al iniciar el WebDriver: {e}")
            raise
    
    def get_chrome_version(self):
        """
        Detecta la versión de Chromium instalada en el sistema.
        Retorna la versión como string (Ejemplo: "90.0.4430.212") o None si falla.
        """
        try:
            output = subprocess.check_output(["chromium", "--version"]).decode("utf-8")
            version_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
            return version_match.group(1) if version_match else None
        except Exception as e:
            print(f"Error al obtener la versión de Chromium: {e}")
            return None
        
    def login(self, url, username, password):
        try:            
            # Check if already logged in (before navigating)
            if self.is_logged_in():
                print("Session is already active.")
                LogService.audit_log("Session is already active.", TASK_NAME)
                return True
            print("Verificando WebDriver antes de cargar la URL...")
            print(f"URL actual: {self.driver.current_url}")
            self.driver.get(url)
            time.sleep(3)  # Esperar un poco para ver si la carga funciona

            print(f"URL después de cargar: {self.driver.current_url}")
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
            )
            LogService.audit_log("Iniciando sesión", TASK_NAME)
            self.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(username)
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div/form[3]/div/div/div/div/div[2]/input[2]').send_keys(password)
            time.sleep(5)
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div/form[3]/div/div/div/div/div[3]/button').click()
            
            # Wait for a successful login
            if self.is_logged_in():
                print("Inicio de sesion exitoso")
                LogService.audit_log("Inicio de sesion exitoso", TASK_NAME)
                return True
            else:
                print("Inicio de sesion fallido")
                LogService.audit_log("Inicio de sesion fallido", TASK_NAME)
                return False
        except Exception as e:

            # Captura el traceback completo
            error_trace = traceback.format_exc()
            
            # Registra el error en logs (si usas logging, puedes integrarlo aquí)
            print("Traceback completo del error:")
            print(error_trace)
            print(f"Error al iniciar sesión: {e}")
            LogService.error_log(f"Error al iniciar sesión: {e}", TASK_NAME)
            return False
        
    def is_logged_in(self):
        try:
            # Replace with a unique element that only appears when logged in
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "accountLink"))
            )
            LogService.audit_log("Sesion iniciada exitosamente", TASK_NAME)
            return True 
        except:
            return False

    def logout(self, url):
        max_retries = 3
        attempt = 0
        logout_successful = False
        
        while attempt < max_retries and not logout_successful:
            try:
                user_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[1]/form/table/tbody/tr/td[2]/div/a[1]')
                self.safe_click(user_button)
                time.sleep(1)
                logout_button = self.driver.find_element(By.XPATH, '/html/body/div[6]/ul/li[7]/a/span/table/tbody/tr/td/a')
                self.safe_click(logout_button)
                
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
                )
                logout_successful = True
                print("Cierre de sesión exitoso.")
                LogService.audit_log("Cierre de sesión exitoso.", TASK_NAME)
                
            except Exception as e:
                attempt += 1
                LogService.audit_log(f"Intento de cerrar sesión fallido. Intento {attempt}/{max_retries}. Error: {str(e)}", TASK_NAME)
                
                if attempt < max_retries:
                    try:
                        if len(self.driver.window_handles) > 0:
                            self.driver.close()
                        
                        if len(self.driver.window_handles) == 0:
                            self.driver.switch_to.new_window('tab')
                        else:
                            self.driver.switch_to.window(self.driver.window_handles[0])
                        
                        # Navega a la URL y verifica el estado de la sesión
                        self.driver.get(url)
                        time.sleep(2)
                        
                        if self.is_logged_in():
                            LogService.audit_log("Sesión aún activa. Reintentando cierre de sesión", TASK_NAME)
                        else:
                            logout_successful = True
                            print("Sesión cerrada exitosamente (por timeout o redirección).")
                            LogService.audit_log("Sesión cerrada exitosamente.", TASK_NAME)
                            
                    except Exception as recovery_error:
                        LogService.audit_log(f"Error en recuperación: {str(recovery_error)}", TASK_NAME)
        
        if logout_successful:
            self.driver.quit()
        else:
            LogService.audit_log("No se pudo cerrar sesión después de todos los intentos", TASK_NAME)
            self.driver.quit()

    def _wait_for_download(self, timeout=600):
        """
        Espera a que se complete una descarga verificando la desaparición del archivo temporal.
        """
        seconds = 0
        while seconds < timeout:
            files = os.listdir(self.download_folder)
            tmp_files = [f for f in files if f.endswith('.crdownload') or f.endswith('.part') or f.endswith('.tmp')]
            if not tmp_files:
                completed_files = [os.path.join(self.download_folder, f) for f in files]
                if completed_files:
                    print(f"Archivos completados: {completed_files}")
                    return max(completed_files, key=os.path.getctime)
            time.sleep(1)
            seconds += 1
        LogService.error_log("Descarga no completó dentro del tiempo esperado.", TASK_NAME)
        raise TimeoutError("La descarga no se completó dentro del tiempo esperado.")

    def obtener_xpath_por_texto(self, xpath_base, texto_buscar):
        """
        Recorre las filas de una tabla para encontrar el texto especificado y devuelve su XPATH.

        :param self: Instancia del WebDriver.
        :param xpath_base: XPATH base de las filas de la tabla, sin el índice de fila.
        :param texto_buscar: Texto a buscar en la columna específica.
        :return: XPATH completo del elemento si se encuentra el texto, None en caso contrario.
        """
        max_retries = 3  # Número máximo de intentos en caso de error por "stale element"
        
        for attempt in range(max_retries):
            try:
                wait = WebDriverWait(self.driver, 10)

                # Esperar a que la tabla esté presente en el DOM
                tabla = wait.until(EC.presence_of_element_located((By.XPATH, xpath_base)))
                # Esperar a que al menos una fila esté presente
                wait.until(EC.presence_of_element_located((By.XPATH, f"{xpath_base}/tr")))

                filas = self.driver.find_elements(By.XPATH, f"{xpath_base}/tr")  # Obtiene todas las filas de la tabla

                if not tabla:
                    print("⚠️ La tabla no se encuentra en el DOM.")
                    LogService.audit_log("⚠️ La tabla no se encuentra en el DOM.", TASK_NAME)
                    return None
                
                if not filas:
                    print("⚠️ La tabla no tiene filas disponibles.")
                    LogService.audit_log("⚠️ La tabla no tiene filas disponibles.", TASK_NAME)
                    return None
                
                for i, fila in enumerate(filas, start=1):  # Itera por el índice de fila (empieza desde 1)
                    try:
                        texto_columna = fila.find_element(By.XPATH, f"{xpath_base}/tr[{i}]/td[3]/a").text  # Obtiene el texto de la columna
                        print(f"Fila {i}: {texto_columna}")  # Imprime el texto para depuración
                        LogService.audit_log(f"Fila {i}: {texto_columna}", TASK_NAME)
                        
                        if texto_columna.strip() == texto_buscar.strip():  # Verifica si el texto coincide
                            xpath_encontrado = f"{xpath_base}/tr[{i}]/td[3]/a"
                            print(f"✅ Texto '{texto_buscar}' encontrado. XPATH: {xpath_encontrado}")
                            LogService.audit_log(f"✅ Texto '{texto_buscar}' encontrado. XPATH: {xpath_encontrado}", TASK_NAME)
                            return xpath_encontrado
                    
                    except NoSuchElementException:
                        print(f"⚠️ No se encontró el enlace en la fila {i}.")
                        LogService.audit_log(f"⚠️ No se encontró el enlace en la fila {i}.", TASK_NAME)

                print(f"❌ Texto '{texto_buscar}' no encontrado en la tabla.")
                LogService.audit_log(f"❌ Texto '{texto_buscar}' no encontrado en la tabla.", TASK_NAME)
                return None

            except StaleElementReferenceException:
                print(f"⚠️ Intento {attempt+1}/{max_retries}: Elemento obsoleto, reintentando...")
                LogService.audit_log(f"⚠️ Intento {attempt+1}/{max_retries}: Elemento obsoleto, reintentando...", TASK_NAME)
                continue  # Reintentar en caso de error por actualización del DOM

            except Exception as e:
                print(f"❌ Error inesperado al recorrer la tabla: {e}")
                LogService.error_log(f"❌ Error inesperado al recorrer la tabla: {e}", TASK_NAME)
                return None

        print("❌ No se pudo procesar la tabla después de varios intentos.")
        LogService.error_log("❌ No se pudo procesar la tabla después de varios intentos.", TASK_NAME)
        return None

    def download_file(self, url, username, password):
        login = self.login(url, username, password)
        if not login:
            print("Error: No se pudo iniciar sesión en la página.")
            LogService.error_log("Error: No se pudo iniciar sesión en la página.", TASK_NAME)
            raise Exception("No fue posible iniciar sesion en Davibox")

        LogService.audit_log("Iniciando descarga", TASK_NAME)
        try:
            # Ruta de la carpeta de descargas
            download_folder = self.download_folder
            # Verifica si la carpeta existe y elimina todos los archivos dentro
            if os.path.exists(download_folder):
                for archivo in os.listdir(download_folder):
                    archivo_path = os.path.join(download_folder, archivo)
                    try:
                        if os.path.isfile(archivo_path) or os.path.islink(archivo_path):
                            os.unlink(archivo_path)  # Eliminar archivo o enlace
                        elif os.path.isdir(archivo_path):
                            shutil.rmtree(archivo_path)  # Eliminar carpeta
                    except Exception as e:
                        print(f"Error al eliminar {archivo_path}: {e}")
                        LogService.error_log(f"Error al eliminar {archivo_path}: {e}", TASK_NAME)

            xpath = '/html/body/div[1]/div[3]/div[2]/div[6]/div/form/div[1]/div/table/tbody'
            texto_a_buscar = current_app.config['WEBSCRAPING']['CarpetaDescarga']
            
            resultado = self.obtener_xpath_por_texto(xpath, texto_a_buscar)
            
            if resultado:
                self.driver.find_element(By.XPATH, resultado).click()
                time.sleep(2)
                self.driver.find_element(By.XPATH, '//*[@id="fileListForm:j_id_8w:j_id_8y"]/div/div[2]/span').click()
                time.sleep(1)
                self.driver.find_element(By.XPATH, '//*[@id="downloadFiles:downloadFiles"]/span').click()
                time.sleep(2)
                downloaded_file = self._wait_for_download()
                print(f"Archivo descargado: {downloaded_file}")
                LogService.audit_log(f"Archivo descargado: {downloaded_file}", TASK_NAME)
                
                backup_compressed_file(downloaded_file)
                
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "breadcrumbForm:j_id_8q:0:j_id_8r"))
                ).click()
                
                # Eliminacion de archivos
                # self.delete_files(url, username, password)
                return downloaded_file
            else:
                print("No se encontró el texto, no se descargará el archivo.")
                LogService.audit_log("No se encontró el texto, no se descargará el archivo.", TASK_NAME)
                return None
        except Exception as e:
            print(f"Error al descargar el archivo: {e}")
            LogService.error_log(f"Error al descargar el archivo: {e}", TASK_NAME)
            return None
        finally:
            self.logout(url)

    def delete_files(self, url: str, username: str, password: str):
        if not self.login(url, username, password):
            print("Error: No se pudo iniciar sesión en la página.")
            return False

        try:
            xpath = '//*[@id="fileListForm:j_id_8w_data"]'
            texto_a_buscar = current_app.config['WEBSCRAPING']['CarpetaDescarga']
            resultado = self.obtener_xpath_por_texto(xpath, texto_a_buscar)

            if not resultado:
                print("No se encontró la carpeta, por lo cual no se puede continuar con el proceso de eliminación de archivos.")
                return False

            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, resultado)))

            self.driver.find_element(By.XPATH, resultado).click()
            time.sleep(2)

            self._procesar_subcarpetas()
            return True

        except Exception as e:
            print(f"Error al eliminar archivos: {e}")
            return False
        finally:
            self.logout(url)

    def _procesar_subcarpetas(self):
        xpath = '//*[@id="fileListForm:j_id_8w_data"]/tr'
        filas = self.driver.find_elements(By.XPATH, xpath)
        for i in range(1, len(filas) + 1):
            try:
                self._procesar_subcarpeta_por_indice(i)
            except Exception as e:
                error_line = traceback.format_exc()
                print(f"Error al interactuar con la carpeta: {e}\nDetalles:\n{error_line}")

    def _procesar_subcarpeta_por_indice(self, i):
        xpath = '//*[@id="fileListForm:j_id_8w_data"]'
        filas = self.driver.find_elements(By.XPATH, f"{xpath}/tr")
        fila = filas[i - 1]
        texto_columna = fila.find_element(By.XPATH, f"{xpath}/tr[{i}]/td[3]/a").text
        print(f"Procesando carpeta: {texto_columna}")
        fila.find_element(By.XPATH, f"{xpath}/tr[{i}]/td[3]/a").click()
        time.sleep(2)

        self._eliminar_archivos_en_subcarpeta()

        # Volver a carpeta principal
        print("Regresando a la carpeta principal...")
        carpeta_principal = self.driver.find_element(By.XPATH, '//*[@id="breadcrumbForm:j_id_8q:1:j_id_8r"]')
        actions = webdriver.ActionChains(self.driver)
        actions.move_to_element(carpeta_principal).perform()
        carpeta_principal.click()
        time.sleep(2)

    def _eliminar_archivos_en_subcarpeta(self):
        xpath_paginador = '//*[@id="fileListForm:j_id_8w_paginator_bottom"]/span[2]/a'
        cantidad_elementos = len(self.driver.find_elements(By.XPATH, xpath_paginador))
        print(f"Número de elementos en el paginador: {cantidad_elementos}")

        indice = 0
        intentos = 0
        max_intentos = 15

        archivos_seleccionados = []

        while intentos < max_intentos:
            try:
                # Verifica si la carpeta está vacía
                texto = self.driver.find_element(By.XPATH, '//*[@id="fileListForm:j_id_8w_data"]/tr/td[1]').text
                if texto in ["Este directorio está vacío.", "This directory is empty."]:
                    print("No se encontraron archivos en la carpeta.")
                    break

                bln_eliminacion = self._seleccionar_archivos_para_eliminar(archivos_seleccionados)

                btn_eliminar_xpath = '//*[@id="deleteFiles:deleteFiles"]/span'
                btn_confirmar = '//*[@id="deleteFiles:j_id_at:j_id_ay:j_id_b1"]/span'

                if bln_eliminacion:
                    try:
                        self.wait.until(EC.presence_of_element_located((By.XPATH, btn_eliminar_xpath)))
                        btn_eliminar = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_eliminar_xpath)))
                        btn_eliminar.click()
                        print("Clic en botón de eliminar.")

                        # Esperar a que aparezca el modal de confirmación
                        self.wait.until(EC.presence_of_element_located((By.XPATH, btn_confirmar)))
                        btn_confirmar = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_confirmar)))
                        btn_confirmar.click()
                        print("Clic en botón de confirmar.")

                        print("Archivos eliminados con exito.")
                        archivos_seleccionados = []

                    except Exception as e:
                        intentos += 1
                        print(f"Fallo al intentar eliminar archivos: {e}")
                        continue

                else:
                    elementos = self.driver.find_elements(By.XPATH, xpath_paginador)
                    if indice < len(elementos):
                        print(f"Clic en el elemento {indice + 1} de {cantidad_elementos}")
                        elementos[indice].click()
                        time.sleep(2)
                        indice += 1
                    else:
                        break

            except StaleElementReferenceException:
                print("Elemento del paginador no encontrado. Reintentando...")
                intentos += 1
                continue
            except Exception as e:
                print(f"Error en el bucle: {e}")
                break

    def _seleccionar_archivos_para_eliminar(self, archivos_seleccionados) -> bool:
        xpath_subfolder = '//*[@id="fileListForm:j_id_8w"]/div[1]/table/tbody'
        filas_subfolder = self.driver.find_elements(By.XPATH, f"{xpath_subfolder}/tr")

        bln_eliminacion = False

        for j in range(1, len(filas_subfolder) + 1):
            fila_actual = filas_subfolder[j - 1]
            texto_archivo = fila_actual.find_element(By.XPATH, f"{xpath_subfolder}/tr[{j}]/td[3]").text

            if texto_archivo not in archivos_seleccionados:
                if DocumentoRepository.exists_by_nombre_archivo(texto_archivo):
                    print(f"Se encontró el archivo a eliminar en la BD: {texto_archivo}")
                    checkbox = fila_actual.find_element(By.XPATH,
                                                        f"{xpath_subfolder}/tr[{j}]/td[1]//input[@type='checkbox']")
                    self.safe_click(checkbox)

                    archivos_seleccionados.append(texto_archivo)
                    bln_eliminacion = True
            else:
                bln_eliminacion = True

        return bln_eliminacion

    def safe_click(self, element):
        try:
            element.click()
        except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException, NoSuchElementException) as e:
            try:
                self.driver.execute_script("arguments[0].click();", element)
            except Exception as js_e:
                print(f"[safe_click] Falló también con JS: {js_e}")
        except Exception as e:
            print(f"[safe_click] Falló: {e}")

    def upload_files(self, url, username, password, files):
        login = self.login(url, username, password)
        if not login:
            print("Error: No se pudo iniciar sesión en la página.")
            LogService.error_log("Error: No se pudo iniciar sesión en la página.", TASK_NAME)
            raise Exception("No fue posible iniciar sesion en Davibox")

        LogService.audit_log("Iniciando subida de documentos", TASK_NAME)
        try:
            if isinstance(files, str):
                files_to_upload = files
            elif isinstance(files, list):
                files_to_upload = "\n".join(files) # Une las rutas
            else:
                raise TypeError("El parámetro 'files' debe ser un string o una lista de strings.")

            #En caso de que al iniciar sesion se redirija al panel, entonces se dara click en archivos para continuar con la subida de los documentos
            try:
                archivo_inicio = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="j_id_6n:j_id_6u"]/tbody/tr[1]/td/h3/a'))
                )
                archivo_inicio.click()
            except TimeoutException:
                pass

            # Ruta de los archivos a subir

            xpath = '/html/body/div[1]/div[3]/div[2]/div[6]/div/form/div[1]/div/table/tbody'
            texto_a_buscar = current_app.config['WEBSCRAPING']['CarpetaSubida']

            resultado = self.obtener_xpath_por_texto(xpath, texto_a_buscar)

            if resultado:
                self.driver.find_element(By.XPATH, resultado).click()
                time.sleep(2)
                self.driver.find_element(By.XPATH, '//*[@id="toolBarForm:j_id_7r"]/span').click()
                time.sleep(2)
                self.driver.find_element(By.XPATH, '//input[@type="file"]').send_keys(files_to_upload)
                #  Verificar subida de archivos
                try:
                    WebDriverWait(self.driver, 600).until(
                        lambda driver : "cargando" not in self.driver.find_element(By.XPATH, '//*[@id="j_id_bd_1"]/div/div/span[2]').text.lower())
                    upload_message = self.driver.find_element(By.XPATH, '//*[@id="j_id_bd_1"]/div/div/span[2]').text.lower()
                    if upload_message and "terminada" in upload_message:
                        print("✅ Archivos subidos con exito")
                        LogService.audit_log("✅ Archivos subidos con exito", TASK_NAME)
                    elif upload_message and "advertencias" in upload_message:
                        print("⚠️ Archivos subidos con advertencias")
                        LogService.audit_log("⚠️ Archivos subidos con advertencias", TASK_NAME)
                    else:
                        print("Error al cargar los archivos")
                        LogService.audit_log("❌ Error al cargar los archivos", TASK_NAME)
                except TimeoutException:
                    print("Tiempo de espera superado.")
                return None
            else:
                print("No se encontró el texto, no se subiran los documentos.")
                LogService.audit_log("No se encontró el texto, no se subiran los documentos.", TASK_NAME)
                return None
        except Exception as e:

            # Captura el traceback completo
            error_trace = traceback.format_exc()
            
            # Registra el error en logs (si usas logging, puedes integrarlo aquí)
            print("Traceback completo del error:")
            print(error_trace)
            print(f"Error al subir los archivos: {e}")
            LogService.error_log(f"Error al subir los archivos: {e}", TASK_NAME)
            return None
        finally:
            self.logout(url)