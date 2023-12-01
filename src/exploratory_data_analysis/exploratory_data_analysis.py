import argparse
import os
import pandas as pd
import sweetviz as sv
# sv.config_parser.read("./sv.ini")
sv.config_parser.read_string("[Layout] \nshow_logo = 0")


DATASET_FILENAME = 'DATASET.csv'
HTML_FILENAME = 'eda.html'

def execute_eda_single_task(task_path):
    if not os.path.isdir(task_path):
        print(f"Aborting: You have to pass a valid task folder absolute path.")
        return False

    dataset_path = os.path.join(task_path, DATASET_FILENAME)
    if not os.path.isfile(dataset_path):
        print(f"Aborting: The task path provided must to have a {DATASET_FILENAME} file.")
        return False
    
    df = pd.read_csv(dataset_path)
    df.drop(['HOUR', 'MINUTE', 'SECOND'], axis=1, inplace=True)
    html_path = os.path.join(task_path, HTML_FILENAME)
    report = sv.analyze([df, "Dataset"],target_feat='LABEL')
    try:
        report.show_html(html_path, open_browser=False, layout='vertical')
        # if os.path.isfile(html_path):
        #     print(f"EDA html file generated. {html_path}")
    except Exception as e:
        print(f"Failure during writing html EDA file. {html_path}")


def execute_eda_multiple_tasks(tasks_path):
    if not os.path.isdir(tasks_path):
        print(f"Aborting: You have to pass a valid task folder absolute path.")
        return False
    
    for root, dirs, files in os.walk(tasks_path):
        for d in dirs:
            task_path = os.path.join(root, d)
            print(f"Executing EDA report generation for {task_path}")
            execute_eda_single_task(task_path)

    


parser = argparse.ArgumentParser()
parser.add_argument('--task', dest='task_path', type=str, help='Execute automated EDA to a specific task absolute path')
parser.add_argument('--tasks', dest='tasks_path', type=str, help='Execute automated EDA to all tasks folders inside a specific absolute path')
args = parser.parse_args()

if (args.task_path):
    execute_eda_single_task(args.task_path)

if (args.tasks_path):
    execute_eda_multiple_tasks(args.tasks_path)


