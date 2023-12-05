import argparse

from exploratory_data_analysis.cli import execute_eda_single_task, execute_eda_multiple_tasks
from feature_selection.cli import execute_feature_selection_single_task

parser = argparse.ArgumentParser('CLI for the BGP Research Software')

parser.add_argument('command', choices=['eda', 'feature_selection'], help='Available commands in this CLI.')

parser.add_argument('--task', dest='task_path', type=str, help='Execute automated EDA to a specific task absolute path')
parser.add_argument('--tasks', dest='tasks_path', type=str, help='Execute automated EDA to all tasks folders inside a specific absolute path')

parser.add_argument('--train-size', dest='train_size', type=float, help='Train size between 0 and 1')

args = parser.parse_args()

#Processing Exploratory Data Analysis (EDA) command
if (args.command == 'eda'):

    if (args.task_path):
        execute_eda_single_task(args.task_path)

    if (args.tasks_path):
        execute_eda_multiple_tasks(args.tasks_path)


if (args.command == 'feature_selection'):

    train_size = args.train_size

    if (args.task_path):
        execute_feature_selection_single_task(args.task_path, train_size)

    # if (args.tasks_path):
    #     execute_eda_multiple_tasks(args.tasks_path)