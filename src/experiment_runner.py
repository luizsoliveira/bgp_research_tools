from dotenv import dotenv_values
import json
import os
import utils
from datetime import datetime
from math import floor, ceil
import json
import sys
import logging
import multiprocessing
from netscience_client import NetScienceClient
from dataset.dataset import Dataset
from feature_selection.feature_selection import ExtraTreesFeatureSelection
from exploratory_data_analysis.cli import execute_eda_single_task
import sweetviz as sv

#Configuração de LOGGING
logging.basicConfig(
    filename=f"bgpresearch.log",
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

app_path = f"{os.path.dirname(__file__)}"

# LOADING ENV FILE
netscience_path = f"{app_path}/../netscience.env"
if not os.path.exists(netscience_path):
    msg=f"ABORTING: were not found the netscience environment file at: {netscience_path}"
    logging.error(msg)
    sys.exit(msg)

uname = os.uname()
print(f" 🖥️ Node Hostname: {uname.nodename}")
print(f"    Sysname: {uname.sysname}")
print(f"    Release: {uname.release}")
print(f"    Version: {uname.version}")
print(f"    Arch: {uname.machine}")

number_of_cores = multiprocessing.cpu_count()
print(f" 🧠 Detected number of CPU cores: {number_of_cores}")

netscience_config = dotenv_values(netscience_path)
print(f" 💼 Netscience User: {netscience_config['USERNAME']}")

task_working_dir = os.getcwd()
print(f" 📂 Starting experiment task on CWD: {task_working_dir}")

today = datetime.today()
print(f" 🕣 Starting time: {today}")

file = open('task.json')
task = json.load(file)

print(f" 🔑 Task key: {task['id']}")

print(f" 🧪 Getting experiment details...")
client = NetScienceClient(netscience_config['BASE_URL'], netscience_config['USERNAME'], netscience_config['PASSWORD'],netscience_config['TASKS_BASE_PATH'], logging=logging)
task = client.get_experiment(task['id'])

p = task['parameters']
p['dataset_id'] = task['dataset_id']
dataset_task_path = os.path.join(netscience_config['TASKS_BASE_PATH'], task['dataset_id'])
p['dataset_path'] = os.path.join(dataset_task_path, 'DATASET.csv')

print(f" ⚙️ Task parameters (before parsing):")
utils.print_task_parameters(task)

# Preparing the parameters
dataset_id = p['dataset_id']
dataset_path = p['dataset_path']

data_partition_training = p['data_partition_training'] / 100

rnn_length = p['rnn_length']

debug = True if p['debug'] == 'activated' else False

params = {
    'dataset_id': dataset_id,
    'dataset_path': dataset_path,
    'data_partition_training': data_partition_training,
    'rnn_length': rnn_length,
    'debug': debug,
}

print('')

print(f" ⚙️ Task parameters (after parsing):")
utils.print_generic_parameters(params)

print('')

print(f" 🍕 Data partition:")

print(f"  → Train size (proportion): {data_partition_training}")
print()

#Dataset object
dataset = Dataset(dataset_path)
#Dataset DataFrame
df = dataset.df

print(f" ⛔️ Looking for NaN values")
nan_rows = df[df.isna().any(axis=1)]
if (len(nan_rows)> 0):
    print(f"  → {nan_rows} NaN values were found.")
else: print(f"  → No NaN value were found.")
print()

print(f" 📊 Stats of the original dataset")
print(f"  → Regular: {len(df.loc[df['LABEL'] == 0])}")
print(f"  → Anomalous: {len(df.loc[df['LABEL'] == 1])}")
print(f"  → Total: {len(df)}")
print(f"  → NaN lines: {len(nan_rows)}")
df = df.dropna()
print(f"  → Total after remove NaN lines: {len(df)}")
print()

df.info(verbose=True, show_counts=True)
print()

#Train Dataset
tr_dataset = dataset.get_training_sample(data_partition_training)

print(f" 📊 Stats of the TRAINING sample:")
print(f"  → Regular: {tr_dataset.count_regular_data_points()}")
print(f"  → Anomalous: {tr_dataset.count_anomalous_data_points()}")
print(f"  → Total: {tr_dataset.count_total_data_points()}")
print()

tr_dataset.df.info(verbose=True, show_counts=True)
print()

#Testing Dataset
ts_dataset = dataset.get_testing_sample(data_partition_training)
print(f" 📊 Stats of the TESTING sample:")
print(f"  → Regular: {ts_dataset.count_regular_data_points()}")
print(f"  → Anomalous: {ts_dataset.count_anomalous_data_points()}")
print(f"  → Total: {ts_dataset.count_total_data_points()}")
print()

ts_dataset.df.info(verbose=True, show_counts=True)
print()

print(f" 📉 Executing automatic exploratory data analysis")

html_path = os.path.join(task_working_dir, 'eda.html')
report = sv.compare([tr_dataset.df, "Trainning"],[ts_dataset.df, "Test"], target_feat=dataset.target_column)
try:
    report.show_html(html_path, open_browser=False, layout='vertical')
except Exception as e:
    print(f"Failure during writing html EDA file. {html_path}")

