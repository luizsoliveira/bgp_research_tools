import logging
from datetime import datetime
import os
import sys
import shutil
import time

from src.data_download.clients.ripe_client import RIPEClient
from src.data_parse.python_mrt_parser import PythonMRTParser
from src.feature_extraction.feature_extraction import BGPFeatureExtraction

# thread = sys.argv[1]
thread = 128

#Configuração de LOGGING
logging.basicConfig(
    filename=f"ripe_stats_{thread}.log",
    filemode='w',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

cache_path = './cache'
if os.path.exists(cache_path):
    #shutil.rmtree(cache_path)
    shutil.rmtree(f"{cache_path}/ascii")
    shutil.rmtree(f"{cache_path}/features")

client = RIPEClient(cacheLocation=f"{cache_path}/mrt/ripe",
                    logging=logging,
                    debug=False,
                    max_concurrent_requests=64)

parser = PythonMRTParser(
                    logging=logging,
                    mrt_client=client,
                    debug=False,
                    max_concurrent_threads=16)

# Test
# datetime_start = datetime(2003, 1, 25, 15, 0)
# datetime_end = datetime(2003, 1, 26, 1, 5)

# Slammer
# Beginning of the event: 25.01.2003 at 5:31 GMT
# End of the event: 25.01.2003 at 19:59 GMT
datetime_start = datetime(2003, 1, 23, 0, 0)
datetime_end = datetime(2003, 1, 27, 23, 59)

#Westrock ransomware dates
# datetime_start = datetime(2021, 1, 21, 0, 0)
# datetime_end = datetime(2021, 1, 31, 23, 59)

start_download_time = time.perf_counter()
# Generator
files = client.download_updates_interval_files(datetime_start,
                                            datetime_end)
# The files are returned as they are being generated using yield
i = 0
t = 0
downloaded_files = []
for file in files:
    t+=1
    if file:
        # filename = os.path.basename(file)
        #print(f"File ready: {filename}")
        downloaded_files.append(file)
        i+=1

finish_download_time = time.perf_counter()
print(f"Were downloaded {i} of {t} files in {finish_download_time-start_download_time:.2f} seconds using {client.max_concurrent_requests} concurrent requests.")

start_parse_time = time.perf_counter()

# Generator
files_parsed = parser.parse_files(downloaded_files)

# The files are returned as they are being generated using yield
parse_i = 0
parse_t = 0
parsed_files = []
for file_parsed in files_parsed:
    parse_t+=1
    if file_parsed:
        # filename = os.path.basename(file)
        #print(f"File ready: {filename}")
        parsed_files.append(file_parsed)
        parse_i+=1

finish_parse_time = time.perf_counter()
print(f"Were parsed {parse_i} of {parse_t} files in {finish_parse_time-start_parse_time:.2f} seconds using {parser.max_concurrent_threads} threads.")


# Extracting Features
extractor = BGPFeatureExtraction(logging=logging,
                    debug=False,
                    max_concurrent_threads=12

)

start_extract_time = time.perf_counter()
files_extract = extractor.extract_features_from_files(parsed_files)

# The files are returned as they are being generated using yield
extract_i = 0
extract_t = 0
extracted_files = []
for file_extract in files_extract:
    extract_t+=1
    if file_extract:
        # filename = os.path.basename(file)
        #print(f"File ready: {filename}")
        extracted_files.append(file_extract)
        extract_i+=1

finish_extract_time = time.perf_counter()
print(f"Were extracted {extract_i} of {extract_t} files in {finish_extract_time-start_extract_time:.2f} seconds using {extractor.max_concurrent_threads} threads.")


# file_result = open("sequential.txt", "+a")
# file_result.write(f"westrock; download; {i}/{t}; {thread}; {finish_download_time - start_download_time}; parse; {parse_i}/{parse_t}; {thread}; {finish_parse_time - start_parse_time}\n")
# file_result.close()
#print(f"Were downloaded {i} of {t} files.")