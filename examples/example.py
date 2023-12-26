import logging
from src.data_download.clients.ripe_client import RIPEClient
from datetime import datetime
import os
import sys

#Configuração de LOGGING
logging.basicConfig(
    filename='ripe.log',
    filemode='w',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


#client = RIPEClient(cacheLocation='./cache/ripe', logging=logging)
#client = RIPEClient(cacheLocation='./cache/ripe', logging=False)

max = sys.argv[1]

client = RIPEClient(logging=logging,debug=True, max_concurrent_requests=max)
#Slammer attack dates

# datetime_start = datetime(2003, 1, 23, 0, 0)
# datetime_end = datetime(2003, 1, 23, 27, 59)

datetime_start = datetime(2003, 1, 23, 0, 0)
datetime_end = datetime(2003, 1, 27, 23, 59)


files = client.download_updates_interval_files(datetime_start,
                                               datetime_end)

# The files are returned as they are being generated using yield
i = 0
t = 0
for file in files:
    t+=1
    if file:
        filename = os.path.basename(file)
        print(f"File ready: {filename}")
        i+=1

print(f"Were downloaded {i} of {t} files.")