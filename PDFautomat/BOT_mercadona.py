#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 12:59:39 2023

@author: sani
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

correo = "sani.mitkov@gmail.com"
password_merca = "lokisimO41-m"
driver = webdriver.Firefox()
driver.get("https://www.portalcliente.mercadona.es/pclie/web/op.htm?operation=pclie.flow.inicio&fwk.locale=es_ES")

#Comprobamos que efectivamente estamos en el portal del Cliente de MERCADONA
assert "Portal del Cliente - Inicio" in driver.title
 

"Hacemos Click en el boton de LOGIN"
driver.find_element(By.ID,"btnLogin").click()
#print(driver.page_source)

'Introducimos el correo y la contraseña'

email = driver.find_element(By.ID, "email")
email.send_keys(correo)

password = driver.find_element(By.ID, "password")
password.send_keys(password_merca)

'Le damos a INICAR SESION'
driver.find_element(By.XPATH,'//button[@class="btn btn-primary" ]').click()


assert "No results found." not in driver.page_source



