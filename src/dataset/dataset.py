import pandas as pd
import os
from sklearn.model_selection import train_test_split

class Dataset:

    def __init__(self,dataset, target_column='LABEL'):

        self.target_column = target_column

        if isinstance(dataset, str):
            self.dataset = self.openDatasetFromFile(dataset)
        elif isinstance(dataset, pd.DataFrame()):
            self.dataset = dataset

        # Check Dataset
        self.checkDataset(self.dataset)
        # Remove undesired columns
        self.dataset = self.removeUndesiredColumns(self.dataset)

    def openDatasetFromFile(self, dataset_path):
        
        if not os.path.isfile(dataset_path):
            raise Exception(f"Aborting: The task path provided must to have a {DATASET_FILENAME} file.")            
        
        df = pd.read_csv(dataset_path)

        return df
    
    def checkDataset(self, df):

        if not self.target_column in df.columns:
            raise Exception(f"Aborting: The dataset needs to have a {self.target_column} column (target column)")
        
    def removeUndesiredColumns(self, df):
        return df.drop(['HOUR', 'MINUTE', 'SECOND', 'TRAIN'], axis=1, errors='ignore')
    
    # Returns a DataFrame with the Dataset plus a TRAIN column
    # The TRAIN colum is filled according with train_size
    def dataset_with_partition_column(self,train_size):
        # In this kind of dataset, a Time Series
        # is not allowed to change the order of the records
        # Therefore the data is partitioned placing the
        # first TRAIN_SIZE records to training_dataset
        # and the rest for testing dataset 

        if not (train_size >=0 and train_size <=1):
            raise Exception(f"Train size must be >= 0 and <= 1")
        
        df_lines = len(self.dataset.index)
        train_lines = round(df_lines * train_size)
        test_lines = df_lines - train_lines

        if not (train_lines + test_lines == df_lines):
            raise Exception(f"The sum between number of training lines and testing lines should be equal to total number of lines")

        # # Creating a new and independent copy of the dataset
        # df = self.dataset.copy(deep=True)

        df = self.dataset
        # Creating a new column and setting train = 0 for all values
        df['TRAIN'] = 0
        # Setting train = 1 for the first train_lines
        df.iloc[:train_lines, df.columns.get_loc('TRAIN')] = 1
        # is a training line => TRAIN = 1
        # is a testing line => TRAIN = 0

        #Checking the amount of training and testing lines
        train_lines_found = len(df.loc[df['TRAIN'] == 1])
        test_lines_found = len(df.loc[df['TRAIN'] == 0])

        if not (train_lines_found == train_lines and test_lines_found == test_lines):
            raise Exception(f"The amount of lines for training and testing dit not matched as was planned. Check the code.")

        return df
    
    def get_training_sample(self, train_size):
        df = self.dataset_with_partition_column(train_size)
        df = df.dropna()
        df = df.loc[df['TRAIN'] == 1]
        return self.removeUndesiredColumns(df)
    
    def get_testing_sample(self, train_size):
        df = self.dataset_with_partition_column(train_size)
        df = df.dropna()
        df = df.loc[df['TRAIN'] == 0]
        return self.removeUndesiredColumns(df)
    
    

        
        
        
