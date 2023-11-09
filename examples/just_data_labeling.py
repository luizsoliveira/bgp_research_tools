import sys
import os
import logging
from datetime import datetime

# append a new directory to sys.path

sys.path.append(os.getcwd())

from src.data_labeling.anomalous_and_regular_data_labeling import AnomalousAndRegularDataLabeling


#Configuração de LOGGING
logging.basicConfig(
    filename=f"./log/example_just_data_labeling.log",
    filemode='w',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


dataset_path = './cache/DATASET.tmp'
dataset_path_out = './cache/DATASET.csv'

data_labeler = AnomalousAndRegularDataLabeling(logging=logging)

anomalous_start = datetime(2003, 1, 25, 19, 0)
anomalous_end = datetime(2003, 1, 26, 1, 5)

dataset = data_labeler.new_dataset_with_labels(dataset_path, dataset_path_out, anomalous_start, anomalous_end)



