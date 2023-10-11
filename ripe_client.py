# https://data.ris.ripe.net/rrcXX/YYYY.MM/TYPE.YYYYMMDD.HHmm.gz

# with:

# XX = the RRC number
# YYYY = year
# MM = month
# TYPE = the type of file, which is either bview (dumps) or update (updates)
# DD = day
# HH = hour
# mm = minute
# Currently dumps are created every 8 hours, and updates are created every 5 minutes
#


import tempfile
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse

class RIPEClient:
    def __init__(self,
                 cacheLocation=False,
                 baseURL='https://data.ris.ripe.net',
                 logging=False,
                 debug=False
                 ):
        
        self.baseURL = baseURL
        self.logging = logging
        self.debug = debug

        #Checking if logging has a valid value
        if not (self.logging==False or (hasattr(self.logging, 'basicConfig') and hasattr(self.logging.basicConfig, '__call__'))):
            raise Exception('The logging parameters need to be a valid logging object or False')

        # Mapping possible cache location passed
        if (cacheLocation):
            self.work_dir = cacheLocation
        else:
            with tempfile.TemporaryDirectory() as tmp_dirname:
                self.log_info(f"created temporary directory: {tmp_dirname}")
                self.work_dir = tmp_dirname + "/ripe"
            

        # Creating the directory if not exists
        if not os.path.exists(self.work_dir):
            self.log_info("Creating the directory: " + self.work_dir)
            os.makedirs(self.work_dir)

    def log_info(self, msg):
        if self.logging:
            return self.logging.info(msg)
        elif self.debug: print(msg)
    
    def log_error(self, msg):
        if self.logging:
            return self.logging.error(msg)
        elif self.debug: print(msg)
        
    def log_warning(self, msg):
        if self.logging:
            return self.logging.warning(msg)
        elif self.debug: print(msg)

    def log_debug(self, msg):
        if self.logging:
            return self.logging.debug(msg)
        elif self.debug: print(msg)
        
    def check_interval(self,number, min, max):
        return min <= number <= max
    
    def validate_year(self, year):
        if not year >= 2021:
            raise Exception('Year {year} must be greater than 2021'.format(year=year))
        return True

    def validate_ripe_minute(self, minute):
        if not minute in range(0, 60, 5):
            raise Exception('Minute {minute} must be within the range between 0 and 59 and be multiple of 5'.format(minute=minute))
        return True
    
    def filename_from_url(self, url):
        parsed_url = urlparse(url)
        path = parsed_url.path
        return os.path.basename(path)

    def create_path_if_not_exists(self,path):
        try:
            if not os.path.exists(path):
                self.log_info('Creating dir: ' + path)
                path = Path(path)
                path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            self.log_error('Failure when creating the dir: ' + path)
            return False
            
        
    def generate_update_url(self, year, month, day, hour, minute, rrc=4):
        
        return "{baseURL}/rrc{rrc}/{year}.{month}/updates.{year}{month}{day}.{hour}{minute}.gz".format(
            baseURL=self.baseURL,
            year=year,
            month="{:02d}".format(month),
            day="{:02d}".format(day),
            hour="{:02d}".format(hour),
            minute="{:02d}".format(minute),
            rrc="{:02d}".format(rrc)
        )
    
    def generate_update_local_path(self, year, month, day, hour, minute, rrc=4):

        return "{work_dir}/rrc{rrc}/{year}.{month}/updates.{year}{month}{day}.{hour}{minute}.gz".format(
            work_dir=self.work_dir,
            year=year,
            month="{:02d}".format(month),
            day="{:02d}".format(day),
            hour="{:02d}".format(hour),
            minute="{:02d}".format(minute),
            rrc="{:02d}".format(rrc)
        )

    def download_update_file(self, ripe_datetime, rrc=4):

        if isinstance(ripe_datetime, datetime):
            year, month, day, hour, minute = [
            ripe_datetime.year,
            ripe_datetime.month,
            ripe_datetime.day,
            ripe_datetime.hour,
            ripe_datetime.minute,
            ]

            # Setting the local attributes
            filePath = self.generate_update_local_path(year, month, day, hour, minute, rrc)
            head, tail = os.path.split(filePath)
            self.create_path_if_not_exists(head)

            # Setting the URL
            url = self.generate_update_url(year, month, day, hour, minute, rrc)

            # CACHE: Checking if the file was already downloaded before
            if not os.path.exists(filePath):
            
                # Downloading the file
                self.log_info('Downloading RIPE file: ' + self.filename_from_url(url))
                try:
                    res = requests.get(url, allow_redirects=True)
                    # Saving the file
                    try:
                        open(filePath, 'wb').write(res.content)
                        #self.log_info('File saved in: ' + url)
                        if os.path.exists(filePath):
                            return filePath
                        else:
                            raise Exception('Downloaded file not found in: ' + url)
                    except:
                        raise Exception('Failure when downloading the file: ' + url)
                except:
                    raise Exception('Failure when downloading the file: ' + url)
                
            else:
                self.log_info('Download prevented because the file was found in cache: ' + self.filename_from_url(url))
                return filePath
        else:
            raise Exception('The parameter ripe_datetime need to be a datetime type.')
    
    def generate_datetimes_interval(self, ripe_datetime_start, ripe_datetime_end):
        if isinstance(ripe_datetime_start, datetime) and isinstance(ripe_datetime_end, datetime):
            timestamps = []
            
            #Rounding datetime_start to the next minute multiple of 5, just if it is not already a multiple of 5
            min =ripe_datetime_start.minute if ripe_datetime_start.minute % 5 == 0 else ((ripe_datetime_start.minute // 5) + 5)
            adjusted_datetime_start = ripe_datetime_start.replace(second=0, microsecond=0, minute=0)+timedelta(minutes=min)

            #Rounding datetime_end to the before minute multiple of 5, just if it is not already a multiple of 5
            min = ripe_datetime_end.minute if ripe_datetime_end.minute % 5 == 0 else ((ripe_datetime_end.minute // 5) * 5)
            adjusted_datetime_end = ripe_datetime_end.replace(second=0, microsecond=0, minute=0)+timedelta(minutes=min)

            #Generating datetimes
            ts = adjusted_datetime_start
            while adjusted_datetime_start <= ts <= adjusted_datetime_end:
                # The timestamps are returned as they are being generated using yield
                yield ts
                ts += timedelta(minutes=5)

        else:
            raise Exception('The parameter ripe_datetime_start and ripe_datetime_start need to be a datetime type.')    
            

    def download_updates_interval_files(self, ripe_datetime_start, ripe_datetime_end, rrc=4):
        if isinstance(ripe_datetime_start, datetime) and isinstance(ripe_datetime_end, datetime):
            
            #Getting timestamps
            timestamps = self.generate_datetimes_interval(ripe_datetime_start, ripe_datetime_end)

            # The timestamps are returned as they are being generated using yield
            for ts in timestamps:
                try:
                    yield self.download_update_file(ts)
                except Exception as err:
                    self.log_error(f"Unexpected error during the download {err=}, {type(err)=}")

        else:
            raise Exception('The parameter ripe_datetime_start and ripe_datetime_start need to be a datetime type.')    
        
