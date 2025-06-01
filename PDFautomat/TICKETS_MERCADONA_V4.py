#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 12:39:55 2025

@author: sani
"""

import glob
import pandas as pd
from pypdf import PdfReader
import os
import logging
import re
import shutil
import sys
from datetime import datetime

# Cargar tarjetas válidas
tarjetas_validas_path = "tarjetas_validas.txt"
tarjetas_validas = set()

if os.path.exists(tarjetas_validas_path):
    with open(tarjetas_validas_path, 'r', encoding='utf-8') as f:
        tarjetas_validas = set(line.strip() for line in f if line.strip())
else:
    logging.warning(f"No se encontró el archivo {tarjetas_validas_path}. Se asumirá 'Banco NO' por defecto.")

def es_tarjeta_valida(ultimos4):
    return str(ultimos4) in tarjetas_validas

# Configuración de logging
log_dir = "LOGGER_LECTURA-ESCRITURA_TICKETS"
os.makedirs(log_dir, exist_ok=True)
log_filename = os.path.join(log_dir, f"log_lectura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename, encoding='utf-8')
    ]
)

def extract_ticket_data(pdf_path):
    """Extrae datos clave de un ticket de Mercadona en PDF."""
    try:
        reader = PdfReader(pdf_path)
        if not reader.pages:
            logging.warning(f"El archivo PDF {pdf_path} no contiene páginas.")
            return None

        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

        if not text.strip():
            logging.warning(f"El archivo PDF {pdf_path} no contiene texto extraíble.")
            return None

        data = {
            "Fecha": None,
            "Tienda": None,
            "Caja": None,
            "Ticket": None,
            "Total": None,
            "Tarjeta": None,
            "Procesado": "",
            "Comentario": ""
        }

        # Fecha
        fecha_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
        if fecha_match:
            data["Fecha"] = fecha_match.group()

        # Factura Simplificada
        factura_match = re.search(r'FACTURA SIMPLIFICADA:\s*(\d{4})-(\d{3})-(\d+)', text)
        if factura_match:
            data["Tienda"] = int(factura_match.group(1))
            data["Caja"] = int(factura_match.group(2))
            data["Ticket"] = int(factura_match.group(3))

        # Total pagado
        total_match = re.search(r'TOTAL \(\u20ac\)\s*([\d,.]+)', text)
        if total_match:
            data["Total"] = float(total_match.group(1).replace(',', '.'))

        # Últimos 4 dígitos de la tarjeta
        tarjeta_match = re.search(r'TARJ\.?\.?\s*BANCARIA.*?(\d{4})', text)
        if tarjeta_match:
            data["Tarjeta"] = int(tarjeta_match.group(1))

        if data["Fecha"] and data["Tienda"] and data["Caja"] and data["Ticket"] and data["Total"]:
            return data
        else:
            logging.warning(f"Datos incompletos en {pdf_path}: {data}")
            return None

    except Exception as e:
        logging.error(f"Error procesando {pdf_path}: {e}")
        return None

def process_tickets(folder_path, processed_folder, excel_path):
    """Procesa todos los tickets en una carpeta y actualiza un Excel evitando duplicados."""
    if not os.path.exists(folder_path):
        logging.error(f"Carpeta de entrada no encontrada: {folder_path}")
        sys.exit(1)

    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    error_folder = os.path.join(folder_path, "..", "TICKETS_MERCADONA_ERROR")
    os.makedirs(error_folder, exist_ok=True)

    if os.path.exists(excel_path):
        df_existente = pd.read_excel(excel_path, dtype={"Tienda": int, "Caja": int, "Ticket": int, "Tarjeta": int, "Procesado": str, "Comentario": str})
    else:
        df_existente = pd.DataFrame(columns=["Fecha", "Tienda", "Caja", "Ticket", "Total", "Tarjeta", "Procesado", "Comentario"])

    nuevos_datos = []
    procesados_ok = []
    procesados_error = []

    for pdf_file in pdf_files:
        logging.info(f"Procesando {pdf_file}")
        ticket_data = extract_ticket_data(pdf_file)
        if ticket_data:
            existe = (
                (df_existente['Fecha'] == ticket_data['Fecha']) &
                (df_existente['Tienda'] == ticket_data['Tienda']) &
                (df_existente['Caja'] == ticket_data['Caja']) &
                (df_existente['Ticket'] == ticket_data['Ticket'])
            ).any()

            if existe:
                logging.info(f"Ticket ya existente: {pdf_file}")
            else:
                nuevos_datos.append(ticket_data)

            destino = os.path.join(processed_folder, os.path.basename(pdf_file))
            os.makedirs(processed_folder, exist_ok=True)
            shutil.move(pdf_file, destino)

            # Banco SI/NO
            estado_banco = "Banco NO"
            if ticket_data.get("Tarjeta") is not None and es_tarjeta_valida(ticket_data["Tarjeta"]):
                estado_banco = "Banco SI"

            logging.info(f"Movido a procesados: {os.path.basename(pdf_file)} | TOTAL: {ticket_data['Total']} € | {estado_banco}")
            procesados_ok.append(os.path.basename(pdf_file))
        else:
            destino = os.path.join(error_folder, os.path.basename(pdf_file))
            shutil.move(pdf_file, destino)
            logging.warning(f"Movido a errores: {os.path.basename(pdf_file)}")
            procesados_error.append(os.path.basename(pdf_file))

    if nuevos_datos:
        df_nuevos = pd.DataFrame(nuevos_datos)
        for col in ["Procesado", "Comentario"]:
            if col not in df_nuevos.columns:
                df_nuevos[col] = ""

        df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        df_final = df_final[["Fecha", "Tienda", "Caja", "Ticket", "Total", "Tarjeta", "Procesado", "Comentario"]]
        df_final.to_excel(excel_path, index=False)
        logging.info(f"Exportación completada: {len(nuevos_datos)} nuevos tickets añadidos.")
    else:
        logging.info("No hay nuevos tickets para agregar.")

    logging.info(f"Tickets procesados correctamente: {len(procesados_ok)}")
    logging.info(f"Tickets con error de lectura: {len(procesados_error)}")

if __name__ == "__main__":
    folder = "TICKETS_MERCADONA_UNREAD"
    processed_folder = "TICKETS_MERCADONA_READ"
    excel_path = "tickets_mercadona_2.xlsx"
    process_tickets(folder, processed_folder, excel_path)
