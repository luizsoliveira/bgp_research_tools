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

class RIPEClient:
    def __init__(self,
                 cacheLocation=False,
                 baseURL='https://data.ris.ripe.net',
                 logging=False):
        
        self.baseURL = baseURL
        self.logging = logging

        # Mapping possible cache location passed
        if (cacheLocation):
            self.workdir = cacheLocation
        else:
            self.workdir = tempfile.gettempdir() + "/ripe"

        # Creating the directory if not exists
        if not os.path.exists(self.workdir):
            self.log_info("Creating the directory: " + self.workdir)
            os.makedirs(self.workdir)

    def log_info(self, msg):
        if self.logging:
            return self.logging.info(msg)
        else: print(msg)
    
    def log_error(self, msg):
        if self.logging:
            return self.logging.error(msg)
        else: print(msg)
        
    def log_warning(self, msg):
        if self.logging:
            return self.logging.warning(msg)
        
    def check_interval(self,number, min, max):
        return min <= number <= max
    
    def validate_year(self, year):
        if not year >= 2021:
            raise Exception('Year {year} must be greater than 2021'.format(year=year))
        return True

    def validate_month(self, month):
        if not self.check_interval(month, 1, 12):
            raise Exception('Month {month} must be within the range between 1 and 12'.format(month=month))
        return True
    
    def validate_day(self, day):
        if not self.check_interval(day, 1, 31):
            raise Exception('Day {day} must be within the range between 1 and 31'.format(day=day))
        return True
    
    def validate_hour(self, hour):
        if not self.check_interval(hour, 0, 23):
            raise Exception('Hour {hour} must be within the range between 0 and 23'.format(hour=hour))
        return True
    
    def validate_minute(self, minute):
        if not self.check_interval(minute, 0, 59):
            raise Exception('Minute {minute} must be within the range between 0 and 59'.format(minute=minute))
        return True
    
    def validate_ripe_minute(self, minute):
        if not minute in range(0, 60, 5):
            raise Exception('Minute {minute} must be within the range between 0 and 59 and be multiple of 5'.format(minute=minute))
        return True
    
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

        return "{workdir}/rrc{rrc}/{year}.{month}/updates.{year}{month}{day}.{hour}{minute}.gz".format(
            workdir=self.workdir,
            year=year,
            month="{:02d}".format(month),
            day="{:02d}".format(day),
            hour="{:02d}".format(hour),
            minute="{:02d}".format(minute),
            rrc="{:02d}".format(rrc)
        )
        
        
    def download_update_file(self, year, month, day, hour, minute, rrc=4):

        # Checking time parameters
        validate = (
                self.validate_year(year)
                and self.validate_month(month)
                and self.validate_day(day)
                and self.validate_hour(hour)
                and self.validate_ripe_minute(minute))
        
        if not validate: return False
        
        # Setting the local attributes
        filePath = self.generate_update_local_path(year, month, day, hour, minute, rrc)
        head, tail = os.path.split(filePath)
        self.create_path_if_not_exists(head)

        # Setting the URL
        url = self.generate_update_url(year, month, day, hour, minute, rrc)

        # Checking if the file was already downloaded before
        if not os.path.exists(filePath):
        
            # Downloading the file
            self.log_info('Downloading RIPE file: ' + url)
            try:
                res = requests.get(url, allow_redirects=True)
                # Saving the file
                try:
                    open(filePath, 'wb').write(res.content)
                    self.log_info('File saved in: ' + url)
                    if os.path.exists(filePath):
                        return filePath
                    else:
                        raise Exception('Downloaded file not found in: ' + url)
                except:
                    raise Exception('Failure when downloading the file: ' + url)
            except:
                raise Exception('Failure when downloading the file: ' + url)
            
        else:
            self.log_info('Download prevented because the file was found in cache: ' + url)
            return filePath
        
    def download_updates_interval_files(self, year_start, month_start, day_start, hour_start, minute_start, year_end, month_end, day_end, hour_end, minute_end, rrc=4):

        # Checking time parameters (range)
        validate = (
                self.validate_year(year_start)
                and self.validate_month(month_start)
                and self.validate_day(day_start)
                and self.validate_hour(hour_start)
                and self.validate_minute(minute_start)
                and self.validate_year(year_end)
                and self.validate_month(month_end)
                and self.validate_day(day_end)
                and self.validate_hour(hour_end)
                and self.validate_minute(minute_end)
                )
        
        if not validate: return False 

        # Checking datetime
        datetime_start = datetime(year_start, month_start, day_start, hour_start, minute_start)
        datetime_end = datetime(year_end, month_end, day_end, hour_end, minute_end)

        #Rounding datetime_start to the next minute multiple of 5, just if it is not multiple of 5
        min =datetime_start.minute if datetime_start.minute % 5 == 0 else ((datetime_start.minute // 5) + 5)
        adjusted_datetime_start = datetime_start.replace(second=0, microsecond=0, minute=0)+timedelta(minutes=min)

        #Rounding datetime_end to the before minute multiple of 5, , just if it is not multiple of 5
        min = datetime_end.minute if datetime_end.minute % 5 == 0 else ((datetime_end.minute // 5) * 5)
        adjusted_datetime_end = datetime_end.replace(second=0, microsecond=0, minute=0)+timedelta(minutes=min)

        self.log_info('Start at: ' + str(datetime_start) + ' Adjusted for: ' + str(adjusted_datetime_start))
        self.log_info('End at: ' + str(datetime_end) + ' Adjusted for: ' + str(adjusted_datetime_end))

        #Generating datetimes
        ts = adjusted_datetime_start
        while adjusted_datetime_start <= ts <= adjusted_datetime_end:
            try:
                self.download_update_file(ts.year, ts.month, ts.day, ts.hour, ts.minute)
            except Exception as err:
                self.log_error(f"Unexpected error during the download {err=}, {type(err)=}")

            ts += timedelta(minutes=5)
        
