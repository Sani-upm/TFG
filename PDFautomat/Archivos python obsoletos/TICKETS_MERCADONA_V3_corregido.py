#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 17 18:55:25 2025

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

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            "Tarjeta": None
        }

        # Fecha
        fecha_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
        if fecha_match:
            data["Fecha"] = fecha_match.group()

        # Factura Simplificada: 3274-013-085994
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
        tarjeta_match = re.search(r'TARJ\. BANCARIA.*?(\d{4})', text)
        if tarjeta_match:
            data["Tarjeta"] = int(tarjeta_match.group(1))

        if all(data.values()):
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
        df_existente = pd.read_excel(excel_path, dtype={"Tienda": int, "Caja": int, "Ticket": int, "Tarjeta": int})
    else:
        df_existente = pd.DataFrame(columns=["Fecha", "Tienda", "Caja", "Ticket", "Total", "Tarjeta"])

    nuevos_datos = []

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
                logging.info(f"Ticket ya existe: {ticket_data}")
            else:
                nuevos_datos.append(ticket_data)

            # Mover archivo procesado
            os.makedirs(processed_folder, exist_ok=True)
            shutil.move(pdf_file, os.path.join(processed_folder, os.path.basename(pdf_file)))
        else:
            logging.warning(f"No se pudo extraer información válida de {pdf_file}. Moviendo a carpeta de errores.")
            shutil.move(pdf_file, os.path.join(error_folder, os.path.basename(pdf_file)))

    if nuevos_datos:
        df_nuevos = pd.DataFrame(nuevos_datos)
        df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        df_final = df_final[["Fecha", "Tienda", "Caja", "Ticket", "Total", "Tarjeta"]]
        df_final.to_excel(excel_path, index=False)
        logging.info("Exportación completada correctamente.")
    else:
        logging.info("No hay nuevos tickets para agregar.")

if __name__ == "__main__":
    folder = "TICKETS_MERCADONA_UNREAD"
    processed_folder = "TICKETS_MERCADONA_READ"
    excel_path = "tickets_mercadona_2.xlsx"
    process_tickets(folder, processed_folder, excel_path)
