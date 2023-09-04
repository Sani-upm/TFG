#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 19:07:50 2023

@author: sani
"""

from __future__ import print_function

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import email
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']

def GetAttachments(service, user_id, msg_id, download_path="./TICKETS_MERCADONA_UNREAD/"):
       """Get and store attachment from Message with given id.

       Args:
       service: Authorized Gmail API service instance.
       user_id: User's email address. The special value "me"
       can be used to indicate the authenticated user.
       msg_id: ID of Message containing attachment.
       download_path: download_path which is added to the attachment filename on saving
       """
       try:
           message = service.users().messages().get(userId=user_id, id=msg_id).execute()

           for part in message['payload'].get('parts', ''):
               if part['filename']:
                   if 'data' in part['body']:
                       data=part['body']['data']
                   else:
                       att_id=part['body']['attachmentId']
                       att=service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
                       data=att['data']
                       
           file_data = base64.urlsafe_b64decode(data.encode('ASCII'))
           path = download_path+part['filename']

           with open(path, 'wb') as f:
                f.write(file_data)
       except HttpError as error:
         # TODO(developer) - Handle errors from gmail API.
         print(f'An error occurred in GetAttachments function: {error}')  


def GetMessage(service, user_id,msg_id):
    try:
        message = service.users().messages().get(userId=user_id,id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        msg_str = email.message_from_bytes(msg_raw)
        content_types = msg_str.get_content_maintype()
        
        if content_types == 'multipart':
            #part 1 is plain text part 2 is HTML
                part1, part2 = msg_str.get_payload()
                print("This is the message body: \n")
                print(part1.get_payload())
                return part1.get_payload()
        else:
            return msg_str.get_payload()
    except HttpError as error:
         # TODO(developer) - Handle errors from gmail API.
         print(f'An error occurred in GetMessage funstion: {error}')       
            

def SearchMessages(service, user_id, search_string):
    try:
        search_id = service.users().messages().list(userId=user_id, q=search_string).execute()
        number_results = search_id['resultSizeEstimate']
        
        
        final_list=[]
        if number_results>0:
            message_ids = search_id['messages']
            
            for ids in message_ids:
                final_list.append(ids['id'])
            return final_list
        else:
            print('There were 0 results for that search string, returning an empty string')
            return ""
        
        
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred in SearchMessages function: {error}')

"Este es el servicio que se encarga de acceder al email y autentificarse, debe estar en el main si o si. Esta copiado tal cual de google.documents"
def get_service():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        #print('Labels:')
        #for label in labels:
        #   print(label['name'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    return service

if __name__ == '__main__':
  
  "Este programa es espeficicamente para descargar los pdf de los tickets de Mercadona, por ahora el el email al que se accede"
  "para descargar los tickets no esta asociado para realmente al sistema de Mercadona, eso se hara una vez el sistema completo funcione"
  "ya que no es un paso imprescindible"    
   
    
  msg_unread = {'removeLabelIds' : ['UNREAD']}  
  path='./TICKETS_MERCADONA_UNREAD/'  
  user_id = 'me' 
  search_string = 'is:unread from:Sani Mitkov' #"Una vez que se asocie este correo a MERCADONA, bastara con cambiar el from: para que funicone correctamente"
  
  service=get_service()
  "Obtenemos todos los mails no leidos que provienen de Sani, y almacenamos sus id en un vector"
  msg_list=SearchMessages(service,user_id, search_string)
  
  for i in msg_list:
      GetAttachments(service, user_id, i, download_path=path)
      """Una vez leido el mensaje y descargado el pdf, cambiamos la etiqueta
      en el Gmail a UNREAD para que no lo vuelva a leer"""
      service.users().messages().modify(userId=user_id,id=i,body=msg_unread).execute()
