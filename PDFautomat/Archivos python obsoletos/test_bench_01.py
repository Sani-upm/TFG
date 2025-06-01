#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 20:09:08 2023

@author: sani
"""

#Incluimos las librerias que vamos a usar
import glob
import pandas as pd
from pypdf import PdfReader
#from openpyxl import Workbook, load_workbook
import os.path

import sys 

#vamos aobtener todos los pdf que queremos contabilizar 
globs = glob.iglob('MAKRO_SI/**.pdf')

#iteramos y obtenemos el excel 
for a in globs:
    reader = PdfReader(a) # leemos el pdf y lo metemos en un objeto reader
    hojas=len(reader.pages)         #obtenemos el numero de hojas
    page = reader.pages[hojas-1]      
    todo=page.extract_text()        #extraemos la hoja

    separado=todo.splitlines()      #separamos todo en una lista de str
    
    
######################
  
