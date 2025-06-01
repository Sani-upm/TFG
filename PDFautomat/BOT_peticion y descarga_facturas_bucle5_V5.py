#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 20:41:06 2025

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
from datetime import datetime

# === CONFIGURACIÓN ===
EXCEL_FILE = "tickets_mercadona_2.xlsx"
TARJETAS_FILE = "tarjetas_validas.txt"
FOLDER_BANCO_SI = "MERCADONA_BANCO_SI"
FOLDER_BANCO_NO = "MERCADONA_BANCO_NO"
COLUMNA_COMENTARIO = "Comentario"
COLUMNA_PROCESADO = "Procesado"
MAX_TICKETS = 5

# === LEER EXCEL ===
df = pd.read_excel(EXCEL_FILE, dtype=str)
if COLUMNA_PROCESADO not in df.columns:
    df[COLUMNA_PROCESADO] = ""

df_pendientes = df[df[COLUMNA_PROCESADO].isnull() | (df[COLUMNA_PROCESADO] == "")].head(MAX_TICKETS)
if df_pendientes.empty:
    print("✅ Todos los tickets están procesados.")
    sys.exit()

# === LEER TARJETAS VÁLIDAS ===
with open(TARJETAS_FILE, "r") as f:
    tarjetas_validas = {line.strip() for line in f if line.strip().isdigit()}

# === CONECTAR A CHROME ===
options = Options()
options.debugger_address = "localhost:9222"
driver = webdriver.Chrome(options=options)

# === CONTADORES PARA RESUMEN ===
resumen = {"procesados_ok": 0, "ya_facturado": 0, "incorrectos": 0, "errores": 0}

# === PROCESAR TICKETS ===
for index, ticket in df_pendientes.iterrows():
    fecha = pd.to_datetime(ticket["Fecha"], dayfirst=True)
    parte1 = str(ticket["Tienda"]).zfill(4)
    parte2 = str(ticket["Caja"]).zfill(3)
    parte3 = str(ticket["Ticket"]).zfill(6)
    total = ticket["Total"].replace(".", ",")
    tarjeta = str(ticket["Tarjeta"]).strip()

    print(f"\n➡️ Procesando ticket: {fecha.strftime('%d/%m/%Y')} | {parte1}-{parte2}-{parte3} | Total: {total} | Tarjeta: {tarjeta}")

    driver.get("https://www.portalcliente.mercadona.es/pclie/web/op.htm?operation=pclie.flow.ri.solicitudFactura")
    time.sleep(2)

    try:
        driver.find_element(By.ID, "dateTicket").send_keys(fecha.strftime("%d/%m/%Y"))
        driver.find_element(By.ID, "simplifiedBillCenter").send_keys(parte1)
        driver.find_element(By.ID, "simplifiedBillBox").send_keys(parte2)
        driver.find_element(By.ID, "simplifiedBillNumTicket").send_keys(parte3)
        driver.find_element(By.ID, "totalBill").send_keys(total)
        time.sleep(1)
        ActionChains(driver).move_to_element(
            driver.find_element(By.XPATH, "//button[contains(text(),'SOLICITAR FACTURA')]")
        ).pause(1).click().perform()
        print("📨 Solicitud enviada.")
        time.sleep(5)
    except Exception as e:
        df.at[index, COLUMNA_PROCESADO] = "error"
        df.at[index, COLUMNA_COMENTARIO] = "Fallo en formulario"
        resumen["errores"] += 1
        continue

    html = driver.page_source
    if "ya está facturado" in html:
        df.at[index, COLUMNA_PROCESADO] = "x"
        df.at[index, COLUMNA_COMENTARIO] = "Factura ya existe"
        resumen["ya_facturado"] += 1
        continue
    elif "Petición incorrecta" in html:
        df.at[index, COLUMNA_PROCESADO] = "error"
        df.at[index, COLUMNA_COMENTARIO] = "Ticket incorrecto"
        resumen["incorrectos"] += 1
        continue
    elif "Últimas facturas" in html:
        try:
            enlace = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'doShowPdf')]"))
            )
            href = enlace.get_attribute("href")
            if "doShowPdf(" in href:
                args = href.split("doShowPdf(")[1].split(")")[0]
                js = f"doShowPdf({args})"

                # Marcar el tiempo justo antes de ejecutar
                momento_inicio = time.time()

                driver.execute_script(js)
                print(f"✅ Ejecutado: {js}")
                time.sleep(8)

                # Buscar PDFs nuevos descargados después del momento de ejecución
                downloads = os.path.expanduser("~/Downloads")
                nuevos = [
                    f for f in glob.glob(os.path.join(downloads, "*.pdf"))
                    if os.path.getctime(f) >= momento_inicio
                ]

                if nuevos:
                    pdf_path = max(nuevos, key=os.path.getctime)
                    destino = FOLDER_BANCO_SI if tarjeta in tarjetas_validas else FOLDER_BANCO_NO
                    os.makedirs(destino, exist_ok=True)
                    nombre_archivo = os.path.basename(pdf_path)
                    shutil.move(pdf_path, os.path.join(destino, nombre_archivo))
                    print(f"📂 PDF '{nombre_archivo}' movido a: {destino}")
                    df.at[index, COLUMNA_PROCESADO] = "x"
                    df.at[index, COLUMNA_COMENTARIO] = "Factura generada y descargada"
                    resumen["procesados_ok"] += 1
                else:
                    df.at[index, COLUMNA_PROCESADO] = "error"
                    df.at[index, COLUMNA_COMENTARIO] = "No se detectó nueva descarga"
                    resumen["errores"] += 1
                    print("❌ No se detectó nueva descarga.")
            else:
                raise ValueError("Enlace sin doShowPdf()")
        except Exception as e:
            df.at[index, COLUMNA_PROCESADO] = "error"
            df.at[index, COLUMNA_COMENTARIO] = "No se pudo lanzar doShowPdf"
            resumen["errores"] += 1
            print(f"❌ Error ejecutando doShowPdf: {e}")
    else:
        df.at[index, COLUMNA_PROCESADO] = "error"
        df.at[index, COLUMNA_COMENTARIO] = "Mensaje desconocido"
        resumen["errores"] += 1
        print("❓ Mensaje no reconocido.")

# === GUARDAR EXCEL ===
df_total = pd.read_excel(EXCEL_FILE, dtype=str)
for col in [COLUMNA_PROCESADO, COLUMNA_COMENTARIO]:
    if col not in df_total.columns:
        df_total[col] = ""
for index in df.index:
    df_total.loc[index, COLUMNA_PROCESADO] = df.at[index, COLUMNA_PROCESADO]
    df_total.loc[index, COLUMNA_COMENTARIO] = df.at[index, COLUMNA_COMENTARIO]
df_total.to_excel(EXCEL_FILE, index=False)
print(f"\n✅ Excel actualizado: {EXCEL_FILE}")

# === RESUMEN FINAL ===
print("\n📊 RESUMEN:")
print(f"  ✅ Facturas generadas y descargadas: {resumen['procesados_ok']}")
print(f"  ⚠️ Tickets ya facturados: {resumen['ya_facturado']}")
print(f"  ❌ Tickets incorrectos: {resumen['incorrectos']}")
print(f"  ❓ Otros errores: {resumen['errores']}")

driver.quit()
