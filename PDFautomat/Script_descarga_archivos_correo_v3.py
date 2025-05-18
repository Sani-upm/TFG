#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 18 21:41:29 2025

@author: sani
"""

from __future__ import print_function
import os
import base64
import logging
import email
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Registrar fecha y hora de inicio
start_time = datetime.now()

# Crear carpeta de logs si no existe
log_dir = "./LOGGER_de_extraccion_de_correos"
os.makedirs(log_dir, exist_ok=True)

# Configurar nombres de archivo de log individual y maestro
log_filename = os.path.join(log_dir, f"gmail_download_{start_time.strftime('%Y-%m-%d_%H-%M')}.log")
master_log_filename = os.path.join(log_dir, "master_logger.log")

# CONFIGURACIÓN DEL LOGGER EXPLÍCITA Y CORREGIDA
logging.getLogger().handlers.clear()  # Elimina duplicados del logger raíz

logger = logging.getLogger("gmail_logger")
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

master_handler = logging.FileHandler(master_log_filename)
master_handler.setFormatter(formatter)
logger.addHandler(master_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

SCOPES = ['https://mail.google.com/']

def GetAttachments(service, user_id, msg_id, download_path="./TICKETS_MERCADONA_UNREAD/"):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        for part in message['payload'].get('parts', ''):
            if part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id, id=att_id).execute()
                    data = att['data']

                file_data = base64.urlsafe_b64decode(data.encode('ASCII'))
                os.makedirs(download_path, exist_ok=True)
                path = os.path.join(download_path, part['filename'])

                with open(path, 'wb') as f:
                    f.write(file_data)

                logger.info(f"Archivo descargado: {part['filename']}")

    except HttpError as error:
        logger.error(f'Ocurrió un error en GetAttachments: {error}')  

def GetMessage(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        msg_str = email.message_from_bytes(msg_raw)
        content_types = msg_str.get_content_maintype()

        if content_types == 'multipart':
            part1, part2 = msg_str.get_payload()
            logger.info("Mensaje de texto: \n" + part1.get_payload())
            return part1.get_payload()
        else:
            return msg_str.get_payload()
    except HttpError as error:
        logger.error(f'Ocurrió un error en GetMessage: {error}')       

def SearchMessages(service, user_id, search_string):
    try:
        search_id = service.users().messages().list(userId=user_id, q=search_string).execute()
        number_results = search_id.get('resultSizeEstimate', 0)

        final_list = []
        if number_results > 0:
            message_ids = search_id['messages']
            for ids in message_ids:
                final_list.append(ids['id'])
            return final_list
        else:
            logger.info('No se encontraron mensajes no leídos con ese criterio.')
            return []
    except HttpError as error:
        logger.error(f'Ocurrió un error en SearchMessages: {error}')
        return []

def get_service():
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except ValueError as e:
            logger.warning("token.json corrupto. Eliminando...")
            os.remove('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        if creds and creds.expiry:
            logger.info(f"El token de credenciales es válido hasta: {creds.expiry.strftime('%Y-%m-%d %H:%M:%S')}")
            return service
    except HttpError as error:
        logger.error(f'Ocurrió un error al construir el servicio: {error}')
        return None

if __name__ == '__main__':
    logger.info(f"Script iniciado a las {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    msg_unread = {'removeLabelIds': ['UNREAD']}
    path = './TICKETS_MERCADONA_UNREAD/'
    user_id = 'me'
    search_string = 'is:unread from:Sani Mitkov'

    service = get_service()
    if service:
        msg_list = SearchMessages(service, user_id, search_string)
        total = 0
        for i in msg_list:
            GetAttachments(service, user_id, i, download_path=path)
            service.users().messages().modify(userId=user_id, id=i, body=msg_unread).execute()
            total += 1

        logger.info(f"Total de archivos descargados: {total}")

    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Script finalizado a las {end_time.strftime('%Y-%m-%d %H:%M:%S')} (Duración total: {duration})")

    # Cierre limpio del logger
    logging.shutdown()
