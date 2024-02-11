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

DATASET_FILENAME = 'DATASET.csv'
DATASET_FILENAME_WITHOUT_NORMALIZATION = 'DATASET-without-normalization.csv'
IMPORTANCES_FILENAME = 'fs_importances.json'

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

print(f" 🧪 Getting experiment details (TaskId = {task['id']})")
client = NetScienceClient(netscience_config['BASE_URL'], netscience_config['USERNAME'], netscience_config['PASSWORD'],netscience_config['TASKS_BASE_PATH'], logging=logging)

task = client.get_experiment(task['id'])
p = task['parameters']
p['dataset_id'] = task['dataset_id']
dataset_task_path = os.path.join(netscience_config['TASKS_BASE_PATH'], task['dataset_id'])
p['dataset_path'] = os.path.join(dataset_task_path, DATASET_FILENAME)

print(f" ⚙️ Task parameters (before parsing):")
utils.print_task_parameters(task)

# Preparing the parameters
dataset_id = p['dataset_id']
dataset_path = p['dataset_path']

data_partition_training = p['data_partition_training'] / 100
data_partition_reference = p['data_partition_reference']

rnn_length = p['rnn_length']

debug = True if p['debug'] == 'activated' else False

params = {
    'dataset_id': dataset_id,
    'dataset_path': dataset_path,
    'data_partition_training': data_partition_training,
    'data_partition_reference': data_partition_reference,
    'rnn_length': rnn_length,
    'debug': debug,
}

print('')

print(f" ⚙️ Task parameters (after parsing):")
utils.print_generic_parameters(params)

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

# df.info(verbose=True, show_counts=True)
print()

#Using dataset with NaN values dropped
dataset = Dataset(df)

print(f" 🍕 Data partition:")

effective_data_train_percentage = data_partition_training

if (data_partition_reference == 'anomalous'):
    print(f"  * Data partition referenced only on anomalous samples was detected.")
    print(f"  * This approach is a indirect way to do data partitioning.")
    
    effective_data_train_percentage = dataset.get_effective_percentage_from_anomalous_percentage(data_partition_training)
    print(f"  * In order to have {data_partition_training*100}% of anomalous data points in the training partition")
    print(f"    will applied a effective data train of {effective_data_train_percentage}%")          

print()

print(f"  → Requested Train size (proportion): {data_partition_training}")
print(f"  ⛔️ Effective Train size (proportion): {effective_data_train_percentage}")
print(f"  ⛔️ Effective Testing size (proportion): {1-effective_data_train_percentage}")
print()

#New Dataset with partition column
new_df = dataset.get_df_with_partition_column(effective_data_train_percentage)
print(f" 📊 Stats of the dataset with partition column")
print(f"  → Training: {len(new_df.loc[new_df['TRAIN'] == 1])}")
print(f"  → Testing: {len(new_df.loc[new_df['TRAIN'] == 0])}")
print(f"  → Training - Regular: {len(new_df.loc[ (new_df['TRAIN'] == 1) & (new_df['LABEL'] == 0)])}")
print(f"  → Training - Anomalous: {len(new_df.loc[(new_df['TRAIN'] == 1) & (new_df['LABEL'] == 1)])}")
print(f"  → Testing - Regular: {len(new_df.loc[(new_df['TRAIN'] == 0) & (new_df['LABEL'] == 0)])}")
print(f"  → Testing - Anomalous: {len(new_df.loc[(new_df['TRAIN'] == 0) & (new_df['LABEL'] == 1)])}")
print(f"  → Total: {len(new_df)}")
print()

# new_df.info(verbose=True, show_counts=True)
 print(f" 💾 Saving dataset")
 new_df.to_csv(DATASET_FILENAME_WITHOUT_NORMALIZATION)

print(f" 💾 Saving Zscore normalized dataset")
normalized_dataset = Dataset(new_df).get_normalized_zscore_dataset()
normalized_dataset.df.to_csv(DATASET_FILENAME)

print()

#Train Dataset
tr_dataset = dataset.get_training_sample(effective_data_train_percentage)

print(f" 📊 Stats of the TRAINING sample:")
print(f"  → Regular: {tr_dataset.count_regular_data_points()}")
print(f"  → Anomalous: {tr_dataset.count_anomalous_data_points()}")
print(f"  → Total: {tr_dataset.count_total_data_points()}")
print()

# tr_dataset.df.info(verbose=True, show_counts=True)
print()

#Testing Dataset
ts_dataset = dataset.get_testing_sample(effective_data_train_percentage)
print(f" 📊 Stats of the TESTING sample:")
print(f"  → Regular: {ts_dataset.count_regular_data_points()}")
print(f"  → Anomalous: {ts_dataset.count_anomalous_data_points()}")
print(f"  → Total: {ts_dataset.count_total_data_points()}")
print()

# ts_dataset.df.info(verbose=True, show_counts=True)
print()

print(f" 📉 Executing automatic exploratory data analysis")
html_path = os.path.join(task_working_dir, 'eda.html')
report = sv.compare([tr_dataset.df, "Trainning"],[ts_dataset.df, "Test"], target_feat=dataset.target_column)
try:
    report.show_html(html_path, open_browser=False, layout='vertical')
except Exception as e:
    print(f"Failure during writing html EDA file. {html_path}")

print(f" 📉 Executing Feature Selection")

fs = ExtraTreesFeatureSelection(tr_dataset)

# Importances Dataframe
idf = fs.getImportancesDataFrame()
print(f"###############################")
print(f"* Features in order of importance:")
print(idf)
print()
fs_importances_path = os.path.join(task_working_dir, IMPORTANCES_FILENAME)
try:
    with open(fs_importances_path, 'w') as file:
        json_obj = json.loads(idf.to_json())
        file.write(json.dumps(json_obj['importance']))
    print(f"File with features importances saved at: {fs_importances_path}")
except Exception as e:
    print(f"Failure when saving features importances file at: {fs_importances_path}.")

top_n_features = 10

print(f"###############################")
print(f"* Selected (N={top_n_features}) features:")
print(fs.getSelectedFeatures(top_n_features))

