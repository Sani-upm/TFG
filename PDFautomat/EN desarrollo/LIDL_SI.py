#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 28 19:13:42 2023

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
globs = glob.iglob('LIDL_SI/**.pdf')

#iteramos y obtenemos el excel 
for a in globs:
    reader = PdfReader(a) # leemos el pdf y lo metemos en un objeto reader
    hojas=len(reader.pages)         #obtenemos el numero de hojas
    #page = reader.pages[hojas-1]   
    
    for k in range(hojas):                  #Vamos a iterar las hojas para buscar "DETALLE (€)"
        page = reader.pages[k]      
        todo=page.extract_text()            #extraemos la hoja
        if todo.find("Bruto Importe IVA Neto")!=-1:    #Buscamos detalle, si lo encuentra esa es la hoja si no que siga iterando
        
            break
        else:
            continue 
        
    separado=todo.splitlines()      #separamos todo en una lista de str
    max_index=len(separado)-1       #obtenemos el maximo indice
    total_factura=0                 #creamos variable que va a almacenar el total de la factura
#-------------------------------------------------------------------------------------------------------
# HASTA aqui igual que en Mercadona
#-------------------------------------------------------------------------------------------------------        
        
    # A estas alturas tenemos la hoja que tiene la informacion, que es aquella que enga el detalle del IVA, porque todas las hojas tienen 
    #en la cabecera Nº de factura fecha....
    
    parts=[]
    def visitor_body(text, cm, tm, font_dict, font_size):
        #y va de 0 a 900 mas o menos por lo que estoy viendo...
         
         if tm[4]>300 and tm[4]<500 and tm[5]>-200 and tm[5]<-140:   #con este visor obtengo el nº de factura
            if len(text) > 1:
                parts.append(text)
                  
         if tm[4]>0 and tm[4]<600 and tm[5]>-100 and tm[5]<-90:     # con este obtengo la fecha factura
            if len(text) > 1:
                parts.append(text)  
                   
    page.extract_text(visitor_text=visitor_body) # meto lo que he sacado del visor en parts
    
    # ahora sacamos el numero de factura que esta en la str 1 de parts
    # que pasa que el numero de factura lo lee muy mal y lo deja pegado a"Barcelona" pues buscmamos donde esta y vamos transformando hasta obtener la estructura
    # que teniamos en mercadona donde factura es una lista de 4 elementos
    for i in parts:
        if i.find("Barcelona")!=-1:
            factura =i
            factura=factura.split() 
            factura.pop(1)
        
            #for inter in range(len(factura[0])):
                #if factura[0][inter] == "B" or "a" or "r" or "c" or "e" or "l" or "o" or "n":
            factura[0] = factura[0].replace("Barcelona","") #factura se convierte de list a str, por eso en la siguiente desaparece el indice
            factura[0] = factura[0].replace("NIF","")
            # ya tengo el numero de factura que lo tengo como str.
    for i in parts:
        if i.find("Fecha Factura:")!=-1:
            aux =i
            aux = aux.split()
            aux[2]=aux[2].replace("-","/")
            aux[2]=aux[2].replace("Ene","01")
            aux[2]=aux[2].replace("Feb","02")
            aux[2]=aux[2].replace("Mar","03")
            aux[2]=aux[2].replace("Abr","04")
            aux[2]=aux[2].replace("May","05")
            aux[2]=aux[2].replace("Jun","06")
            aux[2]=aux[2].replace("Jul","07")
            aux[2]=aux[2].replace("Ago","08")
            aux[2]=aux[2].replace("Sep","09")
            aux[2]=aux[2].replace("Oct","10")
            aux[2]=aux[2].replace("Nov","11")
            aux[2]=aux[2].replace("Dic","12")
            factura.append(aux[2])
            
            aux[0]="Nº Factura:"
            aux[1]=factura[0]
            aux[2]="Fecha Factura:"
            aux.append(factura[1])
            
            factura=aux
            ##------------------------------------------------------------------------        
            '''' Obtenemos la siguiente estructura 
            ['Nº Factura:', 'A-V2023-00000698540', 'Fecha Factura:', '21/02/2023'] '''
            #------------------------------------------------------------------------ 
            
    #Buscamos dentro de la factura el DETALLE (€) de las bases y el iva
    for x in range (max_index):
         if separado[x].find("Bruto Importe IVA Neto")==0:
             detalle=x             # obtenemos el indice a partir del cual buscaremos el iva
             break
   
    #0% y lo guaramos en la variable cero
    for i in range(detalle,max_index):
        j=separado[i]
        if j.find("0,00")!=-1:
            cero=j
            if cero.find("Tipo IVA")==-1:
                cero=None
                continue
            cero=cero.split()
            
            cero[1]=float(cero[1].replace(',','.'))
            cero[2]=float(cero[2].replace(',','.'))
            if cero[2]!= 0.0:
                cero=None
                continue
            cero[3]=float(cero[3].replace(',','.'))
               
            total_factura+=cero[1]
            break
            
        else:
            cero=None  #Si no hay iva del 0% nos devuelve un none
    #------------------------------------------------------------------------      
    '''                                                0        1       2       3      4      5
            ''''                                      tipo    total    iva     base  TIPO    IVA '''
    '''obtenemos la siguiente estructura cuatro = [ '4,00', '6,58', '0,25', '6,33'] [Tipo] [IVA]   '''      
    #------------------------------------------------------------------------           
    # 4% y lo guaradmos en cuatro    
    for i in range(detalle,max_index):
        j=separado[i]
        if j.find("4,00")!=-1:
            cuatro=j
            if cuatro.find("Tipo IVA")==-1:
                cuatro=None
                continue
            cuatro=cuatro.split()
            
            cuatro[1]=float(cuatro[1].replace(',','.'))
            cuatro[2]=float(cuatro[2].replace(',','.'))
            cuatro[3]=float(cuatro[3].replace(',','.'))
            
            total_factura+=cuatro[1]
            break
        else:
            cuatro=None
    # 5% y lo guardamos en cinco    
    for i in range(detalle,max_index):
         j=separado[i]
         if j.find("5,00")!=-1:
             
             cinco=j
             if cinco.find("Tipo IVA")==-1:
                 cinco=None
                 continue
             cinco=cinco.split()
             
             cinco[1]=float(cinco[1].replace(',','.'))
             cinco[2]=float(cinco[2].replace(',','.'))
             cinco[3]=float(cinco[3].replace(',','.'))
             
             total_factura+=cinco[1]
             break
         else:
             cinco=None
             
             
    # 10% y lo guardamos en diez    
    for i in range(detalle,max_index):
         j=separado[i]
         if j.find("10,00")!=-1:
             diez=j
             if diez.find("Tipo IVA")==-1:
                 diez=None
                 continue
             diez=diez.split()
             
             diez[1]=float(diez[1].replace(',','.'))
             diez[2]=float(diez[2].replace(',','.'))
             diez[3]=float(diez[3].replace(',','.'))
             
             
             total_factura+=diez[1]
             break 
         else:
             diez=None
             
    # 21% y lo guardamos en veinte    
    for i in range(detalle,max_index):
         j=separado[i]
         if j.find("21,00")!=-1:
             veinte=j
             if veinte.find("Tipo IVA")==-1:
                 veinte=None
                 continue
             veinte=veinte.split()
             
             veinte[1]=float(veinte[1].replace(',','.'))
             veinte[2]=float(veinte[2].replace(',','.'))
             veinte[3]=float(veinte[3].replace(',','.'))
             
             total_factura+=veinte[1]
             break
         else:
             veinte=None        
    #vale yo necesito que se cree una tabla con los ivas que encuentre, la estructura es la de abajo en el dict.
    proveedor='LIDL SUPERMERCADOS S.A.U.'
    tipo='FACTURA'
    cif='A60195278'
    ref='LIDL'
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
    ARCHIVO = "LIDL.xlsx"

    ##COmprobamos si el archivo existe, si no existe lo creamos con los headers (Fecha,tipo,etc.)
    check_file = os.path.isfile(ARCHIVO)
    if check_file == False:
        df.to_excel(ARCHIVO,index=False)


    #si ya existe solo queremos que se vaya añadiendo, sin el header
    #para ello tenemos que saber a partir de donde tiene que escribir por eso leemos primero el archivo
    #y sacamos las filas (row) y le sumamos 1 porque no cuenta el header del principio
    else:
        df1 = pd.read_excel(ARCHIVO,sheet_name="Sheet1")
        #Cuando leeemos con pandas el excel, en el caso de las facturas de lidl, devuelve como int en nª de factura, y yo en el script tengo str
        #entonces si lo comparamos como se hace en la factura del mercadona str=int luego se piensa que esa factura no esta contabilizada y la mete,
        #por eso primero trasformo en el script factura[1] a int asi cuando me devuelva la lista de nºfactura del excel como int puede comparar
        nfactura=int(factura[1])
        
        #Buscamos si la factura ya esta en el excel
        df2 = []
        df2 = df1.loc[df1["FACTURA"]==nfactura]
        
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