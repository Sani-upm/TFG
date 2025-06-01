#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 20:02:53 2023

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
    
    for k in range(hojas):                  #Vamos a iterar las hojas para buscar "DETALLE (€)"
        page = reader.pages[k]      
        todo=page.extract_text()            #extraemos la hoja
        if todo.find("% IMP")!=-1:    #Buscamos detalle, si lo encuentra esa es la hoja si no que siga iterando
            break
        else:
            continue

    separado=todo.splitlines()      #separamos todo en una lista de str
    max_index=len(separado)-1       #obtenemos el maximo indice
    total_factura=0                 #creamos variable que va a almacenar el total de la factura
    
    # Obtenemos iformacion de la factura como el numero de factra y fecha y lo guardamos en una lista
    for i in separado:
        if i.find("Factura")!=-1:
            factura =i
            factura=factura.split()
            factura.pop(4)
            factura.pop(3)
            factura.pop(2)
            factura[0]="Nº Factura:"
            factura.append("Fecha Factura:")
            
    for i in separado:
        if i.find("Fecha de venta:")!=-1:
            aux=i
            aux=aux.split()
            factura.append(aux[10])
            
            ##------------------------------------------------------------------------        
            '''' Obtenemos la siguiente estructura 
            ['Nº Factura:', 'A-V2023-00000698540', 'Fecha Factura:', '21/02/2023'] '''
            #------------------------------------------------------------------------ 
      
    #Buscamos dentro de la factura el DETALLE (€) de las bases y el iva
    for x in range (max_index):
        if separado[x].find("Número de bultos:")==0:
            detalle=x             # obtenemos el indice a partir del cual buscaremos el iva
            break
    #0% y lo guaramos en la variable cero
    for i in range(detalle,max_index):
         j=separado[i]
         if j.find("0,00%")!=-1:
             
             cero=j
             cero=cero.split()
             
             cero[0]=float(cero[0].replace(',','.'))
             cero[3]=float(cero[3].replace(',','.'))
             cero[1]=cero[0]+cero[3]
             
             aux[0]=cero[2]
             aux[1]=cero[0]
             aux[2]=cero[3]
             aux[3]=cero[1]
             
             cero = aux
             
             if cero[2]!= 0.0:
                 cero=None
                 continue
             
                
             total_factura+=cero[3]
             break
             
         else:
             cero=None  #Si no hay iva del 0% nos devuelve un none
             #------------------------------------------------------------------------        
    ''''                                   tipo  base    iva   total '''
    '''obtenemos la siguiente estructura cero = [ '0%', '9,85', '0', '9,85'] '''      
            #------------------------------------------------------------------------   
             
    # 4% y lo guaradmos en cuatro    
    for i in range(detalle,max_index):
         j=separado[i]
         if j.find("4,00%")!=-1:
             cuatro=j
             cuatro=cuatro.split()
             aux=j
             aux=aux.split()
             
             cuatro[0]=float(cuatro[0].replace(',','.'))
             cuatro[3]=float(cuatro[3].replace(',','.'))
             cuatro[1]=cuatro[0]+cuatro[3]
             
             aux[0]=cuatro[2]
             aux[1]=cuatro[0]
             aux[2]=cuatro[3]
             aux[3]=cuatro[1]
             
             cinco = aux
             
             total_factura+=cuatro[3]
             break
         else:
             cuatro=None
             
             
     # 5% y lo guardamos en cinco    
    for i in range(detalle,max_index):
         j=separado[i]
         if j.find("5,00%")!=-1:
             cinco=j
             cinco=cinco.split()
             aux=j
             aux=aux.split()
             
             cinco[0]=float(cinco[0].replace(',','.'))
             cinco[3]=float(cinco[3].replace(',','.'))
             cinco[1]=cinco[0]+cinco[3]
             
             aux[0]=cinco[2]
             aux[1]=cinco[0]
             aux[2]=cinco[3]
             aux[3]=cinco[1]
             
             cinco = aux
             
             total_factura+=cinco[3]
             break
         else:
             cinco=None
             
             
     # 10% y lo guardamos en diez    
    for i in range(detalle,max_index):
         j=separado[i]
         if j.find("10,00%")!=-1:
             diez=j
             diez=diez.split()
             aux=j
             aux=aux.split()
             
             diez[0]=float(diez[0].replace(',','.'))
             diez[3]=float(diez[3].replace(',','.'))
             diez[1]=diez[0]+diez[3]
             
             aux[0]=diez[2]
             aux[1]=diez[0]
             aux[2]=diez[3]
             aux[3]=diez[1]
             
             diez = aux
             
             total_factura+=diez[3]
             break 
         else:
             diez=None
      
        
    # 21% y lo guardamos en veinte    
    for i in range(detalle,max_index):
        j=separado[i]
        if j.find("21,00%")!=-1:
              veinte=j
              veinte=veinte.split()
              aux=j
              aux=aux.split()
              
              veinte[0]=float(veinte[0].replace(',','.'))
              veinte[3]=float(veinte[3].replace(',','.'))
              veinte[1]=veinte[0]+veinte[3]
              
             
              aux[0]=veinte[2]
              aux[1]=veinte[0]
              aux[2]=veinte[3]
              aux[3]=veinte[1]
              
              veinte = aux
              total_factura+=veinte[3]
              break
        else:
              veinte=None    
              
    #"Porcentaje","Base","IVA","Total"

    #cero.to_excel("Iva.xlsx",index=False)

    #vale yo necesito que se cree una tabla con los ivas que encuentre, la estructura es la de abajo en el dict.
    proveedor='MAKRO DISTRIBUCION MAYORISTA, S.A.'
    tipo='FACTURA'
    cif='A28647451'
    ref='MAKRO'
    flujo='SALIDA'

    BASE=3
    IVA=2
    TOTAL=1
    
    BANCO="SI"

    data = []
    flag=0
    
    if cero is not None:
       dict={'FECHA':factura[3],'BANCO':BANCO,'TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':-cero[BASE],'IVA':cero[IVA],'TIPO IVA':0,'INTRA': None,'TOTAL':-cero[TOTAL], 'TOTAL FACT':-total_factura}
       data.append(dict)
       flag=1
       
    if cuatro is not None:
       if flag==0: 
           dict={'FECHA':factura[3],'BANCO':BANCO,'TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':-cuatro[BASE],'IVA':cuatro[IVA],'TIPO IVA':4,'INTRA': None,'TOTAL':-cuatro[TOTAL],'TOTAL FACT':-total_factura}
           data.append(dict)
           flag=1
       else:
           dict={'FECHA':factura[3],'BANCO':BANCO,'TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':-cuatro[BASE],'IVA':cuatro[IVA],'TIPO IVA':4,'INTRA': None,'TOTAL':-cuatro[TOTAL],'TOTAL FACT':None}
           data.append(dict)
       
    if cinco is not None:
        if flag==0:
            dict={'FECHA':factura[3],'BANCO':BANCO,'TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':-cinco[BASE],'IVA':cinco[IVA],'TIPO IVA':5,'INTRA': None,'TOTAL':-cinco[TOTAL], 'TOTAL FACT': -total_factura}
            data.append(dict)
            flag=1
        else:
            dict={'FECHA':factura[3],'BANCO':BANCO,'TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':-cinco[BASE],'IVA':cinco[IVA],'TIPO IVA':5,'INTRA': None,'TOTAL':-cinco[TOTAL], 'TOTAL FACT': None}
            data.append(dict)
       
    if diez is not None:
        if flag==0:
            dict={'FECHA':factura[3],'BANCO':BANCO,'TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':-diez[BASE],'IVA':diez[IVA],'TIPO IVA':10,'INTRA': None,'TOTAL':-diez[TOTAL], 'TOTAL FACT': -total_factura}
            data.append(dict)
            flag=1
        else:
            dict={'FECHA':factura[3],'BANCO':BANCO,'TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':-diez[BASE],'IVA':diez[IVA],'TIPO IVA':10,'INTRA': None,'TOTAL':-diez[TOTAL], 'TOTAL FACT': None}
            data.append(dict)
            
    if veinte is not None:
        if flag==0:
            dict={'FECHA':factura[3],'BANCO':BANCO,'TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':-veinte[BASE],'IVA':veinte[IVA],'TIPO IVA':21,'INTRA': None,'TOTAL':-veinte[TOTAL], 'TOTAL FACT':-total_factura}
            data.append(dict)
            flag=1
        else:
            dict={'FECHA':factura[3],'BANCO':BANCO,'TIPO':tipo,'FACTURA':factura[1],'PROVEEDOR':proveedor,'CIF':cif,'REFERENCIA':ref,'FLUJO':flujo,'BASE':-veinte[BASE],'IVA':veinte[IVA],'TIPO IVA':21,'INTRA': None,'TOTAL':-veinte[TOTAL], 'TOTAL FACT': None}
            data.append(dict)

    df = pd.DataFrame(data) #Convertimos a formato pandas
    ARCHIVO = "MAKRO.xlsx"

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
        df2 = df1.loc[df1["FACTURA"]==factura[1]]
        
        if df2.empty is False:
            print("\n")
            print(factura[1], "contabilizada" )
            print(df2)      #imprimimos para ver donde esta
            print("\n")
            continue        #si ya esta pues nada, pasamos a la siguiente factura
            
        
        #la factura no esta en el excel por lo que obtenemos los rows para saber donde escribir    
        max_row=len(df1)+1
        #print(max_row)
        with pd.ExcelWriter(ARCHIVO,mode="a",if_sheet_exists="overlay") as writer:
            df.to_excel(writer,index=False,header=False,startrow=max_row) #index=None,columns=None
                  
          