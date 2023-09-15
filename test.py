import logging
from ripe_client import RIPEClient


#Configuração de LOGGING
logging.basicConfig(
    filename='ripe.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


client = RIPEClient(cacheLocation='./cache/ripe', logging=logging)

#client.download_update_file(2023, 9, 14, 10,50)

#client.download_updates_interval_files(2023, 9, 14, 10,50, 2023, 9, 14, 11,4 )

client.download_updates_interval_files(2023, 9, 14, 10,50, 2023, 9, 14, 12,4 )
