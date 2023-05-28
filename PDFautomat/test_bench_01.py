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
globs = glob.iglob('INPUT/**.pdf')

#iteramos y obtenemos el excel 
for a in globs:
    reader = PdfReader(a) # leemos el pdf y lo metemos en un objeto reader
    hojas=len(reader.pages)         #obtenemos el numero de hojas
    page = reader.pages[hojas-1]      
    todo=page.extract_text()        #extraemos la hoja

    separado=todo.splitlines()      #separamos todo en una lista de str



######################
   def visitor_body(text, cm, tm, font_dict, font_size):
       #y va de 0 a 900 mas o menos por lo que estoy viendo...
        
        
        if tm[4]>200 and tm[4]<500 and tm[5]>-450 and tm[5]<-250:  #de aqui sacamos los ivas... pero creo que esto no es muy reutilizable...
            
            if len(text) > 1:
                parts.append(text)
                
        if tm[4]>300 and tm[4]<500 and tm[5]>-200 and tm[5]<-140:
             
             if len(text) > 1:
                 parts.append(text)
        if tm[4]>0 and tm[4]<600 and tm[5]>-100 and tm[5]<-90:
         
         if len(text) > 1:
             print(tm)
             print(text)
             parts.append(text)   
        
            
    page.extract_text(visitor_text=visitor_body)
    #print(parts)
     
    todo=page.extract_text()#extraemos la hoja
   
    separado=todo.splitlines()      #separamos todo en una lista de str


