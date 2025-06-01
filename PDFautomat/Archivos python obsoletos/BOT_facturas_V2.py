#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 23 19:34:46 2025

@author: sani
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

# === CONFIGURACIÓN ===
archivo_excel = "tickets_mercadona_2.xlsx"
comentario_col = "Comentario"

# === LEER EXCEL ===
df = pd.read_excel(archivo_excel, dtype=str)
df = df[df["Procesado"].isnull()]  # solo los no marcados

if df.empty:
    print("✅ Todos los tickets están procesados.")
    exit()

# === TOMAR PRIMER TICKET SIN PROCESAR ===
ticket = df.iloc[0]
index = ticket.name  # índice para modificar luego

# Parseo de datos
fecha = pd.to_datetime(ticket["Fecha"])
parte1 = str(ticket["Tienda"]).zfill(4)
parte2 = str(ticket["Caja"]).zfill(3)
parte3 = str(ticket["Ticket"]).zfill(6)
total = ticket["Total"].replace(".", ",")  # en formato europeo

print(f"🎫 Procesando ticket: {fecha.strftime('%d/%m/%Y')} - {parte1}-{parte2}-{parte3} - Total: {total}€")

# === CONECTAR A CHROME ===
options = Options()
options.debugger_address = "localhost:9222"
driver = webdriver.Chrome(options=options)

# === IR A "SOLICITAR NUEVA FACTURA" ===
driver.get("https://www.portalcliente.mercadona.es/pclie/web/op.htm?operation=pclie.flow.ri.solicitudFactura")
time.sleep(3)

# === RELLENAR FORMULARIO ===
driver.find_element(By.ID, "dateTicket").send_keys(fecha.strftime("%d/%m/%Y"))
driver.find_element(By.ID, "simplifiedBillCenter").send_keys(parte1)
driver.find_element(By.ID, "simplifiedBillBox").send_keys(parte2)
driver.find_element(By.ID, "simplifiedBillNumTicket").send_keys(parte3)
driver.find_element(By.ID, "totalBill").send_keys(total)
time.sleep(1)

# === ENVIAR FORMULARIO ===
btn = driver.find_element(By.XPATH, "//button[contains(text(),'SOLICITAR FACTURA')]")
ActionChains(driver).move_to_element(btn).pause(1).click().perform()
print("📨 Solicitud enviada.")
time.sleep(5)

# === DETECTAR MENSAJES EN EL HTML ===
html = driver.page_source

if "ya está facturado" in html:
    print("⚠️ El ticket ya fue facturado.")
    df.at[index, "Procesado"] = "x"
    df.at[index, comentario_col] = "Factura ya existe"
else:
    print("📍 Aún no detectamos el tipo de mensaje.")
    df.at[index, "Procesado"] = "?"
    df.at[index, comentario_col] = "Mensaje desconocido"
    with open("respuesta_factura.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("📝 HTML guardado como 'respuesta_factura.html' para inspección.")

# === GUARDAR EXCEL ACTUALIZADO ===
df_total = pd.read_excel(archivo_excel, dtype=str)
for col in [comentario_col, "Procesado"]:
    if col not in df_total.columns:
        df_total[col] = ""
df_total.loc[index, "Procesado"] = df.at[index, "Procesado"]
df_total.loc[index, comentario_col] = df.at[index, comentario_col]
df_total.to_excel(archivo_excel, index=False)
print(f"💾 Excel actualizado: {archivo_excel}")

driver.quit()

