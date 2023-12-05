import os
import pandas as pd
from dataset.dataset import Dataset
from feature_selection.feature_selection import ExtraTreesFeatureSelection

DATASET_FILENAME = 'DATASET.csv'

def execute_feature_selection_single_task(task_path, train_size):
    if not os.path.isdir(task_path):
        raise Exception(f"Aborting: You have to pass a valid task folder absolute path.")        
    
    dataset_path = os.path.join(task_path, DATASET_FILENAME)
    if not os.path.isfile(dataset_path):
        raise Exception(f"Aborting: The task path provided must to have a {DATASET_FILENAME} file.")

    print(f"###############################")
    print(f"* Train size (proportion): {train_size}")
    print()

    #Dataset object
    dataset = Dataset(dataset_path)
    #Dataset DataFrame
    df = dataset.dataset

    print(f"###############################")
    print(f"Looking for NaN values")
    nan_rows = df[df.isna().any(axis=1)]
    print(nan_rows)

    print(f"###############################")
    print(f"* Stats of the original dataset")
    print(f"    Regular: {len(df.loc[df['LABEL'] == 0])}")
    print(f"    Anomalous: {len(df.loc[df['LABEL'] == 1])}")
    print(f"    Total: {len(df)}")
    print(f"    NaN lines: {len(nan_rows)}")
    df = df.dropna()
    print(f"    Total after remove NaN lines: {len(df)}")
    print()

    #Train DataFrame
    trdf = dataset.get_training_sample(train_size)
    print(f"###############################")
    print(f"* Stats of the TRAINING sample:")
    print(f"    Regular: {len(trdf.loc[trdf['LABEL'] == 0])}")
    print(f"    Anomalous: {len(trdf.loc[trdf['LABEL'] == 1])}")
    print(f"    Total: {len(trdf)}")
    print()

    #Testing DataFrame
    tsdf = dataset.get_testing_sample(train_size)
    print(f"###############################")
    print(f"* Stats of the TESTING sample:")
    print(f"    Regular: {len(tsdf.loc[tsdf['LABEL'] == 0])}")
    print(f"    Anomalous: {len(tsdf.loc[df['LABEL'] == 1])}")
    print(f"    Total: {len(tsdf)}")
    print()

    fs = ExtraTreesFeatureSelection(trdf)

    print(f"###############################")
    print(f"* Features in order of importance:")
    print(fs.getImportancesDataFrame())
    print()

    fs.getSelectedFeatures()

    
