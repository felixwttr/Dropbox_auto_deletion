#!/usr/bin/env python3
import dropbox
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
from pathlib import Path
import requests
import json

load_dotenv()

#Please configure for your needs

TOKEN = os.getenv('TOKEN')          # Update your DropBox TOKEN in the .env file
IFTTT_KEY = os.getenv('IFTTT_KEY')  # Update your IFTTT Webhook Key in the .env file
age_of_files = 30                   # at which age files should be deleted?
working_dir = '/Felix iPhone Scans/'              # which folder should be observed?
ifttt_integration = True            # do you wish to get an notification through IFTTT whenever a file gets deleted?
logging = True                      # do you want to have a log file with every action this skript does to your files?

# Don't touch these
srcpath = Path(__file__).parent.absolute()
log_path = str(srcpath) + '/log.log' # pwd of logfile
now = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S') # current timestamp

#log function
def log(message):
    log_file = open(log_path, 'a')
    log_file.write(datetime.now().strftime('%d.%m.%Y') + ' --- ' + message + '\n')
    log_file.close()

# establish connection to Dropbox
dbx = dropbox.Dropbox(TOKEN)

# Read files within working_directory
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

# Check whether file is old enough to be deleted
for file in content_to_return:
    metainfo = dbx.files_get_metadata(working_dir + file).client_modified
    created = datetime.strptime(str(metainfo), '%Y-%m-%d %H:%M:%S')
    delta = (now - created).days
    if delta >= age_of_files:
        dbx.files_delete(working_dir + file)
        print('DELETED: ' + str(file) + '!')
        if logging:
            log('DELETED:' + str(file) + '!')
        if ifttt_integration:
            url = "https://maker.ifttt.com/trigger/file_deleted/with/key/" + IFTTT_KEY
            data = {'value1': file, 'value2': '', 'value3': ''}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, data=json.dumps(data), headers=headers)
    else:
        print('SKIPPED: \"' + str(file) + '\"! Reason: Not older than ' + str(age_of_files) + ' days')
        if logging:
            log('SKIPPED: \"' + str(file) + '\"! Reason: Not older than ' + str(age_of_files) + ' days')


