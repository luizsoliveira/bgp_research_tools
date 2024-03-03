import requests
import json
import pandas as pd
from sklearn.preprocessing import MaxAbsScaler
import numpy as np

class IODASignal:
    def __init__(self, signal):

        self.entity_type = signal['entityType']
        self.entity_code = signal['entityCode']
        self.entity_name = signal['entityName']
        self.datasource = signal['datasource']

        self.from_timestamp = signal['from']
        self.until_timestamp = signal['until']
        self.step = signal['step']
        self.native_step = signal['nativeStep']

        self.values = self.interpolate_values(signal['values'])

    def interpolate_values(self, values):
        now = self.from_timestamp
        data = []
        for value in values:
            data.append({"timestamp": now, "value": value})
            now += self.step

        if now != self.until_timestamp:
            raise Exception(f"A value interpolation was finished with the last timestamp ({now}) different from until timestamp ({self.until}).")

        return data



# https://api.ioda.inetintel.cc.gatech.edu/v2/signals/raw/region/1226?from=1696118400&until=1706054400
class IODAClient:

    TYPE = 'ioda'
    VALID_ENTITY_TYPES = ['continent', 'country', 'region', 'country', 'asn']
        
    def __init__(self,
                 base_url='https://api.ioda.inetintel.cc.gatech.edu',
                 logging=False,
                 debug=False,
                 max_concurrent_requests=1
                 ):
        
        self.base_url = base_url
        self.logging = logging
        self.debug = debug
        self.max_concurrent_requests = int(max_concurrent_requests)

        #Checking if logging has a valid value
        if not (self.logging==False or (hasattr(self.logging, 'basicConfig') and hasattr(self.logging.basicConfig, '__call__'))):
            raise Exception('The logging parameters need to be a valid logging object or False')
        

    def log_info(self, msg):
        if self.logging: self.logging.info(msg)
        if self.debug: print(msg)
        return msg
    
    def log_error(self, msg):
        if self.logging: self.logging.error(msg)
        if self.debug: print(msg)
        return msg
        
    def log_warning(self, msg):
        if self.logging: self.logging.warning(msg)
        if self.debug: print(msg)
        return msg

    def log_debug(self, msg):
        if self.logging: self.logging.debug(msg)
        if self.debug: print(msg)
        return msg

    def get_url(self, url):
        try:
            res = requests.get(url, allow_redirects=True)
            res.raise_for_status()
            return res.content
        except requests.exceptions.HTTPError as errh:
            self.log_error(f"HTTP Error: {errh} when getting the URL={url}")
        except requests.exceptions.ConnectionError as errc:
            self.log_error(f"Connecting Error: {errc} when getting the URL={url}")
        except requests.exceptions.Timeout as errt:
            self.log_error(f"Timeout Error: {errt} when getting the URL={url}")
        except requests.exceptions.RequestException as err:
            self.log_error(f"Something Else Error: {err} when getting the URL={url}")

    # Retrieve method is responsible just to do HTTP request
    def retrieve_signals(self, entity_type, code, from_timestamp, until_timestamp):

        if entity_type not in self.VALID_ENTITY_TYPES:
            raise Exception(self.log_error(f"Invalid entity type provided. Allowed entity type are {', '.join(self.VALID_ENTITY_TYPES)}"))

        url = f"{self.base_url}/v2/signals/raw/{entity_type}/{code}?from={from_timestamp}&until={until_timestamp}"
        
        response = self.get_url(url)
        
        return json.loads(response)

    def get_signals(self, entity_type, code, from_timestamp, until_timestamp):

        response = self.retrieve_signals(entity_type, code, from_timestamp, until_timestamp)
        signals = response['data'][0]
        signals_objects = []

        for signal in signals:
            signal_object = IODASignal(signal)
            signals_objects.append(signal_object)

        return signals_objects

    def get_signals_dataframe(self, entity_type, code, from_timestamp, until_timestamp, add_datetime_column=True):
        signals = self.get_signals(entity_type, code, from_timestamp, until_timestamp)

        df = pd.DataFrame()

        for signal in signals:
            datasource = signal.datasource
            signal_df = pd.DataFrame(signal.values, columns=["timestamp","value"])
            signal_df.set_index('timestamp', inplace=True)
            signal_df.columns = [f"{datasource}"]
            df = df.join(signal_df, how='outer')

        df['ping-slash24'] = df['ping-slash24'].fillna(method='bfill')
        # df.dropna(how='any', inplace=True)
        
        if add_datetime_column:
            df['datetime'] = pd.to_datetime(list(df.index.values), unit='s', utc=True)
        return df

    def get_signals_normalized_dataframe(self, entity_type, code, from_timestamp, until_timestamp, add_datetime_column=True):
        df = self.get_signals_dataframe(entity_type, code, from_timestamp, until_timestamp, add_datetime_column=False)
        #Normalizing
        # df=(df-df.min())/(df.max()-df.min())
        features_cols = list(df.select_dtypes(include=[np.number]).columns)
        for column in features_cols:
            print(f"Applying max scaled normalization at column {column}")
            df[column] =  df[column] / df[column].abs().max() 
        if add_datetime_column:
            df['datetime'] = pd.to_datetime(list(df.index.values), unit='s', utc=True)
        return df







    