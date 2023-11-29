import os
import pandas as pd
import numpy as np

class AnomalousAndRegularDataLabeling:

    def __init__(self,
                 logging=False,
                 debug=False,
                 ):
        self.logging = logging
        self.debug = debug
        
        #Checking if logging has a valid value
        if not (self.logging==False or (hasattr(self.logging, 'basicConfig') and hasattr(self.logging.basicConfig, '__call__'))):
            raise Exception('The logging parameters need to be a valid logging object or False')
        
    def log_info(self, msg):
        if self.logging: self.logging.info(msg)
        if self.debug: print(msg)
    
    def log_error(self, msg):
        if self.logging: self.logging.error(msg)
        if self.debug: print(msg)
        
    def log_warning(self, msg):
        if self.logging: self.logging.warning(msg)
        if self.debug: print(msg)

    def log_debug(self, msg):
        if self.logging: self.logging.debug(msg)
        if self.debug: print(msg)

    def new_dataset_with_labels(self,dataset_path_in, dataset_path_out, anomalous_datetime_start, anomalous_datetime_end, regular_label=0, anomalous_label=1):

        if not os.path.exists(dataset_path_in):
            raise IOError(f"Dataset file not found in {dataset_path_in}.")
        
        df = pd.read_csv(dataset_path_in, delimiter=' ')

        df = self.put_labels(df, anomalous_datetime_start, anomalous_datetime_end, regular_label, anomalous_label)

        df.to_csv(dataset_path_out, sep=',', index=False, date_format='%Y-%m-%dT%H:%M:%S')

    def put_labels(self,df, anomalous_datetime_start, anomalous_datetime_end, regular_label=0, anomalous_label=1):

        # In case of CPlusPLus will use the column POSIXTIME
        # In case of CSharp will be use column DATETIME
        if 'POSIXTIME' in df.columns:
            df['DATETIME'] = pd.to_datetime(df['POSIXTIME'], unit='s')
        else: 
            df['DATETIME'] = pd.to_datetime(df['DATETIME'])

        # print(df.info())

        #Adding a new column to put the LABEL
        df = df.assign(LABEL=0)

        #Updating values conditionally
        df['LABEL'] = np.where(( (df['DATETIME'] >= anomalous_datetime_start) & (df['DATETIME'] <= anomalous_datetime_end) ), anomalous_label, regular_label)

        return df