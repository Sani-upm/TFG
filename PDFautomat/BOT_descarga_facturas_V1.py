#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 22 19:04:44 2025

@author: sani
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import shutil
import glob
import os

# Conectarse al Chrome abierto con sesión activa
options = Options()
options.debugger_address = "localhost:9222"

driver = webdriver.Chrome(options=options)

# Ir a la página principal (por si no estamos ahí)
driver.get("https://www.portalcliente.mercadona.es/pclie/web/op.htm?operation=pclie.flow.ri.home")

# Esperar y hacer clic en "Facturas ya solicitadas"
try:
    boton_facturas = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Facturas ya solicitadas')]"))
    )
    boton_facturas.click()
    print("✅ Click en 'Facturas ya solicitadas'")
except Exception as e:
    print("❌ No se pudo hacer clic:", e)
    driver.quit()
    exit()

# Esperar a que aparezca al menos una fila de factura
try:
    fila = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#tableIssuedBills tbody tr"))
    )

    # Buscar el enlace con la función doShowPdf(...)
    enlace = fila.find_element(By.CSS_SELECTOR, "a.btn-download")
    href = enlace.get_attribute("href")

    # Extraer argumentos de doShowPdf(...)
    if "doShowPdf(" in href:
        argumentos = href.split("doShowPdf(")[1].split(")")[0]
        js = f"doShowPdf({argumentos})"
        driver.execute_script(js)
        print(f"✅ Ejecutado: {js}")
    else:
        print("❌ No se pudo extraer la función doShowPdf(...)")

except Exception as e:
    print("❌ Error al intentar localizar o ejecutar la descarga:", e)


# Esperar para que se descargue
time.sleep(10)
# Carpeta donde mover el archivo
carpeta_destino = os.path.abspath("/Users/sani/TFG/PDFautomat/MERCADONA_BANCO_SI")
os.makedirs(carpeta_destino, exist_ok=True)

# Buscar el PDF más reciente en la carpeta Descargas
descargas = os.path.expanduser("~/Downloads")
pdfs = glob.glob(os.path.join(descargas, "*.pdf"))

if pdfs:
    pdf_mas_reciente = max(pdfs, key=os.path.getctime)
    nombre_archivo = os.path.basename(pdf_mas_reciente)
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)

    shutil.move(pdf_mas_reciente, ruta_destino)
    print(f"✅ Archivo movido a: {ruta_destino}")
else:
    print("❌ No se encontró ningún PDF en la carpeta de descargas.")

driver.quit()
