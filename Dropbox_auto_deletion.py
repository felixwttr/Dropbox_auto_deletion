#!/usr/bin/env python3

import dropbox
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
from pathlib import Path

#Bitte anpassen

load_dotenv()
TOKEN = os.getenv('TOKEN')
age_of_files = 30
working_dir = '/Test/'


srcpath = Path(__file__).parent.absolute()
log_path = str(srcpath) + '/log.log'
print(log_path)
now = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')

def log(message):
    log_file = open(log_path, 'a')
    log_file.write(datetime.now().strftime('%d.%m.%Y') + ' ' + message + '\n')
    log_file.close()

#Verbindung zur Dropbox aufbauen
dbx = dropbox.Dropbox(TOKEN)

# Inhalt des Working Directorys auslesen
content_to_return = []
folder_content = dbx.files_list_folder(working_dir)
dir_content = folder_content.entries
while folder_content.has_more:
    cursor = folder_content.cursor
    folder_content = dropbox.dropbox.Dropbox.files_list_folder_continue(cursor)
    dir_content += folder_content.entries

dir_content = folder_content.entries
for fobj in dir_content:
        if isinstance(fobj, dropbox.files.FileMetadata):
            content_to_return.append(fobj.name)
        else:
            print('Datei konnte nicht der Liste der Dateien hinzugefügt werden')

# Prüfen ob Datei älter als age_of_file Tage alt ist, falls ja löschen, falls nein nichts tun
for file in content_to_return:
    metainfo = dbx.files_get_metadata(working_dir + file).client_modified
    created = datetime.strptime(str(metainfo), '%Y-%m-%d %H:%M:%S')
    delta = (now - created).days
    if delta >= age_of_files:
        dbx.files_delete(working_dir + file)
        print('Die Datei ' + str(file) + ' wurde gelöscht!')
        log('Die Datei ' + str(file) + ' wurde gelöscht!')
    else:
        print('Die Datei ' + str(file) + ' ist noch keine ' + str(age_of_files) + ' Tage alt.')
        log('Die Datei ' + str(file) + ' ist noch keine ' + str(age_of_files) + ' Tage alt.')


