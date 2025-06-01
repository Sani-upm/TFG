#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 9:59:03 2025

@author: sani
"""

import glob
import pandas as pd
from pypdf import PdfReader
import os
import logging
import re

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para extraer datos de IVA
def extract_iva_data(lines):
    iva_data = []
    found_iva = False
    collected_lines = []

    for line in lines:
        if "DETALLE (€)" in line:
            found_iva = True
            continue
        
        if found_iva:
            if "%" in line:  # Simplificación de la búsqueda de líneas de IVA
                collected_lines.append(line)
            elif collected_lines: 
                break
    
    for line in collected_lines:
        try:
            matches = re.findall(r'(\d+)%\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)', line)
            for match in matches:
                iva_data.append({
                    'Tipo IVA': int(match[0]),
                    'Base': -float(match[1].replace(',', '.')),
                    'IVA': float(match[2].replace(',', '.')),
                    'Total': float(match[3].replace(',', '.'))
                })
        except ValueError as e:
            logging.warning(f"Error procesando la línea: {line}. Detalles: {e}")
    
    return iva_data

# Función para extraer datos de factura
def extract_invoice_data(lines):
    invoice_data = {
        "Factura": None,
        "Fecha": None,
        "Total": None,
        "IVA": []
    }

    for line in lines:
        factura_match = re.search(r"Nº Factura:\s*(\S+)", line)
        fecha_match = re.search(r"Fecha Factura:\s*(\d{2}/\d{2}/\d{4})", line)
        total_match = re.search(r"Total Factura\s+([\d,.]+)", line)

        if factura_match:
            invoice_data["Factura"] = factura_match.group(1)
        if fecha_match:
            invoice_data["Fecha"] = fecha_match.group(1)
        if total_match:
            invoice_data["Total"] = float(total_match.group(1).replace(",", "."))

    return invoice_data

# Función para procesar el PDF
def process_mercadona_invoice_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        logging.info(f"Procesando archivo: {file_path} con {len(reader.pages)} páginas.")

        for page in reader.pages:
            text = page.extract_text()
            if "DETALLE (€)" in text:
                logging.info(f"Texto 'DETALLE (€)' encontrado en {file_path}.\n")
                lines = text.splitlines()
                invoice_data = extract_invoice_data(lines)
                invoice_data["IVA"] = extract_iva_data(lines)
                logging.info(f"Datos extraídos: \n{invoice_data}\n")
                return invoice_data
        
        logging.warning(f"No se encontró 'DETALLE (€)' en {file_path}.")
        return None

    except Exception as e:
        logging.error(f"Error al leer el archivo PDF {file_path}: {e}")
        return None

# Función para escribir en Excel
def write_to_excel(data,BANCO,filename="facturas.xlsx"):
    
    columnas = ["FECHA", "BANCO", "TIPO", "FACTURA", "PROVEEDOR", "CIF", "REFERENCIA", 
                "FLUJO", "BASE", "IVA", "TIPO IVA", "INTRA", "TOTAL", "TOTAL FACTURA"]

    try:
        df_existente = pd.read_excel(filename)
    except FileNotFoundError:
        df_existente = pd.DataFrame(columns=columnas)

    if not df_existente.empty and str(data["Factura"]).strip() in df_existente["FACTURA"].astype(str).str.strip().values:
        logging.info(f"La factura {data['Factura']} ya existe en {filename}, no se agregará.\n")
        return
    
    new_rows = [
        {
            "FECHA": data["Fecha"],
            "BANCO": BANCO,
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
            "TOTAL FACTURA": data["Total"] if i == 0 else None
        }
        for i, iva in enumerate(data["IVA"])
    ]

    df_nuevo = pd.DataFrame(new_rows)
    if not df_nuevo.empty:
        df_nuevo = df_nuevo.dropna(axis=1, how='all')  # Elimina columnas completamente vacías
        df_existente = df_existente.dropna(how='all')  # Asegura que df_existente no tenga filas completamente vacías
    
        # Si df_existente está vacío, usa solo df_nuevo para evitar FutureWarning
    if df_existente.empty:
        df_final = df_nuevo
    else:
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
    
    df_final.to_excel(filename, index=False)
    logging.info(f"Datos escritos en {filename}\n")

# Función principal
def main():
    
    #Se recorre la carpeta de BANCO SI
    pdf_files = glob.glob('MERCADONA_BANCO_SI/*.pdf')
    logging.info(f"Se encontraron {len(pdf_files)} archivos PDF.")

    try:
        df_existente = pd.read_excel("facturas.xlsx")
    except FileNotFoundError:
        df_existente = pd.DataFrame(columns=["FACTURA"])

    for pdf_file in pdf_files:
        extracted_data = process_mercadona_invoice_pdf(pdf_file)
        if extracted_data:
            write_to_excel(extracted_data, "SI")
            
    #Se recorre la carpeta de BANCO NO        
    pdf_files = glob.glob('MERCADONA_BANCO_NO/*.pdf')
    logging.info(f"Se encontraron {len(pdf_files)} archivos PDF.")

    try:
        df_existente = pd.read_excel("facturas.xlsx")
    except FileNotFoundError:
        df_existente = pd.DataFrame(columns=["FACTURA"])

    for pdf_file in pdf_files:
        extracted_data = process_mercadona_invoice_pdf(pdf_file)
        if extracted_data:
            write_to_excel(extracted_data, "NO")

if __name__ == "__main__":
    main()