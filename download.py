import ftplib
import os
from hashlib import md5

import xmltodict
from io import BytesIO
from zipfile import ZipFile

HOSTNAME = "ftp.zakupki.gov.ru"
USERNAME = "free"
PASSWORD = "free"
SUBJECTS = ['kraj', 'Resp', 'obl', 'AO', 'Moskva', 'ERUZ']

DIR = '/fcs_regions/Astrakhanskaja_obl/notifications'
region = ''
for i in DIR.split('/'):
    for j in SUBJECTS:
        if i.endswith(j):
            region = i
print(region)

ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)

ftp_server.encoding = "utf-8"

files = ftp_server.nlst(DIR)
for filename in files:
    if not filename.endswith('.zip'):
        continue
    with open('buffer.zip', 'wb') as file:
        ftp_server.retrbinary(F'RETR {filename}', file.write)

    with open('buffer.zip', 'rb') as file:
        zipfile = ZipFile(BytesIO(file.read()))

        for name in zipfile.namelist():
            xml = ''
            for line in zipfile.open(name).readlines():
                xml += line.decode('utf-8')
            json = xmltodict.parse(xml.strip())
            # for key in json['ns2:export']:
            #     if str(key).startswith('ns2:fcsNotification'):
            #         json = json['ns2:export'].pop(key)
            #         break
            json['md5'] = md5(xml.encode('utf-8')).hexdigest()
            json['region'] = region
            json['zipName'] = filename.split('/')[-1]
            json['xmlName'] = name
            print(json)

    os.remove('buffer.zip')
    break


ftp_server.quit()
