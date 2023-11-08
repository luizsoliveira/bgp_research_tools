import logging

from src.data_parse.python_mrt_parser import PythonMRTParser
from src.data_download.clients.ripe_client import RIPEClient

logging.basicConfig(
    filename=f"ripe_client.log",
    filemode='w',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


#client = RIPEClient(cacheLocation='./cache/ripe', logging=logging)
#client = RIPEClient(cacheLocation='./cache/ripe', logging=False)

client = RIPEClient(logging=logging,
                    debug=False,
                    max_concurrent_requests=128,
                    cacheLocation='./cache')

parser = PythonMRTParser(logging=logging,
                    mrt_client=client,
                         debug=False)

