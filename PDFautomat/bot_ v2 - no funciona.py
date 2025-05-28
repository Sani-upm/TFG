#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 19 23:32:31 2025

@author: sani
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

correo = "sani.mitkov@gmail.com"
password_merca = "KAMEN99merca-"

options = webdriver.FirefoxOptions()
# Quitar modo headless si estuviera activo
# options.headless = False

driver = webdriver.Firefox(options=options)
driver.get("https://www.portalcliente.mercadona.es/pclie/web/op.htm?operation=pclie.flow.inicio&fwk.locale=es_ES")
time.sleep(2)  # Simula carga natural

# Clic en el botón de login
try:
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btnLogin"))
    )
    ActionChains(driver).move_to_element(login_btn).pause(1).click().perform()
    time.sleep(1)
except Exception as e:
    print("Error al hacer clic en el botón de login:", e)
    driver.quit()

# Introducir email y contraseña
try:
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    password_input = driver.find_element(By.ID, "password")

    # Simula tecleo humano
    for char in correo:
        email_input.send_keys(char)
        time.sleep(0.1)

    for char in password_merca:
        password_input.send_keys(char)
        time.sleep(0.1)

    time.sleep(1)

    # Clic en el botón de iniciar sesión
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    )
    ActionChains(driver).move_to_element(login_button).pause(1).click().perform()

except Exception as e:
    print("Error al rellenar el formulario de acceso:", e)
    driver.quit()
