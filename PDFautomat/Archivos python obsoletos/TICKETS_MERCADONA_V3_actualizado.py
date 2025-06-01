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

def extraer_pago_tarjeta(texto: str) -> float | None:
    """
    Extrae el importe pagado con tarjeta bancaria desde el texto de un ticket,
    soportando diferentes formas de expresión como:
    - TARJETA BANCARIA 81,01
    - TARGETA BANCÀRIA 50,23
    - TARJ. BANCARIA: **** **** **** 8305
    """
    patron = r'(TARJ[\.ETA]*\s+BANC[AÀ]RIA)[\s:]*([\d,.]+)'
    coincidencia = re.search(patron, texto, re.IGNORECASE)

    if coincidencia:
        importe_str = coincidencia.group(2).replace(',', '.')
        try:
            return float(importe_str)
        except ValueError:
            return None
    return None

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

        # Pago con tarjeta bancaria
        pago_tarjeta = extraer_pago_tarjeta(text)
        if pago_tarjeta:
            data["Tarjeta"] = int(pago_tarjeta)  # Solo si necesitas los últimos 4 dígitos, usa otro regex

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
        datos_ticket = extract_ticket_data(pdf_file)
        if datos_ticket:
            existe = (
                (df_existente["Tienda"] == datos_ticket["Tienda"]) &
                (df_existente["Caja"] == datos_ticket["Caja"]) &
                (df_existente["Ticket"] == datos_ticket["Ticket"])
            ).any()

            if not existe:
                nuevos_datos.append(datos_ticket)
                shutil.move(pdf_file, os.path.join(processed_folder, os.path.basename(pdf_file)))
                logging.info(f"Procesado y movido: {pdf_file}")
            else:
                logging.info(f"Ticket duplicado, ignorado: {pdf_file}")
        else:
            shutil.move(pdf_file, os.path.join(error_folder, os.path.basename(pdf_file)))
            logging.warning(f"Error al procesar, movido a errores: {pdf_file}")

    if nuevos_datos:
        df_nuevos = pd.DataFrame(nuevos_datos)
        df_total = pd.concat([df_existente, df_nuevos], ignore_index=True)
        df_total.to_excel(excel_path, index=False)
        logging.info(f"Excel actualizado: {excel_path}")
    else:
        logging.info("No hay nuevos datos para agregar.")