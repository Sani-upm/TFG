#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 11:22:20 2025

@author: sani
"""

import glob
import pandas as pd
from pypdf import PdfReader
import os
import shutil
import logging
import re
from datetime import datetime

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_iva_data(lines):
    iva_data = []
    found_iva = False
    collected_lines = []

    for line in lines:
        if "DETALLE (€)" in line:
            found_iva = True
            continue
        if found_iva:
            if "%" in line:
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

def process_mercadona_invoice_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        logging.info(f"Procesando archivo: {file_path} con {len(reader.pages)} páginas.")

        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue
            if "DETALLE (€)" in text:
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

def write_to_excel(data, BANCO, filename="facturas.xlsx"):
    columnas = [
        "FECHA", "BANCO", "TIPO", "FACTURA", "PROVEEDOR", "CIF", "REFERENCIA",
        "FLUJO", "BASE", "IVA", "TIPO IVA", "INTRA", "TOTAL", "TOTAL FACTURA"
    ]

    try:
        df_existente = pd.read_excel(filename)
    except FileNotFoundError:
        df_existente = pd.DataFrame(columns=columnas)

    factura_str = str(data.get("Factura", "")).strip()
    if not df_existente.empty and factura_str in df_existente["FACTURA"].astype(str).str.strip().values:
        logging.info(f"La factura {factura_str} ya existe en {filename}, no se agregará.\n")
        return "DUPLICADO"

    iva_items = data.get("IVA", [])
    if not iva_items:
        logging.warning(f"No hay datos de IVA para la factura {factura_str}. No se agregará.")
        return "ERROR"

    new_rows = [
        {
            "FECHA": data.get("Fecha"),
            "BANCO": BANCO,
            "TIPO": "FACTURA",
            "FACTURA": factura_str,
            "PROVEEDOR": "MERCADONA S.A.",
            "CIF": "A46103834",
            "REFERENCIA": "MERC",
            "FLUJO": "SALIDA",
            "BASE": iva.get("Base"),
            "IVA": iva.get("IVA"),
            "TIPO IVA": iva.get("Tipo IVA"),
            "INTRA": None,
            "TOTAL": iva.get("Total"),
            "TOTAL FACTURA": data.get("Total") if i == 0 else None
        }
        for i, iva in enumerate(iva_items)
    ]

    df_nuevo = pd.DataFrame(new_rows)
    df_nuevo.dropna(axis=1, how='all', inplace=True)
    df_existente.dropna(how='all', inplace=True)

    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True) if not df_existente.empty else df_nuevo
    df_final.to_excel(filename, index=False)
    logging.info(f"Datos escritos en {filename}\n")
    return "OK"

def procesar_pdfs_en_carpeta(carpeta, banco_flag, log_summary, log_files):
    pdf_files = glob.glob(os.path.join(carpeta, '*.pdf'))
    logging.info(f"Se encontraron {len(pdf_files)} archivos PDF en {carpeta}.")

    carpetas_destino = {
        "OK": "FACTURAS_MERCADONA_PROCESADAS",
        "DUPLICADO": "FACTURAS_MERCADONA_DUPLICADAS",
        "ERROR": "FACTURA_MERCADONA_ERROR"
    }

    for path in carpetas_destino.values():
        os.makedirs(path, exist_ok=True)

    for pdf_file in pdf_files:
        resultado = "ERROR"
        nombre_archivo = os.path.basename(pdf_file)
        total_factura = None

        try:
            extracted_data = process_mercadona_invoice_pdf(pdf_file)
            if extracted_data:
                resultado = write_to_excel(extracted_data, banco_flag)
                if resultado == "OK":
                    total_factura = extracted_data.get("Total")
        except Exception as e:
            logging.error(f"Excepción al procesar {pdf_file}: {e}")
            resultado = "ERROR"

        log_summary[resultado] += 1

        if resultado == "OK":
            detalle = f"{nombre_archivo} (Banco {banco_flag}) → Total: {total_factura:.2f} €"
        else:
            detalle = nombre_archivo

        log_files[resultado].append(detalle)

        destino = os.path.join(carpetas_destino.get(resultado, "FACTURA_MERCADONA_ERROR"), nombre_archivo)
        try:
            shutil.move(pdf_file, destino)
            logging.info(f"Archivo movido a: {destino}")
        except Exception as e:
            logging.error(f"No se pudo mover el archivo {pdf_file}: {e}")

def main():
    log_summary = {"OK": 0, "DUPLICADO": 0, "ERROR": 0}
    log_files = {"OK": [], "DUPLICADO": [], "ERROR": []}

    procesar_pdfs_en_carpeta('MERCADONA_BANCO_SI', "SI", log_summary, log_files)
    procesar_pdfs_en_carpeta('MERCADONA_BANCO_NO', "NO", log_summary, log_files)

    log_dir = "LOGGER_PROCESAMIENTO_FACTURAS_EN_EXCEL"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(log_dir, f"log_facturas_{timestamp}.txt")

    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write("RESUMEN DE LA EJECUCIÓN\n")
        log_file.write("=========================\n")
        log_file.write(f"Facturas procesadas correctamente: {log_summary['OK']}\n")
        log_file.write(f"Facturas duplicadas: {log_summary['DUPLICADO']}\n")
        log_file.write(f"Errores durante el procesamiento: {log_summary['ERROR']}\n\n")

        log_file.write("ARCHIVOS PROCESADOS POR CATEGORÍA\n")
        log_file.write("==================================\n\n")

        for categoria, descripcion in [
            ("OK", "✅ Facturas añadidas al Excel:"),
            ("DUPLICADO", "🔁 Facturas duplicadas:"),
            ("ERROR", "❌ Facturas con error:")
        ]:
            log_file.write(f"{descripcion}\n")
            if log_files[categoria]:
                for archivo in log_files[categoria]:
                    log_file.write(f" - {archivo}\n")
            else:
                log_file.write(" (ninguna)\n")
            log_file.write("\n")

    print("\n\n📋 RESUMEN FINAL DE LA EJECUCIÓN")
    print("=================================")
    print(f"✅ Facturas procesadas correctamente: {log_summary['OK']}")
    print(f"🔁 Facturas duplicadas: {log_summary['DUPLICADO']}")
    print(f"❌ Facturas con error: {log_summary['ERROR']}\n")

    for categoria, descripcion in [
        ("OK", "✅ Añadidas"),
        ("DUPLICADO", "🔁 Duplicadas"),
        ("ERROR", "❌ Con error")
    ]:
        print(f"{descripcion}:")
        if log_files[categoria]:
            for archivo in log_files[categoria]:
                print(f" - {archivo}")
        else:
            print(" (ninguna)")
        print()

    print(f"📄 Log guardado en: {log_file_path}")

if __name__ == "__main__":
    main()

