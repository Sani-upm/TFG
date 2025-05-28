#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 23 18:13:27 2025

@author: sani
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time
import sys

# Cargar variables desde .env
load_dotenv(".env")
correo = os.getenv("CORREO")
password_merca = os.getenv("PASSWORD")

if not correo or not password_merca:
    print("❌ Faltan CORREO o PASSWORD en el archivo .env")
    sys.exit()

# Configurar Chrome con un perfil aislado
options = Options()
options.add_argument("--user-data-dir=chrome-login-mercadona")  # para mantener sesión futura
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Iniciar navegador
driver = webdriver.Chrome(options=options)
driver.get("https://www.portalcliente.mercadona.es/pclie/web/op.htm?operation=pclie.flow.inicio&fwk.locale=es_ES")

time.sleep(2)

# Clic en "Iniciar sesión" inicial
try:
    login_button = driver.find_element(By.ID, "btnLogin")
    ActionChains(driver).move_to_element(login_button).pause(1).click().perform()
    print("✅ Click en botón de login inicial")
except Exception as e:
    print("❌ No se encontró el botón de login:", e)
    driver.quit()
    sys.exit()

time.sleep(2)

# Simular tecleo humano en el campo de correo
try:
    email_input = driver.find_element(By.ID, "email")
    for letra in correo:
        email_input.send_keys(letra)
        time.sleep(0.05)
except Exception as e:
    print("❌ No se encontró el campo de email:", e)
    driver.quit()
    sys.exit()

# Simular tecleo humano en el campo de contraseña
try:
    password_input = driver.find_element(By.ID, "password")
    for letra in password_merca:
        password_input.send_keys(letra)
        time.sleep(0.05)
except Exception as e:
    print("❌ No se encontró el campo de contraseña:", e)
    driver.quit()
    sys.exit()

# Clic en el botón de "Iniciar sesión"
try:
    iniciar_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    )
    ActionChains(driver).move_to_element(iniciar_btn).pause(1).click().perform()
    print("✅ Se hizo clic en 'Iniciar sesión'")
except Exception as e:
    print("❌ No se pudo hacer clic en 'Iniciar sesión':", e)
    driver.quit()
    sys.exit()

# Esperar para verificar si accede
time.sleep(10)
driver.save_screenshot("login_mercadona.png")
print("📸 Captura guardada como 'login_mercadona.png'")

input("Presiona ENTER para cerrar el navegador...")
driver.quit()

