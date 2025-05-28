#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 24 12:08:24 2025

@author: sani
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import glob
import shutil
import sys

# === CONFIGURACIÓN ===
EXCEL_FILE = "tickets_mercadona_2.xlsx"
TARJETAS_FILE = "tarjetas_validas.txt"
FOLDER_ERRORES = "errores_html"
FOLDER_BANCO_SI = "MERCADONA_BANCO_SI"
FOLDER_BANCO_NO = "MERCADONA_BANCO_NO"
COLUMNA_COMENTARIO = "Comentario"
COLUMNA_PROCESADO = "Procesado"

# === LEER EXCEL ===
df = pd.read_excel(EXCEL_FILE, dtype=str)
if COLUMNA_PROCESADO not in df.columns:
    df[COLUMNA_PROCESADO] = ""

df = df[df[COLUMNA_PROCESADO].isnull() | (df[COLUMNA_PROCESADO] == "")]

if df.empty:
    print("✅ Todos los tickets están procesados.")
    sys.exit()

ticket = df.iloc[0]
index = ticket.name

# === LEER TARJETAS VÁLIDAS ===
with open(TARJETAS_FILE, "r") as f:
    tarjetas_validas = {line.strip() for line in f if line.strip().isdigit()}

# === DATOS DEL TICKET ===
fecha = pd.to_datetime(ticket["Fecha"])
parte1 = str(ticket["Tienda"]).zfill(4)
parte2 = str(ticket["Caja"]).zfill(3)
parte3 = str(ticket["Ticket"]).zfill(6)
total = ticket["Total"].replace(".", ",")
tarjeta = str(ticket["Tarjeta"]).strip()

print(f"🎫 Ticket: {fecha.strftime('%d/%m/%Y')} | {parte1}-{parte2}-{parte3} | Total: {total} | Tarjeta: {tarjeta}")

# === CONECTAR A CHROME ===
options = Options()
options.debugger_address = "localhost:9222"
driver = webdriver.Chrome(options=options)

# === IR A "Solicitar nueva factura" ===
driver.get("https://www.portalcliente.mercadona.es/pclie/web/op.htm?operation=pclie.flow.ri.solicitudFactura")
time.sleep(3)

# === RELLENAR FORMULARIO ===
driver.find_element(By.ID, "dateTicket").send_keys(fecha.strftime("%d/%m/%Y"))
driver.find_element(By.ID, "simplifiedBillCenter").send_keys(parte1)
driver.find_element(By.ID, "simplifiedBillBox").send_keys(parte2)
driver.find_element(By.ID, "simplifiedBillNumTicket").send_keys(parte3)
driver.find_element(By.ID, "totalBill").send_keys(total)
time.sleep(1)

# === ENVIAR SOLICITUD ===
btn = driver.find_element(By.XPATH, "//button[contains(text(),'SOLICITAR FACTURA')]")
ActionChains(driver).move_to_element(btn).pause(1).click().perform()
print("📨 Solicitud enviada.")
time.sleep(5)

# === ANALIZAR RESPUESTA ===
html = driver.page_source

if "ya está facturado" in html:
    print("⚠️ Ya existe una factura.")
    df.at[index, COLUMNA_PROCESADO] = "x"
    df.at[index, COLUMNA_COMENTARIO] = "Factura ya existe"

elif "Petición incorrecta" in html:
    print("❌ Ticket incorrecto.")
    df.at[index, COLUMNA_PROCESADO] = "error"
    df.at[index, COLUMNA_COMENTARIO] = "Ticket incorrecto"

elif "Últimas facturas" in html:
    print("✅ Factura generada. Esperando enlace de descarga...")

    try:
        enlace = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'doShowPdf')]"))
        )
        href = enlace.get_attribute("href")
        if "doShowPdf(" in href:
            args = href.split("doShowPdf(")[1].split(")")[0]
            js = f"doShowPdf({args})"
            driver.execute_script(js)
            print(f"✅ Ejecutado: {js}")
        else:
            raise ValueError("href no contenía doShowPdf()")
    except Exception as e:
        print(f"❌ Error ejecutando doShowPdf(): {e}")
        os.makedirs(FOLDER_ERRORES, exist_ok=True)
        nombre_html = f"{fecha.strftime('%Y%m%d')}_{parte1}-{parte2}-{parte3}_no_pdf.html"
        with open(os.path.join(FOLDER_ERRORES, nombre_html), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        df.at[index, COLUMNA_PROCESADO] = "error"
        df.at[index, COLUMNA_COMENTARIO] = "No se pudo lanzar doShowPdf"
        driver.quit()
        sys.exit()

    # === MOVER PDF DESCARGADO ===
    time.sleep(5)
    downloads = os.path.expanduser("~/Downloads")
    pdfs = glob.glob(os.path.join(downloads, "*.pdf"))
    if not pdfs:
        print("❌ No se encontró ningún PDF.")
        df.at[index, COLUMNA_PROCESADO] = "error"
        df.at[index, COLUMNA_COMENTARIO] = "PDF no detectado"
    else:
        archivo_pdf = max(pdfs, key=os.path.getctime)
        destino = FOLDER_BANCO_SI if tarjeta in tarjetas_validas else FOLDER_BANCO_NO
        os.makedirs(destino, exist_ok=True)
        shutil.move(archivo_pdf, os.path.join(destino, os.path.basename(archivo_pdf)))
        print(f"📂 PDF movido a: {destino}")
        df.at[index, COLUMNA_PROCESADO] = "x"
        df.at[index, COLUMNA_COMENTARIO] = "Factura generada y descargada"

else:
    print("❓ Mensaje no reconocido. Guardando HTML...")
    os.makedirs(FOLDER_ERRORES, exist_ok=True)
    nombre_html = f"{fecha.strftime('%Y%m%d')}_{parte1}-{parte2}-{parte3}.html"
    with open(os.path.join(FOLDER_ERRORES, nombre_html), "w", encoding="utf-8") as f:
        f.write(html)
    df.at[index, COLUMNA_PROCESADO] = "error"
    df.at[index, COLUMNA_COMENTARIO] = "Mensaje desconocido"

# === GUARDAR EXCEL ACTUALIZADO ===
df_total = pd.read_excel(EXCEL_FILE, dtype=str)
for col in [COLUMNA_PROCESADO, COLUMNA_COMENTARIO]:
    if col not in df_total.columns:
        df_total[col] = ""
df_total.loc[index, COLUMNA_PROCESADO] = df.at[index, COLUMNA_PROCESADO]
df_total.loc[index, COLUMNA_COMENTARIO] = df.at[index, COLUMNA_COMENTARIO]
df_total.to_excel(EXCEL_FILE, index=False)

print(f"✅ Excel actualizado: {EXCEL_FILE}")
driver.quit()


