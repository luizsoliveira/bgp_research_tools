import json
import os
import utils
from datetime import datetime
from math import floor, ceil
import json
import sys
import time
import logging
import shutil
import multiprocessing

number_of_cores = multiprocessing.cpu_count()

# lib_path = f"{os.path.dirname(__file__)}/../"
# print(lib_path)
# sys.path.append(lib_path)
# print(sys.path)

from data_download.clients.ripe_client import RIPEClient
from data_parse.python_mrt_parser import PythonMRTParser
from feature_extraction.feature_extraction import BGPFeatureExtraction
from data_aggregation.merge_files import merge_files
from data_labeling.anomalous_and_regular_data_labeling import AnomalousAndRegularDataLabeling


task_working_dir = os.getcwd()
print(f" 📂 Starting task on CWD: {task_working_dir}")

today = datetime.today()
print(f" 🕣 Starting time: {today}")

file = open('task.json')
task = json.load(file)

print(f" 🔑 Task key: {task['id']}")
print(f" ⚙️ Task parameters (before parsing):")
utils.print_task_parameters(task)

p = task['parameters']

date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

# Preparing the parameters
collection_site = p['collection_site']
ripe_ris_rrc = p['ripe_ris_rrc']

date_start = p['date_start']
date_end = p['date_end']

anomalous_date_start = p['anomalous_date_start']
anomalous_date_end = p['anomalous_date_end']

anomalous_time_start = p['anomalous_time_start']
anomalous_time_end = p['anomalous_time_end']

# data_partition_training = p['data_partition_training'] 
# data_partition_testing = p['data_partition_testing'] 
# rnn_length = p['rnn_length']

cache_path = '/opt/bgp_research' if p['cache'] == 'activated' else False
debug = True if p['debug'] == 'activated' else False

print('')

datetime_start = datetime.strptime(f"{date_start}T000000", "%Y%m%dT%H%M%S")
datetime_end = datetime.strptime(f"{date_end}T235959", "%Y%m%dT%H%M%S")

anomalous_datetime_start = datetime.strptime(f"{anomalous_date_start}T{anomalous_time_start}00", "%Y%m%dT%H%M%S")
anomalous_datetime_end = datetime.strptime(f"{anomalous_date_end}T{anomalous_time_end}59", "%Y%m%dT%H%M%S")

params = {
    'collection_site': collection_site,
    'ripe_ris_rrc': ripe_ris_rrc,
    'datetime_start': datetime_start,
    'datetime_end': datetime_end,
    'anomalous_datetime_start': anomalous_datetime_start,
    'anomalous_datetime_end': anomalous_datetime_end
}

print(f" ⚙️ Task parameters (after parsing):")
utils.print_generic_parameters(params)

print('')

#Configuração de LOGGING
logging.basicConfig(
    filename=f"bgpresearch.log",
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

if os.path.exists(cache_path):
    #shutil.rmtree(cache_path)
    ascii_path = f"{cache_path}/ascii"
    if os.path.exists(ascii_path): shutil.rmtree(ascii_path)
    features_path = f"{cache_path}/features"
    if os.path.exists(features_path): shutil.rmtree(features_path)

client = RIPEClient(cacheLocation=f"{cache_path}/mrt/ripe",
                    logging=logging,
                    debug=False,
                    max_concurrent_requests=64)

parser = PythonMRTParser(
                    logging=logging,
                    mrt_client=client,
                    debug=False,
                    max_concurrent_threads=number_of_cores)

start_download_time = time.perf_counter()
# Generator
files = client.download_updates_interval_files(datetime_start,
                                            datetime_end, int(ripe_ris_rrc))
# The files are returned as they are being generated using yield
i = 0
t = 0
downloaded_files = []
for file in files:
    t+=1
    if file:
        # filename = os.path.basename(file)
        #print(f"File ready: {filename}")
        print(f"File ready: {file}")
        downloaded_files.append(file)
        i+=1

print('')

finish_download_time = time.perf_counter()
print(f"Were downloaded (or obtained from cache) {i} of {t} files in {finish_download_time-start_download_time:.2f} seconds using {client.max_concurrent_requests} concurrent requests.")

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
                    max_concurrent_threads=number_of_cores
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

extracted_files.sort()

dataset_path_tmp = './DATASET.tmp'
dataset_path_with_labels = './DATASET.csv'

headerLine = "DATETIME HOUR MINUTE SECOND F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 F13 F14 F15 F16 F17 F18 F19 F20 F21 F22 F23 F24 F25 F26 F27 F28 F29 F30 F31 F32 F33 F34 F35 F36 F37"

merge_files(extracted_files, dataset_path_tmp, headerLine)

data_labeler = AnomalousAndRegularDataLabeling(logging=logging)

data_labeler.new_dataset_with_labels(dataset_path_tmp,dataset_path_with_labels, anomalous_datetime_start, anomalous_datetime_end)

os.remove(dataset_path_tmp)