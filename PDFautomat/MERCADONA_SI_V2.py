#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 20:06:42 2025

@author: sani
"""
# Incluimos las librerías que vamos a usar
import glob
import pandas as pd
from pypdf import PdfReader
import os.path
import sys
import logging
import re

# Configuración del registro de actividad
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para extraer datos de IVA de las facturas
def extract_iva_data(lines):
    """
    Procesa las líneas de una factura para extraer información sobre las bases imponibles,
    IVAs y totales.

    Args:
        lines (list): Líneas de texto extraídas del PDF de la factura.

    Returns:
        list: Una lista de diccionarios con los datos de IVA encontrados.
    """
    iva_data = []
    found_iva = False
    collected_lines = []
    
    for line in lines:
        if "DETALLE (€)" in line:
            found_iva = True  # Marcar que hemos encontrado las lineas de IVA despues de "DETALLE (€)"
            continue  # Pasar a la siguiente línea
        
        if found_iva:
            if re.search(r'\d+%.*', line):  # Buscar líneas con el símbolo %
                collected_lines.append(line)
            elif collected_lines:  # Si ya hemos recolectado líneas y encontramos otra sin %, terminamos
                break
    
    for line in collected_lines:
        try:
            parts = re.findall(r'(\d+)%\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)', line)
            if parts:
                for part in parts:
                    iva_data.append({
                        'Tipo IVA': int(part[0]),
                        'Base': -float(part[1].replace(',', '.')),
                        'IVA': float(part[2].replace(',', '.')),
                        'Total': float(part[3].replace(',', '.'))
                    })
        except ValueError as e:
            logging.warning(f"Error procesando la línea: {line}. Detalles: {e}")
    
    return iva_data


# Función para procesar un archivo PDF de facturas de Mercadona
def process_mercadona_invoice_pdf(file_path, search_text="DETALLE (€)"):
    try:
        reader = PdfReader(file_path)  # Intentamos leer el archivo PDF
        hojas = len(reader.pages)  # Obtenemos el número de hojas
        logging.info(f"Procesando archivo: {file_path} con {hojas} páginas.")

        for k in range(hojas):  # Iteramos las páginas para buscar el texto proporcionado
            try:
                page = reader.pages[k]
                todo = page.extract_text()  # Extraemos el texto de la página

                if todo.find(search_text) != -1:  # Si encontramos el texto
                    logging.info(f"Texto '{search_text}' encontrado en la página {k + 1} del archivo {file_path}.\n")

                    # Obtención de información básica de la factura
                    separated = todo.splitlines()  # Dividimos el texto en líneas
                    invoice_data = {
                        "Factura": None,
                        "Fecha": None,
                        "Total": None,
                        "IVA": []
                    }

                    for line in separated:
                        if "Nº Factura:" in line:
                            invoice_data["Factura"] = line.split("Nº Factura:")[1].split(" Fecha Factura:")[0].strip()
                        if "Fecha Factura:" in line:
                            invoice_data["Fecha"] = line.split("Fecha Factura:")[1].strip()
                        if "Total Factura" in line:
                            invoice_data["Total"] = line.split()[-1].strip()

                    invoice_data["IVA"] = extract_iva_data(separated)
                    
                    logging.info(f"Datos extraídos de la factura: \n{invoice_data}\n")
                    return invoice_data  # Devolvemos los datos extraídos

            except Exception as e:
                logging.warning(f"Error al procesar la página {k + 1} del archivo {file_path}: {e}")
                continue

        logging.warning(f"No se encontró '{search_text}' en el archivo {file_path}.")
        return None  # Si no se encuentra el texto

    except Exception as e:
        logging.error(f"Error al leer el archivo PDF {file_path}: {e}")
        return None

# Función para escribir los datos en un archivo Excel
def write_to_excel(data, filename="facturas.xlsx"):
    columnas = ["FECHA", "BANCO", "TIPO", "FACTURA", "PROVEEDOR", "CIF", "REFERENCIA", "FLUJO", "BASE", "IVA", "TIPO IVA", "INTRA", "TOTAL", "TOTAL FACTURA"]
    
    try:
        df_existente = pd.read_excel(filename)
        if data["Factura"] in df_existente["FACTURA"].values:
            logging.info(f"La factura {data['Factura']} ya existe en {filename}, no se agregará.")
            return
    except FileNotFoundError:
        df_existente = pd.DataFrame(columns=columnas)
    
    new_rows = []
    for index, iva in enumerate(data["IVA"]):
        new_rows.append({
            "FECHA": data["Fecha"],
            "BANCO": "SI",
            "TIPO": "FACTURA",
            "FACTURA": data["Factura"],
            "PROVEEDOR": "MERCADONA S.A.",
            "CIF": "A46103834",
            "REFERENCIA": "MERC",
            "FLUJO": "SALIDA",
            "BASE": iva["Base"],
            "IVA": iva["IVA"],
            "TIPO IVA": iva["Tipo IVA"],
            "INTRA": None,
            "TOTAL": iva["Total"],
            "TOTAL FACTURA": data["Total"] if index == 0 else None
        })
    df_nuevo = pd.DataFrame(new_rows)
    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
    df_final.to_excel(filename, index=False)
    logging.info(f"Datos escritos en {filename}\n")

# Función principal para procesar todos los archivos PDF
def main():
    pdf_files = glob.glob('FACTURAS MERCADONA CONTABILIZADAS/*.pdf')  # Obtenemos todos los PDFs
    search_text = "DETALLE (€)"  # Texto a buscar, configurable

    for pdf_file in pdf_files:
        extracted_data = process_mercadona_invoice_pdf(pdf_file, search_text)
        if extracted_data:
            write_to_excel(extracted_data)

if __name__ == "__main__":
    main()



