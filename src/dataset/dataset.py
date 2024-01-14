import pandas as pd
import os
from sklearn.model_selection import train_test_split

class Dataset:

    def __init__(self,dataset, target_column='LABEL'):

        self.target_column = target_column

        if isinstance(dataset, str):
            self.file_path_input = dataset
            self.df = self.openDatasetFromFile(dataset)
        elif isinstance(dataset, pd.DataFrame):
            self.df = dataset

        # Check Dataset
        self.checkDataset(self.df)
        # Remove undesired columns
        self.df = self.removeUndesiredColumns(self.df)

    def openDatasetFromFile(self, dataset_path):
        
        if not os.path.isfile(dataset_path):
            raise Exception(f"Aborting: The task path provided must to have a {dataset_path} file.")            
        
        df = pd.read_csv(dataset_path)

        return df
    
    def checkDataset(self, df):

        if not self.target_column in df.columns:
            raise Exception(f"Aborting: The dataset needs to have a {self.target_column} column (target column)")
        
    def removeUndesiredColumns(self, df):
        return df.drop(['HOUR', 'MINUTE', 'SECOND', 'TRAIN'], axis=1, errors='ignore')
    
    # Returns a DataFrame with the Dataset plus a TRAIN column
    # The TRAIN colum is filled according with train_size
    def get_df_with_partition_column(self,train_size):
        # In this kind of dataset, a Time Series
        # is not allowed to change the order of the records
        # Therefore the data is partitioned placing the
        # first TRAIN_SIZE records to training_dataset
        # and the rest for testing dataset 

        if not (train_size >=0 and train_size <=1):
            raise Exception(f"Train size must be >= 0 and <= 1")
        
        df_lines = len(self.df.index)
        train_lines = round(df_lines * train_size)
        test_lines = df_lines - train_lines

        if not (train_lines + test_lines == df_lines):
            raise Exception(f"The sum between number of training lines and testing lines should be equal to total number of lines")

        # # Creating a new and independent copy of the dataset
        # df = self.df.copy(deep=True)

        df = self.df
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
        df = self.get_df_with_partition_column(train_size)
        df = df.dropna()
        df = df.loc[df['TRAIN'] == 1]
        df = self.removeUndesiredColumns(df)
        return Dataset(df)
    
    def get_testing_sample(self, train_size):
        df = self.get_df_with_partition_column(train_size)
        df = df.dropna()
        df = df.loc[df['TRAIN'] == 0]
        df = self.removeUndesiredColumns(df)
        return Dataset(df)
    
    def count_regular_data_points(self, regular_value=0):
        return len(self.df.loc[self.df[self.target_column] == regular_value])
    
    def count_anomalous_data_points(self, anomalous_value=1):
        return len(self.df.loc[self.df[self.target_column] == anomalous_value])
    
    def count_total_data_points(self):
        return len(self.df)
    
    # This method was designed for ordered datasets, usually time series dataset
    # which all anomalous data points are located in a single contiguous cluster
    def get_effective_percentage_from_anomalous_percentage(self, anomalous_percentage, anomalous_value=1):
        
        # Total amount of data points
        size_total_sample = self.count_total_data_points()
        
        # Index of the first anomalous data point (getting target column from the class attribute)
        first_anomalous_index = self.df[self.df[self.target_column] == anomalous_value].first_valid_index()
        
        # Index of the last anomalous data point (getting target column from the class attribute)
        # last_anomalous_index = self.df[self.df[self.target_column] == anomalous_value].last_valid_index()
        
        # Amount of anomalous data points
        size_anomalous_sample = len(self.df[self.df[self.target_column] == anomalous_value])

        # Index of separation data point (data point that will split the partitions)
        separation_data_point = round(first_anomalous_index + (size_anomalous_sample * anomalous_percentage))
        
        effective_percentage = separation_data_point / size_total_sample
        return effective_percentage
    
    def get_x_y(self):
        # Separating the dependent and independent variables
        # The use of x and y variables are a convention in ML codes
        y = self.df[self.target_column]
        x = self.df.drop(self.target_column, axis = 1)
        return x, y
    
    def save_to_file(self, path = './DATASET.CSV'):
        self.df.to_csv(path)
    



    
    

        
        
        
