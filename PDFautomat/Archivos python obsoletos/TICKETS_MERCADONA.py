#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 12:50:22 2023

@author: sani
"""

#Incluimos las librerias que vamos a usar
import glob
import pandas as pd
from pypdf import PdfReader
#from openpyxl import Workbook, load_workbook
import os.path

import sys
import re
import shutil 

#vamos aobtener todos los pdf que queremos contabilizar 
globs = glob.iglob('TICKETS_MERCADONA_UNREAD/**.pdf')

#iteramos y obtenemos el excel 
for a in globs:
    reader = PdfReader(a) # leemos el pdf y lo metemos en un objeto reader
    hojas=len(reader.pages)         #obtenemos el numero de hojas
    
    for k in range(hojas):                  #Vamos a iterar las hojas para buscar "DETALLE (€)"
        page = reader.pages[k]      
        todo=page.extract_text()            #extraemos la hoja
        

    separado=todo.splitlines()      #separamos todo en una lista de str
    max_index=len(separado)-1       #obtenemos el maximo indice
    total_factura=0                 #creamos variable que va a almacenar el total de la factura
    
    'fecha'
    for i in separado:
        match = re.search(r'../../....', i)
        if match:
          fecha = match.group() ## 'found word:cat'
    'Numero de tienda, numero de caja, numero de ticket'
    for i in separado:
        if i.find("FACTURA SIMPLIFICADA:")!=-1:
            factura=i
            match = re.search(r'\d\d\d\d', factura)
            if match:
              tienda = int(match.group())
            match = re.search(r'-\d\d\d-', factura)
            if match:
              caja = match.group()
              caja=int(caja.replace('-',''))
            match = re.search(r'\d\d\d\d\d\d', factura)
            if match:
              ticket = int(match.group())
            factura=factura.replace('FACTURA SIMPLIFICADA: ', '')  
    'Precio'
    for i in separado:
        if i.find("TOTAL (€)")!=-1:
            precio=i          
            precio=precio.replace('TOTAL (€)', '')
            precio=float(precio.replace(',', '.'))
    'Tarjeta bancaria'          
    for i in separado:
        if i.find("TARJ. BANCARIA:")!=-1:
            tarjeta=i
            match = re.search(r'\d\d\d\d', tarjeta)
            if match:
              tarjeta_termina = int(match.group())
              if  tarjeta_termina == 8313:   ### Y MOVEMOS LOS PDF A LAS DISTINTAS CARPETAS
                  Banco ='SI'
                  new_dir=[]
                  new_path=a
                  new_path=new_path.replace('UNREAD', 'READ_8313')
                  new_dir = shutil.move(a,new_path)
              elif tarjeta_termina == 8305:
                      Banco ='SI'
                      new_dir=[]
                      new_path=a
                      new_path=new_path.replace('UNREAD', 'READ_8305')
                      new_dir = shutil.move(a,new_path)
              else:
                  Banco ='NO'
                  new_dir=[]
                  new_path=a
                  new_path=new_path.replace('UNREAD', 'READ_REST')
                  new_dir = shutil.move(a,new_path)
                  
     
    '-----------------------------------------'
    #AQUI MONTAMOS LA ESTRUCTURA PARA EL EXCEL
    '-----------------------------------------'
    data = []
    
    dict={'FECHA':fecha,'FACTURA SIMPLIFICADA':factura,'TIENDA':tienda,'CAJA':caja,'TICKET':ticket,'TOTAL':precio,'TARJETA':tarjeta_termina,'BANCO':Banco, 'FACTURA PEDIDA': None, 'FACTURA RECIBIDA': None}
    
    data.append(dict)
   
    
    '-----------------------------------------'
    #AQUI METEMOS EN EL EXCEL
    '-----------------------------------------'    
    
    df = pd.DataFrame(data) #Convertimos a formato pandas
    ARCHIVO = "TICKETS_MERCADONA.xlsx"

    ##COmprobamos si el archivo existe, si no existe lo creamos con los headers (Fecha,tipo,etc.)
    check_file = os.path.isfile(ARCHIVO)
    if check_file == False:
        df.to_excel(ARCHIVO,index=False)

    
    #si ya existe solo queremos que se vaya añadiendo, sin el header
    #para ello tenemos que saber a partir de donde tiene que escribir por eso leemos primero el archivo
    #y sacamos las filas (row) y le sumamos 1 porque no cuenta el header del principio
    else:
        df1 = pd.read_excel(ARCHIVO,sheet_name="Sheet1")
        
        #Buscamos si la factura ya esta en el excel
        df2 = []
        df2 = df1.loc[df1["FACTURA SIMPLIFICADA"]==factura]
        
        if df2.empty is False:
            print("\n")
            print(factura, "contabilizada" )
            print(df2)      #imprimimos para ver donde esta
            print("\n")
            continue        #si ya esta pues nada, pasamos a la siguiente factura
            
        
        #la factura no esta en el excel por lo que obtenemos los rows para saber donde escribir    
        max_row=len(df1)+1
        #print(max_row)
        with pd.ExcelWriter(ARCHIVO,mode="a",if_sheet_exists="overlay") as writer:
            df.to_excel(writer,index=False,header=False,startrow=max_row) #index=None,columns=None
        
    




