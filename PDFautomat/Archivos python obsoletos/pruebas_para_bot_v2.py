#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 23 19:41:43 2025

@author: sani
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Conexión a Chrome ya abierto con --remote-debugging-port=9222
options = Options()
options.debugger_address = "localhost:9222"

driver = webdriver.Chrome(options=options)

# Ir directamente a "Solicitar nueva factura"
driver.get("https://www.portalcliente.mercadona.es/pclie/web/op.htm?operation=pclie.flow.ri.solicitudFactura")

# Esperar unos segundos a que la página cargue
time.sleep(5)

# Guardar el HTML completo de la página
with open("formulario_factura.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("✅ HTML guardado como 'formulario_factura.html'. Por favor, súbelo aquí para que pueda inspeccionarlo.")

input("Presiona ENTER para cerrar el navegador...")
driver.quit()
