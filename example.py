import logging
from ripe_client import RIPEClient
from datetime import datetime

#Configuração de LOGGING
logging.basicConfig(
    filename='ripe.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


#client = RIPEClient(cacheLocation='./cache/ripe', logging=logging)
client = RIPEClient(cacheLocation='./cache/ripe', logging=False)


client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))
