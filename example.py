import logging
from ripe_client import RIPEClient
from datetime import datetime
import os
import sys

#Configuração de LOGGING
logging.basicConfig(
    filename='ripe.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


#client = RIPEClient(cacheLocation='./cache/ripe', logging=logging)
#client = RIPEClient(cacheLocation='./cache/ripe', logging=False)

max = sys.argv[1]

client = RIPEClient(debug=True, max_concurrent_requests=max)
#Slammer attack dates
files = client.download_updates_interval_files(datetime(2021, 1, 7, 0, 0),
                                               datetime(2021, 1, 9, 23, 59))



# The timestamps are returned as they are being generated using yield
i = 0
for file in files:
    filename = os.path.basename(file)
    print(f"File ready: {filename}")
    i+=1

print(f"Were downloaded {i} files.")