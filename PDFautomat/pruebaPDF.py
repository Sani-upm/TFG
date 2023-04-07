#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 10:41:29 2023

@author: sani
"""
#Incluimos las librerias que vamos a usar
import pandas as pd
from pypdf import PdfReader
from openpyxl import Workbook, load_workbook
import os.path

import sys 

#glob para reiterar todos los pdf en un directorio



reader = PdfReader("A-V2023-00000698540.pdf")
#reader = PdfReader("A-V2023-00000698555.pdf") # leemos el pdf y lo metemos en un objeto reader
hojas=len(reader.pages)         #obtenemos el numero de hojas
page = reader.pages[hojas-1]    #la informacion esta en la ultima hoja
todo=page.extract_text()        #extraemos la hoja

separado=todo.splitlines()      #separamos todo en una lista de str
max_index=len(separado)-1       #obtenemos el maximo indice


# Obtenemos iformacion de la factura como el numero de factra y fecha y lo guardamos en una lista
for i in separado:
    if i.find("Nº Factura:")!=-1:
        factura =i
        factura=factura.split() #me interesan los indices 2 (nº factura) y el 5 (fecha factura)
        factura[0]=factura[0]+(' ')+factura[1]
        factura.pop(1)
        factura[2]=factura[2]+(' ')+factura[3]
        factura.pop(3)
        #factura=pd.Series(factura)
##------------------------------------------------------------------------        
'''' Obtenemos la siguiente estructura 
['Nº Factura:', 'A-V2023-00000698540', 'Fecha Factura:', '21/02/2023'] '''
#------------------------------------------------------------------------ 
'''IVA - tenemos las lineas separadas, ahora vamos a separar segun el tipo de iva'''

#Buscamos dentro de la factura el DETALLE (€) de las bases y el iva
for x in range (max_index):
    if separado[x].find("DETALLE")==0:
        detalle=x             # obtenemos el indice a partir del cual buscaremos el iva
        break
    
   

#0% y lo guaramos en la variable cero
for i in range(detalle,max_index):
    j=separado[i]
    if j.find(" 0%")!=-1:
        cero=j
        cero=cero.split()
        #cero.pop(0)
        cero[1]=float(cero[1].replace(',','.'))
        cero[2]=float(cero[2].replace(',','.'))
        cero[3]=float(cero[3].replace(',','.'))
        #cero=pd.Series(cero)   
        break
    else:
        cero=None  #Si no hay iva del 0% nos devuelve un -1
#------------------------------------------------------------------------        
        ''''                                   tipo  base    iva   total '''
'''obtenemos la siguiente estructura cero = [ '0%', '9,85', '0', '9,85'] '''      
#------------------------------------------------------------------------   
        
# 4% y lo guaradmos en cuatro    
for i in range(detalle,max_index):
    j=separado[i]
    if j.find("4%")!=-1:
        cuatro=j
        cuatro=cuatro.split()
        #cuatro.pop(0)
        cuatro[1]=float(cuatro[1].replace(',','.'))
        cuatro[2]=float(cuatro[2].replace(',','.'))
        cuatro[3]=float(cuatro[3].replace(',','.'))
        #cuatro=pd.Series(cuatro)  
        break
    else:
        cuatro=None
        
        
# 5% y lo guardamos en cinco    
for i in range(detalle,max_index):
    j=separado[i]
    if j.find("5%")!=-1:
        cinco=j
        cinco=cinco.split()
        #cinco.pop(0)
        cinco[1]=float(cinco[1].replace(',','.'))
        cinco[2]=float(cinco[2].replace(',','.'))
        cinco[3]=float(cinco[3].replace(',','.'))
        #cinco=pd.Series(cinco)  
        break
    else:
        cinco=None
        
        
# 10% y lo guardamos en diez    
for i in range(detalle,max_index):
    j=separado[i]
    if j.find("10%")!=-1:
        diez=j
        diez=diez.split()
        #diez.pop(0)
        diez[1]=float(diez[1].replace(',','.'))
        diez[2]=float(diez[2].replace(',','.'))
        diez[3]=float(diez[3].replace(',','.'))
        #diez=pd.Series(diez)  
        break 
    else:
        diez=None
        
# 21% y lo guardamos en veinte    
for i in range(detalle,max_index):
    j=separado[i]
    if j.find("21%")!=-1:
        veinte=j
        veinte=veinte.split()
        #veinte.pop(0)
        veinte[1]=float(veinte[1].replace(',','.'))
        veinte[2]=float(veinte[2].replace(',','.'))
        veinte[3]=float(veinte[3].replace(',','.'))
        #veinte=pd.Series(veinte)  
        break
    else:
        veinte=None
    
#"Porcentaje","Base","IVA","Total"

#cero.to_excel("Iva.xlsx",index=False)

#vale yo necesito que se cree una tabla con los ivas que encuentre, la estructura es la de abajo en el dict.
proveedor='MERCADONA S.A.'
tipo='FACTURA'
cif='A46103834'
ref='MERC'
flujo='SALIDA'

data = []

if cero is not None:
   dict={'FECHA':factura[3],'BANCO':'SI','TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':cero[1],'IVA':cero[2],'TIPO IVA':0,'TOTAL':cero[3]}
   data.append(dict)
if cuatro is not None:
   dict={'FECHA':factura[3],'BANCO':'SI','TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':cuatro[1],'IVA':cuatro[2],'TIPO IVA':4,'TOTAL':cuatro[3]}
   data.append(dict)
if cinco is not None:
   dict={'FECHA':factura[3],'BANCO':'SI','TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':cinco[1],'IVA':cinco[2],'TIPO IVA':5,'TOTAL':cinco[3]}
   data.append(dict)
if diez is not None:
   dict={'FECHA':factura[3],'BANCO':'SI','TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':diez[1],'IVA':diez[2],'TIPO IVA':10,'TOTAL':diez[3]}
   data.append(dict)
if veinte is not None:
   dict={'FECHA':factura[3],'BANCO':'SI','TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':veinte[1],'IVA':veinte[2],'TIPO IVA':21,'TOTAL':veinte[3]}
   data.append(dict) 

df = pd.DataFrame(data) #Convertimos a formato pandas


##COmprobamos si el archivo existe, si no existe lo creamos con los headers (Fecha,tipo,etc.)
check_file = os.path.isfile("MERCADONA.xlsx")
if check_file == False:
    df.to_excel("MERCADONA.xlsx",index=False)


#si ya existe solo queremos que se vaya añadiendo, sin el header
#para ello tenemos que saber a partir de donde tiene que escribir por eso leemos primero el archivo
#y sacamos las filas (row) y le sumamos 1 porque no cuenta el header del principio
else:
    df1 = pd.read_excel('MERCADONA.xlsx',sheet_name="Sheet1")
    
    #Buscamos si la factura ya esta en el excel
    df2 = []
    df2 = df1.loc[df1["FACTURA"]==factura[1]]
    
    if df2.empty is False:
        print(df2) #imprimimos para ver donde esta
        print(factura[1], "contabilizada" )
        sys.exit() #salimos del programa
    
    #la factura no esta en el excel por lo que obtenemos los rows para saber donde escribir    
    max_row=len(df1)+1
    #print(max_row)
    with pd.ExcelWriter("MERCADONA.xlsx",mode="a",if_sheet_exists="overlay") as writer:
        df.to_excel(writer,index=False,header=False,startrow=max_row) #index=None,columns=None




